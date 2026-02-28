from typing import Any
import numpy as np
from sklearn.cluster import AgglomerativeClustering


class FaceClustering:

    def __init__(self, face_repo: Any, person_repo: Any):
        self.face_repo = face_repo
        self.person_repo = person_repo
        self.threshold = 0.6

    def resolve_identities(self) -> None:
        print("CLUSTERING: Starting robust incremental clustering...")

        unassigned_faces, known_faces = self._load_split_faces()

        if not unassigned_faces:
            return

        new_face_ids = [f[0] for f in unassigned_faces]
        new_embs = np.array([f[1] for f in unassigned_faces])

        # LOCAL CLUSTERING: Cluster unassigned faces to find groups of similar faces
        cluster_labels = self._run_local_clustering(new_embs)
        unique_clusters = np.unique(cluster_labels)

        known_person_ids = np.array(
            [f[0] for f in known_faces]) if known_faces else np.array([])
        known_embs = np.array([f[1] for f in known_faces]
                              ) if known_faces else np.array([])

        new_people_count = 0
        matched_people_count = 0

        # For each local cluster, try to match it to known people or create a new person
        for cluster_id in unique_clusters:
            cluster_indices = np.where(cluster_labels == cluster_id)[0]
            cluster_embs = new_embs[cluster_indices]

            matched_person_id = None

            if len(known_embs) > 0:
                # Calculate cosine distances between ALL faces in this cluster
                # and ALL faces in the known db simultaneously.
                sim_matrix = np.dot(cluster_embs, known_embs.T)
                distances = 1.0 - sim_matrix

                # Find the closest match
                min_dist = np.min(distances)

                # If the closest match is within the threshold, consider it a match
                if min_dist < self.threshold:
                    best_match_idx = np.unravel_index(
                        np.argmin(distances, axis=None), distances.shape)[1]
                    matched_person_id = known_person_ids[best_match_idx]

            if matched_person_id is not None:
                final_person_id = matched_person_id
                matched_people_count += 1
            else:
                existing_people = self.person_repo.get_all_people_data()
                next_num = len(existing_people) + 1 if existing_people else 1
                person_name = f"Person{next_num}"

                dummy_bytes = np.zeros(512, dtype=np.float32).tobytes()
                final_person_id = self.person_repo.create_person(
                    person_name, dummy_bytes)
                new_people_count += 1

            # Update known embeddings with the new cluster's embeddings for future matches
            for emb in cluster_embs:
                if len(known_embs) == 0:
                    known_embs = np.array([emb])
                    known_person_ids = np.array([final_person_id])
                else:
                    known_embs = np.vstack([known_embs, emb])
                    known_person_ids = np.append(
                        known_person_ids, final_person_id)

            # Assign person_id in DB to all faces in this cluster
            for idx in cluster_indices:
                self.face_repo.update_person_id(
                    int(new_face_ids[idx]),
                    int(final_person_id)
                )

        print(f"CLUSTERING: Done!")

    def _normalize_l2(self, vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _run_local_clustering(self, embeddings_array: np.ndarray) -> np.ndarray:
        if len(embeddings_array) < 2:
            return np.array([0])

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=self.threshold,
            metric='cosine',
            linkage='average'
        ).fit(embeddings_array)

        return clustering.labels_

    def _load_split_faces(self) -> tuple[list[tuple[int, np.ndarray]], list[tuple[int, np.ndarray]]]:
        rows = self.face_repo.get_all_embeddings()
        unassigned = []
        known = []

        for row in rows:
            face_id = row['id']
            emb_bytes = row['embedding']
            person_id = row['person_id']

            if not emb_bytes:
                continue

            if isinstance(emb_bytes, memoryview):
                emb_bytes = emb_bytes.tobytes()

            emb = np.frombuffer(emb_bytes, dtype=np.float32)
            emb = self._normalize_l2(emb)

            if person_id is None:
                unassigned.append((face_id, emb))
            else:
                known.append((person_id, emb))

        return unassigned, known
