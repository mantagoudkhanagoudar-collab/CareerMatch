import os
import requests
from dotenv import load_dotenv

from matching import extract_skills_from_text


# Load .env
load_dotenv(override=True)


def search_adzuna_jobs(
    keyword="python",
    location="",
    page=1,
    results_per_page=10
):
    """
    Search jobs from the Adzuna API
    and extract required skills from
    the job title and description.
    """

    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    country = os.getenv("ADZUNA_COUNTRY", "in")

    if not app_id or not app_key:
        raise ValueError(
            "Adzuna API credentials are missing."
        )

    url = (
        f"https://api.adzuna.com/v1/api/jobs/"
        f"{country}/search/{page}"
    )

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": results_per_page,
        "what": keyword,
        "content-type": "application/json"
    }

    if location:
        params["where"] = location

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    jobs = []

    for job in data.get("results", []):

        title = job.get("title", "")
        description = job.get("description", "")

        # -------------------------------------------------
        # Combine title + description
        # -------------------------------------------------

        full_job_text = f"{title} {description}"

        # -------------------------------------------------
        # Extract skills from the complete job
        # -------------------------------------------------

        required_skills = extract_skills_from_text(
            full_job_text
        )

        jobs.append({
            "adzuna_id": job.get("id"),

            "title": title,

            "company": job.get(
                "company", {}
            ).get(
                "display_name", ""
            ),

            "location": job.get(
                "location", {}
            ).get(
                "display_name", ""
            ),

            "description": description,

            "required_skills": required_skills,

            "salary_min": job.get(
                "salary_min"
            ),

            "salary_max": job.get(
                "salary_max"
            ),

            "contract_type": job.get(
                "contract_type", ""
            ),

            "redirect_url": job.get(
                "redirect_url", ""
            ),

            "created": job.get(
                "created", ""
            )
        })

    return {
        "jobs": jobs,
        "count": data.get("count", 0),
        "mean": data.get("mean")
    }