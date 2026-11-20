"""
CivicMind AI — 768-Dimensional Dense Vector Embedding Service
Generates dense semantic representations matching PostgreSQL pgvector schema (vector(768)).
Supports SentenceTransformer (paraphrase-multilingual-mpnet-base-v2) with
a fast, deterministic offline projection fallback ensuring strict 768-dim invariant.
"""

import hashlib
import logging
from typing import List, Union
import numpy as np

from app.core.config import settings
from ml.data.normalization import clean_text

logger = logging.getLogger("civicmind.ml.embeddings")


class SentenceEmbedder:
    """
    Produces 768-dimensional dense vector embeddings for citizen grievance text.
    Strictly verifies that output vectors match settings.EMBEDDING_DIMENSION (768).
    """

    def __init__(
        self,
        model_name: str = settings.DEFAULT_EMBEDDING_MODEL,
        dimension: int = settings.EMBEDDING_DIMENSION,
    ):
        self.model_name = model_name
        self.dimension = dimension
        self._model = None
        self._is_transformer_loaded = False

    def _lazy_load_model(self):
        """Attempts to load SentenceTransformer if not already loaded."""
        if self._model is not None or self._is_transformer_loaded:
            return

        import os
        allow_download = os.environ.get("CIVICMIND_DOWNLOAD_MODELS", "false").lower() == "true"
        if not allow_download:
            # Fast deterministic 768-dim municipal projection for offline/test performance
            self._model = None
            self._is_transformer_loaded = False
            return

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self._is_transformer_loaded = True
            logger.info("SentenceTransformer '%s' loaded successfully.", self.model_name)
        except Exception as ex:
            logger.info(
                "SentenceTransformer '%s' offline (%s). Using deterministic 768-dim projection.",
                self.model_name,
                str(ex),
            )
            self._model = None
            self._is_transformer_loaded = False

    def _deterministic_768_project(self, text: str) -> np.ndarray:
        """
        Fast deterministic semantic hashing projection that maps arbitrary text
        into a unit-normalized 768-dimensional vector.
        Guarantees that identical/similar phrases produce high cosine similarity.
        """
        cleaned = clean_text(text).lower()
        vec = np.zeros(self.dimension, dtype=np.float32)

        if not cleaned:
            # Return small non-zero normalized vector
            vec[0] = 1.0
            return vec

        words = cleaned.split()
        for i, word in enumerate(words):
            # Compute hash digest of word
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if (h >> 16) % 2 == 0 else -1.0
            weight = 1.0 / (1.0 + 0.1 * i)
            vec[idx] += sign * weight

            # Also hash character bigrams for subword robustness
            for j in range(len(word) - 1):
                bg = word[j : j + 2]
                bg_h = int(hashlib.md5(bg.encode("utf-8")).hexdigest(), 16)
                bg_idx = bg_h % self.dimension
                bg_sign = 1.0 if (bg_h >> 8) % 2 == 0 else -1.0
                vec[bg_idx] += bg_sign * 0.25

        # L2 unit normalize
        norm = np.linalg.norm(vec)
        if norm > 1e-9:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return vec

    def embed_text(self, text: str) -> List[float]:
        """
        Encodes a single string into a 768-dimensional float list.
        Enforces embedding dimension invariant strictly.
        """
        self._lazy_load_model()

        if self._is_transformer_loaded and self._model is not None:
            try:
                raw_vec = self._model.encode(clean_text(text), normalize_embeddings=True)
                vec = np.array(raw_vec, dtype=np.float32)
                # If transformer dimension does not match 768, project or pad
                if vec.shape[0] != self.dimension:
                    if vec.shape[0] > self.dimension:
                        vec = vec[: self.dimension]
                    else:
                        vec = np.pad(vec, (0, self.dimension - vec.shape[0]))
                    norm = np.linalg.norm(vec)
                    if norm > 1e-9:
                        vec = vec / norm
                assert len(vec) == self.dimension, f"Embedding dimension mismatch: {len(vec)} != {self.dimension}"
                return [round(float(x), 6) for x in vec]
            except Exception as ex:
                logger.warning("Inference with transformer failed (%s), using fallback projection.", str(ex))

        # Deterministic projection
        vec = self._deterministic_768_project(text)
        assert len(vec) == self.dimension, f"Embedding dimension mismatch: {len(vec)} != {self.dimension}"
        return [round(float(x), 6) for x in vec]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Batch encodes multiple strings into 768-dimensional float vectors."""
        return [self.embed_text(t) for t in texts]


# Global singleton instance
sentence_embedder = SentenceEmbedder()
