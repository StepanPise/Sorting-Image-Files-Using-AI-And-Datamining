

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
    rows = db.cursor.execute("SELECT id, embedding FROM faces").fetchall()
    faces = []
    for face_id, embedding_bytes in rows:
        embedding = np.frombuffer(embedding_bytes, dtype=np.float64)
        faces.append((face_id, embedding))
    return faces


def _cluster_embeddings(embeddings_array):
    clustering = DBSCAN(metric='euclidean', eps=0.5,
                        min_samples=1).fit(embeddings_array)
    return clustering.labels_


def _load_people_embeddings():
    people_rows = db.get_people()
    people_avg_embeddings = {}
    for person_id, name, avg_bytes in people_rows:
        people_avg_embeddings[person_id] = (
            np.frombuffer(avg_bytes, dtype=np.float64) if avg_bytes else None
        )
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
                "UPDATE people SET avg_embedding = ? WHERE id = ?",
                (new_avg.tobytes(), person_id)
            )
            people_avg_embeddings[person_id] = new_avg
        else:
            person_name = f"Person{next_person_index}"
            avg_bytes = cluster_avg.tobytes() if cluster_avg is not None else None
            db.insert_person(name=person_name, avg_embedding=avg_bytes)
            person_id = db.cursor.lastrowid
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
            "UPDATE faces SET person_id = ? WHERE id = ?", (person_id, face_id)
        )
