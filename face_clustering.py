import numpy as np
from sklearn.cluster import DBSCAN
from collections import Counter


class FaceClustering:

    def __init__(self, face_repo, person_repo):
        self.face_repo = face_repo
        self.person_repo = person_repo

    def resolve_identities(self):
        faces = self._load_faces()

        if not faces:
            print("CLUSTERING: No faces in database.")
            return

        face_ids, embeddings, current_person_ids = zip(*faces)
        embeddings_array = np.array(embeddings)

        # array([ 0, 0, 0, 1, 1, -1])
        cluster_ids = self._cluster_embeddings(embeddings_array)
        # array([-1, 0, 1])
        unique_cluster_ids = np.unique(cluster_ids)

        people_avg_embeddings = self._load_people_embeddings()

        cluster_id_to_person_id = self._assign_clusters_to_people(
            embeddings_array, cluster_ids, unique_cluster_ids,
            people_avg_embeddings, current_person_ids
        )

        self._update_faces_with_person_ids(
            face_ids, cluster_ids, cluster_id_to_person_id)

        print(f"CLUSTERING: Processed {len(face_ids)} faces.")

    def _load_faces(self):
        rows = self.face_repo.get_all_embeddings()
        faces = []

        for row in rows:
            face_id = row['id']
            embedding_bytes = row['embedding']

            current_person_id = None
            if len(row) > 2:
                current_person_id = row['person_id']

            if isinstance(embedding_bytes, memoryview):
                embedding_bytes = embedding_bytes.tobytes()

            if not embedding_bytes:
                continue

            embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
            faces.append((face_id, embedding, current_person_id))

        return faces

    def _cluster_embeddings(self, embeddings_array):
        # eps 0.45 - mabye change later
        clustering = DBSCAN(metric='cosine', eps=0.45,
                            min_samples=1).fit(embeddings_array)
        return clustering.labels_

    def _load_people_embeddings(self):
        people_rows = self.person_repo.get_all_people_data()
        people_avg_embeddings = {}

        for person_id, name, avg_bytes in people_rows:
            if avg_bytes is None:
                continue

            if isinstance(avg_bytes, memoryview):
                avg_bytes = avg_bytes.tobytes()
            elif isinstance(avg_bytes, str):
                try:
                    if avg_bytes.startswith("\\x"):
                        avg_bytes = bytes.fromhex(avg_bytes[2:])
                    else:
                        avg_bytes = avg_bytes.encode('latin1')
                except Exception:
                    continue

            if len(avg_bytes) % 4 != 0:
                continue

            arr = np.frombuffer(avg_bytes, dtype=np.float32)
            people_avg_embeddings[person_id] = arr

        return people_avg_embeddings

    def _assign_clusters_to_people(self, embeddings_array, cluster_ids, unique_cluster_ids,
                                   people_avg_embeddings, current_person_ids):
        cluster_id_to_person_id = {}

        existing_ids = list(people_avg_embeddings.keys())
        next_person_num = (max(existing_ids) + 1) if existing_ids else 1

        for cluster_id in unique_cluster_ids:
            if cluster_id == -1:
                continue

            cluster_indices = [i for i, l in enumerate(
                cluster_ids) if l == cluster_id]

            # Are there any existing people IDs in this cluster?
            owners = [current_person_ids[i]
                      for i in cluster_indices if current_person_ids[i] is not None]

            dominant_person_id = None
            if owners:
                dominant_person_id = Counter(owners).most_common(1)[0][0]

            cluster_embeddings = embeddings_array[cluster_indices]
            cluster_avg = np.mean(cluster_embeddings, axis=0)

            final_person_id = None

            # A = At least one person in cluster is EXISTING
            if dominant_person_id is not None:
                final_person_id = dominant_person_id

            # B = All people from this cluster are NEW
            else:
                matched_id = self._find_matching_person(
                    cluster_avg, people_avg_embeddings)
                if matched_id:
                    final_person_id = matched_id

            if final_person_id is not None:
                person_id = final_person_id

                if person_id in people_avg_embeddings:
                    all_embeddings = np.vstack(
                        [cluster_embeddings, people_avg_embeddings[person_id].reshape(1, -1)])
                    new_avg = np.mean(all_embeddings, axis=0)
                else:
                    new_avg = cluster_avg

                self.person_repo.update_embedding(person_id, new_avg.tobytes())
                people_avg_embeddings[person_id] = new_avg

            else:
                person_name = f"Person {next_person_num}"
                avg_bytes = cluster_avg.tobytes()
                person_id = self.person_repo.create_person(
                    person_name, avg_bytes)

                people_avg_embeddings[person_id] = cluster_avg
                next_person_num += 1

            cluster_id_to_person_id[cluster_id] = person_id

        return cluster_id_to_person_id

    def _find_matching_person(self, cluster_avg, people_avg_embeddings, threshold=0.45):
        best_match_id = None
        min_dist = float('inf')

        for person_id, avg_emb in people_avg_embeddings.items():
            if avg_emb is not None:
                dist = np.linalg.norm(cluster_avg - avg_emb)
                if dist < threshold and dist < min_dist:
                    min_dist = dist
                    best_match_id = person_id
        return best_match_id

    def _update_faces_with_person_ids(self, face_ids, cluster_ids, cluster_id_to_person_id):
        for face_id, cluster_id in zip(face_ids, cluster_ids):
            if cluster_id == -1:
                continue

            person_id = cluster_id_to_person_id.get(cluster_id)
            if person_id:
                self.face_repo.update_person_id(face_id, person_id)
