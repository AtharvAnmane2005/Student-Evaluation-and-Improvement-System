"""
Inference wrapper around the three trained PLACER artifacts:
  - bi-encoder   (fine-tuned all-MiniLM-L6-v2, sentence-transformers format)
  - cross-encoder (fine-tuned cross-encoder/stsb-roberta-base)
  - calibrator   (sklearn LogisticRegression, Platt scaling)

Deliberately built on plain `transformers` + manual pooling/sigmoid math,
NOT the `sentence-transformers` wrapper classes. Reasoning (see
PROJECT_PROGRESS.md Phase 7/9 section for the full writeup): the saved
cross-encoder uses sentence-transformers 5.x's newer `CrossEncoder` save
format (a `config_sentence_transformers.json` with `model_type:
"CrossEncoder"` and a baked-in `activation_fn`), which an older
sentence-transformers install (e.g. the 3.x originally pinned in
requirements.txt) cannot reliably load. Loading both models via bog-standard
`AutoModel`/`AutoModelForSequenceClassification` sidesteps that fragility
entirely — those classes only care about `config.json` + `model.safetensors`
+ tokenizer files, which are stable, ordinary HuggingFace format regardless
of which wrapper library saved them. The pooling/sigmoid math below is a
direct, deliberate port of the notebook's own training-time evaluation code
(see cells 4 and 11), not a reinterpretation of it.
"""
import logging
import pickle
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)

_ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
_BI_ENCODER_PATH = _ARTIFACTS_DIR / "bi_encoder"
_CROSS_ENCODER_PATH = _ARTIFACTS_DIR / "cross_encoder"
_CALIBRATOR_PATH = _ARTIFACTS_DIR / "calibrator.pkl"

# From the notebook's CELL 2 config block — CROSS_MAX_LENGTH is actually 256
# in the code that ran, despite a stale comment nearby claiming 512 was
# applied. Using what the model was really trained/tokenized with, not what
# the comment says.
_CROSS_MAX_LENGTH = 256
_BI_MAX_LENGTH = 256

_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class MatchingModelsUnavailable(Exception):
    """Raised when the artifact files aren't present — e.g. a deployment
    that hasn't had the (large, git-unfriendly) model weights uploaded yet.
    Callers should catch this and degrade gracefully (skills/experience-only
    scoring, or a clear "matching temporarily unavailable" response) rather
    than the app crashing outright."""


class MatchingEngine:
    """
    Lazily-loaded singleton — the three models total ~570MB and take a real
    amount of time to load from disk plus move onto the inference device.
    Paying that cost at app startup would slow down every deploy/restart
    and every health check; paying it once on first actual use (any
    endpoint that needs a match score) is the better trade for a service
    where matching is one feature among many, not the primary hot path.
    """

    _instance: "MatchingEngine | None" = None

    def __init__(self):
        if not _BI_ENCODER_PATH.exists() or not _CROSS_ENCODER_PATH.exists() or not _CALIBRATOR_PATH.exists():
            raise MatchingModelsUnavailable(
                "Matching model artifacts not found under app/ml/matching/artifacts/. "
                "See PROJECT_PROGRESS.md Phase 7/9 for how these are provisioned "
                "(they're too large for a normal git push — Git LFS or external "
                "hosting is expected for real deployments)."
            )

        logger.info("Loading matching models onto %s ...", _DEVICE)

        self.bi_tokenizer = AutoTokenizer.from_pretrained(str(_BI_ENCODER_PATH))
        self.bi_model = AutoModel.from_pretrained(str(_BI_ENCODER_PATH)).to(_DEVICE).eval()

        self.cross_tokenizer = AutoTokenizer.from_pretrained(str(_CROSS_ENCODER_PATH))
        self.cross_model = (
            AutoModelForSequenceClassification.from_pretrained(str(_CROSS_ENCODER_PATH)).to(_DEVICE).eval()
        )

        with open(_CALIBRATOR_PATH, "rb") as f:
            self.calibrator = pickle.load(f)

        logger.info("Matching models loaded.")

    @classmethod
    def get(cls) -> "MatchingEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Bi-encoder: mean pooling over token embeddings (attention-mask
    # weighted), then L2 normalize — replicates the saved model's own
    # declared pipeline (Transformer -> Pooling(mean) -> Normalize, see
    # modules.json / 1_Pooling/config.json in the artifact folder) by hand.
    # ------------------------------------------------------------------
    @torch.no_grad()
    def embed_texts(self, texts: list[str], batch_size: int = 16) -> np.ndarray:
        if not texts:
            return np.zeros((0, self.bi_model.config.hidden_size), dtype=np.float32)

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            encoded = self.bi_tokenizer(
                batch, padding=True, truncation=True, max_length=_BI_MAX_LENGTH, return_tensors="pt"
            ).to(_DEVICE)

            output = self.bi_model(**encoded)
            token_embeddings = output.last_hidden_state  # (batch, seq_len, hidden)
            attention_mask = encoded["attention_mask"].unsqueeze(-1).float()  # (batch, seq_len, 1)

            summed = (token_embeddings * attention_mask).sum(dim=1)
            counts = attention_mask.sum(dim=1).clamp(min=1e-9)
            mean_pooled = summed / counts

            normalized = torch.nn.functional.normalize(mean_pooled, p=2, dim=1)
            all_embeddings.append(normalized.cpu().numpy())

        return np.concatenate(all_embeddings, axis=0)

    @staticmethod
    def cosine_similarity(query_vec: np.ndarray, candidate_vecs: np.ndarray) -> np.ndarray:
        """Both inputs are expected to already be L2-normalized (embed_texts
        does this), so a plain dot product is the cosine similarity."""
        if candidate_vecs.shape[0] == 0:
            return np.zeros((0,), dtype=np.float32)
        return candidate_vecs @ query_vec

    # ------------------------------------------------------------------
    # Cross-encoder: raw single-logit regression head, sigmoid applied by
    # hand (this is what the notebook's own eval code does — see CELL 11's
    # `1.0/(1+np.exp(-raw))` — not relying on the saved config's
    # `activation_fn` metadata being auto-applied by a wrapper we're not using).
    # ------------------------------------------------------------------
    @torch.no_grad()
    def cross_score(self, pairs: list[tuple[str, str]], batch_size: int = 16) -> np.ndarray:
        if not pairs:
            return np.zeros((0,), dtype=np.float32)

        all_scores = []
        for i in range(0, len(pairs), batch_size):
            batch = pairs[i : i + batch_size]
            texts_a = [p[0] for p in batch]
            texts_b = [p[1] for p in batch]
            encoded = self.cross_tokenizer(
                texts_a, texts_b, padding=True, truncation=True, max_length=_CROSS_MAX_LENGTH, return_tensors="pt"
            ).to(_DEVICE)

            output = self.cross_model(**encoded)
            raw_logits = output.logits.squeeze(-1)  # (batch,) — num_labels=1
            raw_logits = torch.clamp(raw_logits, -50, 50)  # matches the notebook's overflow guard
            sigmoid_scores = torch.sigmoid(raw_logits)
            all_scores.append(sigmoid_scores.cpu().numpy())

        return np.concatenate(all_scores, axis=0)

    def calibrate(self, sigmoid_scores: np.ndarray) -> np.ndarray:
        """Platt scaling: sigmoid cross-encoder score -> calibrated match
        probability. `coef_`/`intercept_` were fit on exactly this input
        shape (a single feature column) — see CELL 12 of the notebook."""
        if sigmoid_scores.shape[0] == 0:
            return sigmoid_scores
        return self.calibrator.predict_proba(sigmoid_scores.reshape(-1, 1))[:, 1]
