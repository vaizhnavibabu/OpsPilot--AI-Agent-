from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from src.agent.config import settings

KNOWLEDGE_DIR = Path("data/raw/knowledge")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class KnowledgeRetriever:
    def __init__(self):
        print("Loading embedding model...")
        self.model = SentenceTransformer(
            MODEL_NAME,
            device="cpu",
        )

        self.documents = []
        self.embeddings = None
        
        # TF-IDF Vectorizer for keyword search baseline
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = None

        self._load_documents()

    def _load_documents(self):
        for path in KNOWLEDGE_DIR.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.documents.append(
                {
                    "source": path.name,
                    "text": text,
                }
            )

        if not self.documents:
            raise RuntimeError(
                f"No knowledge documents found in {KNOWLEDGE_DIR}"
            )

        texts = [document["text"] for document in self.documents]

        # Fit embedding index
        self.embeddings = self.model.encode(
            texts,
            batch_size=1,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        # Fit TF-IDF matrix for keyword search
        self.tfidf_matrix = self.vectorizer.fit_transform(texts)

        print(
            f"Loaded {len(self.documents)} knowledge documents."
        )

    def search(self, query: str, top_k: int | None = None, min_score: float | None = None) -> list[dict]:
        """Embedding search (cosine similarity on sentence-transformer embeddings)."""
        if top_k is None:
            top_k = settings.retrieval_top_k
        if min_score is None:
            min_score = settings.min_retrieval_score

        query_embedding = self.model.encode(
            [query],
            batch_size=1,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        scores = cosine_similarity(
            query_embedding,
            self.embeddings,
        )[0]

        ranked_indexes = scores.argsort()[::-1]
        results = []

        for index in ranked_indexes:
            score = float(scores[index])
            if score >= min_score:
                results.append(
                    {
                        "source": self.documents[index]["source"],
                        "text": self.documents[index]["text"],
                        "score": score,
                    }
                )
            if len(results) >= top_k:
                break

        return results

    def search_keyword(self, query: str, top_k: int | None = None) -> list[dict]:
        """Keyword search baseline using TF-IDF and cosine similarity."""
        if top_k is None:
            top_k = settings.retrieval_top_k

        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.tfidf_matrix)[0]

        ranked_indexes = scores.argsort()[::-1]
        results = []

        for index in ranked_indexes:
            score = float(scores[index])
            # Even for keyword search, we only return non-zero matches up to top_k
            if score > 0.0:
                results.append(
                    {
                        "source": self.documents[index]["source"],
                        "text": self.documents[index]["text"],
                        "score": score,
                    }
                )
            if len(results) >= top_k:
                break

        return results


if __name__ == "__main__":
    retriever = KnowledgeRetriever()
    results = retriever.search("I forgot my password and cannot login")
    for result in results:
        print("=" * 60)
        print("SOURCE:", result["source"])
        print("SCORE:", round(result["score"], 3))