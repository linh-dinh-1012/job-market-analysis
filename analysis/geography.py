import pandas as pd
import folium
from folium.plugins import MarkerCluster


# ==================================================
# FRANCE TRAVAIL — MAP ANALYSIS
# ==================================================
def create_ft_jobs_map(
    df: pd.DataFrame,
    center: list[float] | None = None,
    zoom_start: int = 5,
):
    """
    Create an interactive map showing job offers
    (only rows with valid latitude / longitude)

    Expected columns:
    - latitude
    - longitude
    - title
    - ville
    """

    required_cols = {"latitude", "longitude", "title", "ville"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"DataFrame must contain columns: {required_cols}"
        )

    df_geo = df.dropna(subset=["latitude", "longitude"])

    if df_geo.empty:
        return None

    if center is None:
        center = [df_geo["latitude"].mean(), df_geo["longitude"].mean()]

    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles="CartoDB positron",
    )

    marker_cluster = MarkerCluster().add_to(m)

    for row in df_geo.itertuples():
        popup = (
            f"<b>{row.title}</b><br>"
            f"{row.ville}"
        )

        folium.Marker(
            location=[row.latitude, row.longitude],
            popup=popup,
            icon=folium.Icon(
                color="darkblue",
                icon="briefcase",
                prefix="fa",
            ),
        ).add_to(marker_cluster)

    return m


# ==================================================
# BASIC GEO STATS (OPTIONAL KPI)
# ==================================================
def jobs_by_location(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Count number of job offers by city
    """
    if "ville" not in df.columns:
        raise ValueError("DataFrame must contain column 'ville'")

    return (
        df["ville"]
        .value_counts()
        .head(top_n)
        .reset_index(name="count")
        .rename(columns={"index": "ville"})
    )
