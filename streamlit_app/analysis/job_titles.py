import pandas as pd
import re
from collections import Counter
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ==================================================
# MODEL (CACHED)
# ==================================================
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


@st.cache_resource
def load_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


model = load_model()


# ==================================================
# HELPERS
# ==================================================
def normalize_title(title: str) -> str:
    if not isinstance(title, str):
        return ""
    title = title.lower()
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", " ", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


def embed(texts: list[str]):
    return model.encode(texts, normalize_embeddings=True)


# ==================================================
# MAIN FUNCTION
# ==================================================
def find_related_job_titles(
    df: pd.DataFrame,
    query_title: str,
    top_n: int = 10,
    min_similarity: float = 0.7,
) -> pd.DataFrame:
    """
    Find job titles semantically close to a given title
    """

    if "title" not in df.columns or not query_title:
        return pd.DataFrame()

    df = df.copy()
    df["title_clean"] = df["title"].apply(normalize_title)

    title_counts = Counter(df["title_clean"])
    unique_titles = list(title_counts.keys())

    if not unique_titles:
        return pd.DataFrame()

    query_clean = normalize_title(query_title)

    query_emb = embed([query_clean])
    titles_emb = embed(unique_titles)

    similarities = cosine_similarity(query_emb, titles_emb)[0]

    results = [
        {
            "job_title": title,
            "similarity": round(sim, 3),
            "nb_offres": title_counts[title],
        }
        for title, sim in zip(unique_titles, similarities)
        if sim >= min_similarity and title != query_clean
    ]

    if not results:
        return pd.DataFrame()

    return (
        pd.DataFrame(results)
        .sort_values(["similarity", "nb_offres"], ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
