from __future__ import annotations

import os
from typing import List

import pandas as pd
import psycopg2
import plotly.express as px
import streamlit as st


# ==================================================
# CONFIG
# ==================================================
def get_secret(key: str, default=None):
    """
    Safely get a secret:
    - Streamlit Cloud → st.secrets
    - Local dev → environment variables
    """
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key, default)

APP_TITLE = "Explorateur du marché de l'emploi"

st.set_page_config(page_title=APP_TITLE, layout="wide")

# --- DB config via environment / Streamlit secrets
DB_CONFIG = {
    "host": get_secret("DB_HOST"),
    "dbname": get_secret("DB_NAME"),
    "user": get_secret("DB_USER"),
    "password": get_secret("DB_PASSWORD"),
    "port": int(get_secret("DB_PORT", 5432)),
    "connect_timeout": 5,
}
st.write("DB:", DB_CONFIG["host"], DB_CONFIG["dbname"])
st.title(APP_TITLE)


# ==================================================
# DB HELPERS
# ==================================================
@st.cache_data(ttl=600)
def load_dataframe(query: str) -> pd.DataFrame:
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error("Impossible de charger les données depuis la base.")
        st.exception(e)
        return pd.DataFrame()


# ==================================================
# UI — CSS / COMPONENTS
# ==================================================
def inject_global_css() -> None:
    st.markdown(
        """
<style>
/* ---------- Base ---------- */
:root{
  --card:#FFFFFF;
  --muted:#64748B;
  --text:#0F172A;
  --blue:#2563EB;
  --sky:#0EA5E9;
  --border: rgba(15,23,42,.10);
  --shadow: 0 14px 34px rgba(2, 8, 23, .10);
  --radius: 18px;
}

.stApp{
  background:
    radial-gradient(1200px 420px at 12% -10%, rgba(14,165,233,.20), transparent 60%),
    radial-gradient(1000px 420px at 88% -20%, rgba(37,99,235,.18), transparent 55%),
    linear-gradient(180deg, #F6FAFF 0%, #F7FBFF 30%, #F4F8FF 100%);
}

.block-container{
  max-width: 1380px;
  padding-top: 1rem;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def topbar() -> None:
    st.markdown(
        f"""
<div style="padding:18px;border-radius:20px;
background:linear-gradient(90deg,#2563EB,#0EA5E9);
color:white;font-weight:900;font-size:22px;
box-shadow:0 10px 30px rgba(0,0,0,.15)">
{APP_TITLE}
</div>
        """,
        unsafe_allow_html=True,
    )


inject_global_css()
topbar()


# ==================================================
# LOAD DATA
# ==================================================
df_jobs = load_dataframe(
    """
    SELECT
        jo.id,
        jo.title,
        jo.salary_min_annual,
        jo.salary_max_annual,
        jo.date_posted,
        c.type_contrat AS contract,
        l.ville,
        l.code_postal,
        l.latitude,
        l.longitude
    FROM public.job_offer jo
    LEFT JOIN public.contract c ON c.id = jo.contract_id
    LEFT JOIN public.location l ON l.id = jo.location_id
    """
)
st.write(df_jobs.head())

df_skills = load_dataframe(
    """
    SELECT
        s.name,
        s.category,
        jos.requirement_level,
        jos.job_offer_id
    FROM public.job_offer_skill jos
    JOIN public.skill s ON s.id = jos.skill_id
    """
)

if df_jobs.empty:
    st.stop()


# ==================================================
# TABS
# ==================================================
tabs = st.tabs(
    [
        "Marché",
        "Compétences",
        "Salaire",
        "Géographie",
        "Métiers proches",
    ]
)

# ==================================================
# TAB 1 — MARCHÉ
# ==================================================
with tabs[0]:
    st.subheader("Vue globale du marché")

    st.metric("Nombre total d'offres", df_jobs["id"].nunique())

    st.dataframe(
        df_jobs[["title", "ville", "contract"]],
        use_container_width=True,
    )

    st.subheader("Top localisations")

    loc_counts = (
        df_jobs.groupby("ville")
        .size()
        .reset_index(name="nb_offres")
        .sort_values("nb_offres", ascending=False)
        .head(5)
    )

    fig = px.bar(
        loc_counts,
        x="ville",
        y="nb_offres",
        title="Top 5 des villes avec le plus d'offres",
    )
    st.plotly_chart(fig, use_container_width=True)


# ==================================================
# TAB 2 — COMPÉTENCES
# ==================================================
with tabs[1]:
    st.subheader("Analyse des compétences")

    total_jobs = df_jobs["id"].nunique()

    for category, label in [("hard", "Hard skills"), ("soft", "Soft skills")]:
        skills = (
            df_skills[df_skills["category"] == category]
            .groupby("name")["job_offer_id"]
            .nunique()
            .reset_index(name="nb_offres")
            .sort_values("nb_offres", ascending=False)
        )
        skills["pct"] = round(100 * skills["nb_offres"] / total_jobs, 1)

        st.markdown(f"### {label}")
        st.dataframe(skills.head(20), use_container_width=True)

        fig = px.pie(
            skills.head(5),
            names="name",
            values="nb_offres",
            title=f"Top 5 {label.lower()}",
        )
        st.plotly_chart(fig, use_container_width=True)


# ==================================================
# TAB 3 — SALAIRE
# ==================================================
with tabs[2]:
    st.subheader("Analyse des salaires")

    total = len(df_jobs)
    with_salary = df_jobs["salary_min_annual"].notna().sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Offres totales", total)
    col2.metric("Offres avec salaire", with_salary)
    col3.metric("% avec salaire", f"{round(100 * with_salary / total, 1)} %")

    st.dataframe(
        df_jobs[["title", "salary_min_annual", "ville"]]
        .dropna(subset=["salary_min_annual"])
        .head(50),
        use_container_width=True,
    )


# ==================================================
# TAB 4 — GÉOGRAPHIE
# ==================================================
with tabs[3]:
    st.subheader("Répartition géographique")

    df_geo = df_jobs.dropna(subset=["latitude", "longitude"])

    if df_geo.empty:
        st.info("Aucune coordonnée géographique exploitable.")
    else:
        fig_map = px.scatter_mapbox(
            df_geo,
            lat="latitude",
            lon="longitude",
            hover_name="title",
            hover_data=["ville", "contract"],
            zoom=4,
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)


# ==================================================
# TAB 5 — MÉTIERS PROCHES
# ==================================================
with tabs[4]:
    st.subheader("Métiers proches (similarité sémantique)")

    query = st.text_input("Intitulé de poste de référence")

    if query:
        from analysis.job_titles import find_related_job_titles

        results = find_related_job_titles(
            df_jobs[["title"]],
            query_title=query,
            top_n=10,
            min_similarity=0.7,
        )

        if results.empty:
            st.info("Aucun métier proche trouvé.")
        else:
            st.dataframe(results, use_container_width=True)
