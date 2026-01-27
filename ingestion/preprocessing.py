import os
import re
import unicodedata
from typing import Optional, Tuple

import pandas as pd


# ==================================================
# TEXT NORMALIZATION
# ==================================================
def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_job_title(title: str) -> str:
    if not isinstance(title, str):
        return ""
    title = title.lower()
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"[^a-zàâçéèêëîïôûùüÿñæœ\s]", " ", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


# ==================================================
# SALARY PARSING — FRANCE TRAVAIL
# ==================================================
def extract_numbers(text: str) -> list[float]:
    if not text:
        return []
    nums = re.findall(r"\d+(?:[\.,]\d+)?", text)
    return [float(n.replace(",", ".")) for n in nums]


def detect_salary_unit(text: str) -> str:
    if "horaire" in text or "/h" in text:
        return "hourly"
    if "mois" in text or "mensuel" in text:
        return "monthly"
    return "annual"


def to_annual(amount: float, unit: str) -> float:
    if unit == "monthly":
        return amount * 12
    if unit == "hourly":
        return amount * 151.67 * 12
    return amount


def parse_salary_france_travail(
    salary_text: str,
) -> Tuple[Optional[float], Optional[float]]:
    text = normalize_text(salary_text)
    numbers = extract_numbers(text)

    if not numbers:
        return None, None

    if max(numbers) == 0:
        return None, None

    unit = detect_salary_unit(text)

    if unit == "annual" and max(numbers) < 1000:
        numbers = [n * 1000 for n in numbers]

    if len(numbers) == 1:
        value = to_annual(numbers[0], unit)
        return value, value

    return to_annual(min(numbers), unit), to_annual(max(numbers), unit)


# ==================================================
# LOCATION PREPROCESSING (BY DEPARTMENT)
# ==================================================
def normalize_unicode(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.encode("latin1", errors="ignore").decode("utf-8", errors="ignore")
    text = unicodedata.normalize("NFKC", text)
    return text.strip()


# ---------- Load department referential ----------
_DEPT_GEO = None


def load_dept_geo(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # Normalize department code → "01", "02", ..., "75"
    df["dep_code"] = df["dep_code"].astype(str).str.zfill(2)

    return df.set_index("dep_code")


def get_dept_geo() -> Optional[pd.DataFrame]:
    global _DEPT_GEO
    if _DEPT_GEO is not None:
        return _DEPT_GEO

    path = os.getenv("DEPT_GEO_CSV", "").strip()
    if not path:
        return None

    _DEPT_GEO = load_dept_geo(path)
    return _DEPT_GEO


# ---------- Main parser ----------
def clean_city_name(city: str) -> str:
    """
    Remove arrondissement / district info from city names
    Examples:
    - "Paris 9e arrondissement" -> "Paris"
    - "Paris 1er Arrondissement" -> "Paris"
    """
    if not isinstance(city, str):
        return city

    city = city.strip()

    # Remove arrondissement patterns
    city = re.sub(
        r"\s+\d{1,2}(er|e)?\s+arrondissement.*$",
        "",
        city,
        flags=re.IGNORECASE,
    )

    # Safety: remove trailing commas or spaces
    city = city.rstrip(", ").strip()

    return city

def parse_location(
    location: str,
) -> Tuple[Optional[str], Optional[str], Optional[float], Optional[float]]:
    """
    Input  : "75 - Paris"
    Output : (dep_code, city, latitude, longitude)
    """

    if not isinstance(location, str):
        return None, None, None, None

    location = normalize_unicode(location)

    # Extract department code and raw city before "-"
    match = re.match(r"^\s*(\d{1,3})\s*-\s*(.+)$", location)
    if not match:
        return None, None, None, None

    dep_code = match.group(1).zfill(2)
    city_raw = clean_city_name(match.group(2))

    dept_geo = get_dept_geo()

    # If no referential → keep FT city, no GPS
    if dept_geo is None or dep_code not in dept_geo.index:
        return dep_code, city_raw, None, None

    row = dept_geo.loc[dep_code]

    # Fallback city: FT city first, else department name
    city = city_raw if city_raw else row["dep_nom"]

    return (
        dep_code,
        city,
        float(row["latitude_mairie"]) if pd.notna(row["latitude_mairie"]) else None,
        float(row["longitude_mairie"]) if pd.notna(row["longitude_mairie"]) else None,
    )