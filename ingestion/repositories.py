# ==================================================
# Company
# ==================================================

def get_or_create_company(conn, name: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM company
            WHERE name = %s
            """,
            (name,),
        )
        row = cur.fetchone()

        if row:
            return row[0]

        cur.execute(
            """
            INSERT INTO company (name)
            VALUES (%s)
            RETURNING id
            """,
            (name,),
        )
        return cur.fetchone()[0]


# ==================================================
# Job offer
# ==================================================

def get_or_create_job_offer(conn, data: dict) -> int:
    with conn.cursor() as cur:
        # 1. Check existence (unicité par URL)
        cur.execute(
            """
            SELECT id
            FROM job_offer
            WHERE url = %s
            """,
            (data["url"],),
        )
        row = cur.fetchone()

        # 2. UPDATE si existe
        if row:
            job_offer_id = row[0]
            cur.execute(
                """
                UPDATE job_offer
                SET
                    title = %s,
                    description = %s,
                    salary_min_annual = %s,
                    salary_max_annual = %s,
                    experience = %s,
                    education = %s,
                    date_posted = %s,
                    company_id = %s,
                    contract_id = %s,
                    industry_id = %s,
                    location_id = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (
                    data["title"],
                    data["description"],
                    data["salary_min_annual"],
                    data["salary_max_annual"],
                    data["experience"],
                    data["education"],
                    data["date_posted"],
                    data.get("company_id"),
                    data.get("contract_id"),
                    data.get("industry_id"),
                    data.get("location_id"),
                    job_offer_id,
                ),
            )
            return job_offer_id

        # 3. INSERT si nouveau
        cur.execute(
            """
            INSERT INTO job_offer (
                title,
                description,
                salary_min_annual,
                salary_max_annual,
                experience,
                education,
                date_posted,
                url,
                company_id,
                contract_id,
                industry_id,
                location_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                data["title"],
                data["description"],
                data["salary_min_annual"],
                data["salary_max_annual"],
                data["experience"],
                data["education"],
                data["date_posted"],
                data["url"],
                data.get("company_id"),
                data.get("contract_id"),
                data.get("industry_id"),
                data.get("location_id"),
            ),
        )
        return cur.fetchone()[0]
    
# ==================================================
# Skills
# ==================================================

def get_or_create_skill(conn, name: str, category: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM skill
            WHERE name = %s AND category = %s
            """,
            (name, category),
        )
        row = cur.fetchone()

        if row:
            return row[0]

        cur.execute(
            """
            INSERT INTO skill (name, category)
            VALUES (%s, %s)
            RETURNING id
            """,
            (name, category),
        )
        return cur.fetchone()[0]


def link_job_offer_skill(
    conn,
    job_offer_id: int,
    skill_id: int,
    requirement_level: str,
):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO job_offer_skill (
                job_offer_id,
                skill_id,
                requirement_level
            )
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (job_offer_id, skill_id, requirement_level),
        )

# ==================================================
# Location
# ==================================================

def get_or_create_location(
    conn,
    city: str | None,
    postal_code: str | None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> int:
    with conn.cursor() as cur:
        # 1. Check existence
        cur.execute(
            """
            SELECT id
            FROM location
            WHERE ville = %s AND code_postal = %s
            """,
            (city, postal_code),
        )
        row = cur.fetchone()

        if row:
            return row[0]

        # 2. Insert new location
        cur.execute(
            """
            INSERT INTO location (
                ville,
                code_postal,
                latitude,
                longitude
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (city, postal_code, latitude, longitude),
        )
        return cur.fetchone()[0]
    
# ==================================================
# Industry
# ==================================================

def get_or_create_industry(conn, name: str | None) -> int | None:
    if not name:
        return None

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM industry
            WHERE name = %s
            """,
            (name,),
        )
        row = cur.fetchone()

        if row:
            return row[0]

        cur.execute(
            """
            INSERT INTO industry (name)
            VALUES (%s)
            RETURNING id
            """,
            (name,),
        )
        return cur.fetchone()[0]
    
# ==================================================
# Contract
# ==================================================

def get_or_create_contract(conn, label: str | None) -> int | None:
    if not label:
        return None

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id
            FROM contract
            WHERE type_contrat = %s
            """,
            (label,),
        )
        row = cur.fetchone()

        if row:
            return row[0]

        cur.execute(
            """
            INSERT INTO contract (type_contrat)
            VALUES (%s)
            RETURNING id
            """,
            (label,),
        )
        return cur.fetchone()[0]