

import numpy as np
import psycopg2
from sklearn.cluster import DBSCAN


class FaceClustering:

    def __init__(self, face_repo, person_repo):
        self.face_repo = face_repo
        self.person_repo = person_repo

    def assign_person_ids(self):
        faces = self._load_faces()
        if not faces:
            print("No faces in database.")
            return

        face_ids, embeddings = zip(*faces)
        embeddings_array = np.array(embeddings)

        labels = self._cluster_embeddings(embeddings_array)
        unique_labels = np.unique(labels)

        people_avg_embeddings = self._load_people_embeddings()
        label_to_person_id = self._assign_clusters_to_people(
            embeddings_array, labels, unique_labels, people_avg_embeddings
        )

        self._update_faces_with_person_ids(
            face_ids, labels, label_to_person_id)

        print(
            f"Assigned person_id to {len(face_ids)} faces and created {len(unique_labels)} people.")

    def _load_faces(self):
        rows = self.face_repo.get_all_embeddings()
        faces = []

        for row in rows:
            face_id = row['id']
            embedding_bytes = row['embedding']

            if isinstance(embedding_bytes, memoryview):
                embedding_bytes = embedding_bytes.tobytes()

            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            faces.append((face_id, embedding))

        return faces

    def _cluster_embeddings(self, embeddings_array):
        clustering = DBSCAN(metric='cosine', eps=0.4,
                            min_samples=1).fit(embeddings_array)
        return clustering.labels_

    def _load_people_embeddings(self):
        people_rows = self.person_repo.get_all_people_data()
        people_avg_embeddings = {}

        for person_id, name, avg_bytes in people_rows:
            if avg_bytes is None:
                people_avg_embeddings[person_id] = None
                continue

            # avg_bytes has to be BYTEA
            if isinstance(avg_bytes, memoryview):
                avg_bytes = avg_bytes.tobytes()

            elif isinstance(avg_bytes, str):
                try:
                    if avg_bytes.startswith("\\x"):
                        avg_bytes = bytes.fromhex(avg_bytes[2:])
                    else:
                        avg_bytes = avg_bytes.encode('latin1')
                except Exception as e:
                    people_avg_embeddings[person_id] = None
                    continue
            if len(avg_bytes) % 4 != 0:
                people_avg_embeddings[person_id] = None
                continue

            arr = np.frombuffer(avg_bytes, dtype=np.float32)
            people_avg_embeddings[person_id] = arr

        return people_avg_embeddings

    def _assign_clusters_to_people(self, embeddings_array, labels, unique_labels, people_avg_embeddings):
        label_to_person_id = {}
        next_person_index = len(people_avg_embeddings)

        for label in unique_labels:
            cluster_indices = [i for i, l in enumerate(labels) if l == label]
            cluster_embeddings = embeddings_array[cluster_indices]
            cluster_avg = np.mean(cluster_embeddings, axis=0)

            matched_person_id = self._find_matching_person(
                cluster_avg, people_avg_embeddings)

            if matched_person_id is not None:
                person_id = matched_person_id
                all_embeddings = np.vstack(
                    [cluster_embeddings,
                        people_avg_embeddings[person_id].reshape(1, -1)]
                )
                new_avg = np.mean(all_embeddings, axis=0)

                self.person_repo.update_embedding(person_id, new_avg.tobytes())

                people_avg_embeddings[person_id] = new_avg
            else:
                person_name = f"Person{next_person_index}"
                avg_bytes = cluster_avg.tobytes() if cluster_avg is not None else None

                person_id = self.person_repo.create_person(
                    person_name, avg_bytes)

                people_avg_embeddings[person_id] = cluster_avg
                next_person_index += 1

            label_to_person_id[label] = person_id

        return label_to_person_id

    def _find_matching_person(self, cluster_avg, people_avg_embeddings, threshold=0.5):
        for person_id, avg_emb in people_avg_embeddings.items():
            if avg_emb is not None:
                dist = np.linalg.norm(cluster_avg - avg_emb)
                if dist < threshold:
                    return person_id
        return None

    def _update_faces_with_person_ids(self, face_ids, labels, label_to_person_id):
        for face_id, label in zip(face_ids, labels):
            person_id = label_to_person_id[label]
            self.face_repo.update_person_id(face_id, person_id)
