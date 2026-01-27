from __future__ import annotations

import pandas as pd
import streamlit as st
import psycopg2
import plotly.express as px

# ==================================================
# CONFIG
# ==================================================
APP_TITLE = "Explorateur du marché de l'emploi"

DB_CONFIG = {
    "host": "localhost",
    "dbname": "job_market_analysis",
    "user": "job_app",
    "password": "123456",
    "port": 5432,
}

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)


# ==================================================
# DB HELPERS
# ==================================================
@st.cache_data
def load_dataframe(query: str) -> pd.DataFrame:
    conn = psycopg2.connect(**DB_CONFIG)
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# ==================================================
# LOAD CORE DATA
# ==================================================
df_jobs = load_dataframe("""
SELECT
    jo.id,
    jo.title,
    jo.salary_min_annual AS salary_min_annual,
    jo.salary_max_annual AS salary_max_annual,
    jo.date_posted,
    c.type_contrat AS contract,
    l.ville,
    l.code_postal,
    l.latitude,
    l.longitude
FROM job_offer jo
LEFT JOIN contract c ON c.id = jo.contract_id
LEFT JOIN location l ON l.id = jo.location_id
""")

df_skills = load_dataframe("""
SELECT
    s.name,
    s.category,
    jos.requirement_level,
    jos.job_offer_id
FROM job_offer_skill jos
JOIN skill s ON s.id = jos.skill_id
""")


# ==================================================
# TABS
# ==================================================
tabs = st.tabs([
    "Marché",
    "Compétences",
    "Salaire",
    "Géographie",
    "Métiers proches"
])

# ==================================================
# TAB 1 — MARCHÉ
# ==================================================
with tabs[0]:
    st.subheader("Vue globale du marché")

    st.metric("Nombre total d'offres", len(df_jobs))

    st.dataframe(
        df_jobs[["title", "ville", "contract"]].head(50),
        use_container_width=True
    )

    st.subheader("Top localisations")

    loc_counts = (
        df_jobs
        .groupby("ville")
        .size()
        .reset_index(name="nb_offres")
        .sort_values("nb_offres", ascending=False)
        .head(5)
    )

    fig = px.bar(
        loc_counts,
        x="ville",
        y="nb_offres",
        title="Top 20 des localisations",
    )
    st.plotly_chart(fig, use_container_width=True)


# ==================================================
# TAB 2 — COMPÉTENCES
# ==================================================
with tabs[1]:
    st.subheader("Analyse des compétences")

    total_jobs = df_jobs["id"].nunique()

    # ---------- Hard skills
    hard = (
        df_skills[df_skills["category"] == "hard"]
        .groupby("name")["job_offer_id"]
        .nunique()
        .reset_index(name="nb_offres")
        .sort_values("nb_offres", ascending=False)
    )
    hard["pct"] = round(100 * hard["nb_offres"] / total_jobs, 1)

    st.markdown("### Hard skills")
    st.dataframe(hard.head(20), use_container_width=True)

    fig_hard = px.pie(
        hard.head(5),
        names="name",
        values="nb_offres",
        title="Top 5 hard skills",
    )
    st.plotly_chart(fig_hard, use_container_width=True)

    # ---------- Soft skills
    soft = (
        df_skills[df_skills["category"] == "soft"]
        .groupby("name")["job_offer_id"]
        .nunique()
        .reset_index(name="nb_offres")
        .sort_values("nb_offres", ascending=False)
    )
    soft["pct"] = round(100 * soft["nb_offres"] / total_jobs, 1)

    st.markdown("### Soft skills")
    st.dataframe(soft.head(20), use_container_width=True)

    fig_soft = px.pie(
        soft.head(5),
        names="name",
        values="nb_offres",
        title="Top 5 soft skills",
    )
    st.plotly_chart(fig_soft, use_container_width=True)


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
    col3.metric(
        "% avec salaire",
        f"{round(100 * with_salary / total, 1)} %"
    )

    st.markdown("### Exemples d'offres avec salaire renseigné")

    st.dataframe(
        df_jobs[["title", "salary_min_annual", "ville"]]
        .dropna(subset=["salary_min_annual"])
        .head(50),
        use_container_width=True
    )


# ==================================================
# TAB 4 — GÉOGRAPHIE
# ==================================================
with tabs[3]:
    st.subheader("Répartition géographique")

    df_geo = df_jobs.dropna(subset=["latitude", "longitude"])

    if not df_geo.empty:
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
    else:
        st.info("Aucune coordonnée géographique exploitable.")


# ==================================================
# TAB 5 — MÉTIERS PROCHES
# ==================================================
with tabs[4]:
    st.subheader("Métiers proches (similarité sémantique)")

    query = st.text_input("Intitulé de poste de référence")

    if st.button("Rechercher"):
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
