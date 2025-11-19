

import numpy as np
from sklearn.cluster import DBSCAN
from db_setup import Database

db = Database()


def assign_person_ids():
    faces = _load_faces()
    if not faces:
        print("No faces in database.")
        return

    face_ids, embeddings = zip(*faces)
    embeddings_array = np.array(embeddings)

    labels = _cluster_embeddings(embeddings_array)
    unique_labels = np.unique(labels)

    people_avg_embeddings = _load_people_embeddings()
    label_to_person_id = _assign_clusters_to_people(
        embeddings_array, labels, unique_labels, people_avg_embeddings
    )

    _update_faces_with_person_ids(face_ids, labels, label_to_person_id)
    db.conn.commit()

    print(
        f"Assigned person_id to {len(face_ids)} faces and created {len(unique_labels)} people.")


def _load_faces():
    db.cursor.execute("SELECT id, embedding FROM faces")
    rows = db.cursor.fetchall()
    faces = []

    for row in rows:
        face_id = row['id']
        embedding_bytes = row['embedding']

        # pokud je memoryview, převedeme na bytes
        if isinstance(embedding_bytes, memoryview):
            embedding_bytes = embedding_bytes.tobytes()

        embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
        faces.append((face_id, embedding))

    return faces


def _cluster_embeddings(embeddings_array):
    clustering = DBSCAN(metric='cosine', eps=0.4,
                        min_samples=1).fit(embeddings_array)
    return clustering.labels_


def _load_people_embeddings():
    people_rows = db.get_people()
    people_avg_embeddings = {}
    for person_id, name, avg_bytes in people_rows:
        if avg_bytes is None:
            people_avg_embeddings[person_id] = None
            continue

        # pokud je memoryview, převedeme na bytes
        if isinstance(avg_bytes, memoryview):
            avg_bytes = avg_bytes.tobytes()
        elif isinstance(avg_bytes, str):
            # někdy DB vrátí string, převedeme na bytes
            avg_bytes = avg_bytes.encode('latin1')  # nebo 'utf-8', podle DB

        people_avg_embeddings[person_id] = np.frombuffer(
            avg_bytes, dtype=np.float32)

    return people_avg_embeddings


def _assign_clusters_to_people(embeddings_array, labels, unique_labels, people_avg_embeddings):
    label_to_person_id = {}
    next_person_index = len(people_avg_embeddings)

    for label in unique_labels:
        cluster_indices = [i for i, l in enumerate(labels) if l == label]
        cluster_embeddings = embeddings_array[cluster_indices]
        cluster_avg = np.mean(cluster_embeddings, axis=0)

        matched_person_id = _find_matching_person(
            cluster_avg, people_avg_embeddings)

        if matched_person_id is not None:
            person_id = matched_person_id
            all_embeddings = np.vstack(
                [cluster_embeddings,
                    people_avg_embeddings[person_id].reshape(1, -1)]
            )
            new_avg = np.mean(all_embeddings, axis=0)
            db.cursor.execute(
                "UPDATE people SET avg_embedding = %s WHERE id = %s",
                (new_avg.tobytes(), person_id)
            )
            people_avg_embeddings[person_id] = new_avg
        else:
            person_name = f"Person{next_person_index}"
            avg_bytes = cluster_avg.tobytes() if cluster_avg is not None else None
            # místo db.cursor.lastrowid použij insert_person, která vrací ID
            person_id = db.insert_person(
                name=person_name, avg_embedding=avg_bytes)
            people_avg_embeddings[person_id] = cluster_avg
            next_person_index += 1

        label_to_person_id[label] = person_id

    return label_to_person_id


def _find_matching_person(cluster_avg, people_avg_embeddings, threshold=0.5):
    for person_id, avg_emb in people_avg_embeddings.items():
        if avg_emb is not None:
            dist = np.linalg.norm(cluster_avg - avg_emb)
            if dist < threshold:
                return person_id
    return None


def _update_faces_with_person_ids(face_ids, labels, label_to_person_id):
    for face_id, label in zip(face_ids, labels):
        person_id = label_to_person_id[label]
        db.cursor.execute(
            "UPDATE faces SET person_id = %s WHERE id = %s",
            (person_id, face_id)
        )
