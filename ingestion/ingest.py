import os
import time
import json
import requests
import pandas as pd
from datetime import datetime

from config import settings
from db import get_connection

from repositories import get_or_create_location

from repositories import (
    get_or_create_company,
    get_or_create_job_offer,
    get_or_create_skill,
    get_or_create_location,
    get_or_create_industry,
    link_job_offer_skill,
    get_or_create_contract, 
)

from preprocessing import (
    parse_salary_france_travail,
    parse_location,
)

# ==================================================
# France Travail API
# ==================================================

FT_SEARCH_URL = (
    "https://api.francetravail.io/partenaire/"
    "offresdemploi/v2/offres/search"
)


def get_ft_access_token() -> str:
    resp = requests.post(
        "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire",
        data={
            "grant_type": "client_credentials",
            "client_id": os.environ["FT_CLIENT_ID"],
            "client_secret": os.environ["FT_CLIENT_SECRET"],
            "scope": "api_offresdemploiv2 o2dsoffre",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch_all_ft_offers(
    token: str,
    keywords: str,
    location: str | None = None,
    contract_type: str | None = None,
    step: int = 150,
    max_results: int = 600,
) -> list[dict]:
    headers = {"Authorization": f"Bearer {token}"}
    all_results = []
    start = 0

    while start < max_results:
        params = {
            "motsCles": keywords,
            "range": f"{start}-{start + step - 1}",
            "sort": "1",
        }

        if location:
            params["lieuTravail"] = location
        if contract_type:
            params["typeContrat"] = contract_type

        r = requests.get(FT_SEARCH_URL, headers=headers, params=params)
        r.raise_for_status()

        results = r.json().get("resultats", [])
        if not results:
            break

        all_results.extend(results)

        if len(results) < step:
            break

        start += step
        time.sleep(0.5)

    return all_results


# ==================================================
# Helpers preprocessing FT
# ==================================================

def extract_required_optional(items):
    if not isinstance(items, list):
        return [], []
    required = [i.get("libelle") for i in items if i.get("exigence") == "E"]
    optional = [i.get("libelle") for i in items if i.get("exigence") == "S"]
    return required, optional


def to_date(x):
    if not x:
        return None
    return datetime.fromisoformat(x.replace("Z", "+00:00")).date()


def preprocess_ft(raw_items: list[dict]) -> pd.DataFrame:
    rows = []

    for item in raw_items:
        r_sk, o_sk = extract_required_optional(item.get("competences"))
        r_lg, o_lg = extract_required_optional(item.get("langues"))

        raw_salary = item.get("salaire", {}).get("libelle")
        salary_min, salary_max = parse_salary_france_travail(raw_salary)

        raw_location = item.get("lieuTravail", {}).get("libelle")
        dep_code, city, latitude, longitude = parse_location(raw_location)

        rows.append({
            "url": (
                item.get("origineOffre", {}).get("urlOrigine")
                or f"francetravail:{item.get('id')}"
            ),
            "title": item.get("intitule"),
            "description": item.get("description"),
            "company": item.get("entreprise", {}).get("nom"),
            "industry": item.get("secteurActiviteLibelle"),
            "experience": item.get("experienceLibelle"),
            "education": (
                ", ".join(f.get("libelle", "") for f in item.get("formations", []))
                if isinstance(item.get("formations"), list)
                else None
            ),
            "contract": item.get("typeContratLibelle"),
            "salary_raw": raw_salary,
            "salary_min_annual": salary_min,
            "salary_max_annual": salary_max,
            "date_posted": to_date(item.get("dateCreation")),
            "postal_code": dep_code,
            "city": city,
            "latitude": latitude,
            "longitude": longitude,
            "skills_hard_required": r_sk,
            "skills_hard_optional": o_sk,
            "skills_soft": [
                q.get("libelle")
                for q in item.get("qualitesProfessionnelles", [])
            ],
            "languages_required": r_lg,
            "languages_optional": o_lg,
        })

    return pd.DataFrame(rows)


# ==================================================
# Ingestion PostgreSQL
# ==================================================

def ingest_ft_to_postgres(
    keywords: str,
    location: str | None = None,
    contract_type: str | None = None,
    max_results: int = 600,
):
    token = get_ft_access_token()
    raw_items = fetch_all_ft_offers(
        token=token,
        keywords=keywords,
        location=location,
        contract_type=contract_type,
        max_results=max_results,
    )

    if not raw_items:
        return

    df = preprocess_ft(raw_items)
    conn = get_connection()

    try:
        for _, row in df.iterrows():
            company_name = row["company"] or "Unknown"
            company_id = get_or_create_company(conn, company_name)

            industry_id = get_or_create_industry(conn, row["industry"])

            contract_id = get_or_create_contract(conn, row["contract"])

            city = row["city"] if row["city"] else "Inconnue"
            postal_code = row["postal_code"] if row["postal_code"] else "00"

            location_id = get_or_create_location(
                conn,
                city=city,
                postal_code=postal_code,
                latitude=row["latitude"],
                longitude=row["longitude"],
            )

            job_offer_id = get_or_create_job_offer(
                conn,
                {
                    "company_id": company_id,
                    "url": row["url"],
                    "title": row["title"],
                    "description": row["description"],
                    "location_id": location_id,
                    "contract_id": contract_id,
                    "salary_min_annual": row["salary_min_annual"],
                    "salary_max_annual": row["salary_max_annual"],
                    "date_posted": row["date_posted"],
                    "industry_id": industry_id,
                    "experience": row["experience"],
                    "education": row["education"],
                },
            )

            for skill in row["skills_hard_required"]:
                sid = get_or_create_skill(conn, skill, "hard")
                link_job_offer_skill(conn, job_offer_id, sid, "required")

            for skill in row["skills_hard_optional"]:
                sid = get_or_create_skill(conn, skill, "hard")
                link_job_offer_skill(conn, job_offer_id, sid, "optional")
            for skill in row["skills_soft"]:
                sid = get_or_create_skill(conn, skill, "soft")
                link_job_offer_skill(conn, job_offer_id, sid, "required")

            for lang in row["languages_required"]:
                sid = get_or_create_skill(conn, lang, "language")
                link_job_offer_skill(conn, job_offer_id, sid, "required")

            for lang in row["languages_optional"]:
                sid = get_or_create_skill(conn, lang, "language")
                link_job_offer_skill(conn, job_offer_id, sid, "optional")
        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# ==================================================
# CLI
# ==================================================

if __name__ == "__main__":
    ingest_ft_to_postgres(
        keywords="data analyst",
        max_results=settings.FT_MAX_RESULTS,
    )
