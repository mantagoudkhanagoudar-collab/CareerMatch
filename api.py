from flask import Blueprint, jsonify, session

from database import get_db_connection
from matching import calculate_match


api = Blueprint(
    "api",
    __name__,
    url_prefix="/api"
)


# ==================================================
# API: GET ALL JOBS
# ==================================================

@api.route("/jobs", methods=["GET"])
def get_jobs():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    connection = get_db_connection()

    jobs = connection.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY created_at DESC
        """
    ).fetchall()

    candidate_skill_rows = connection.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE user_id = ?
        ORDER BY id
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    candidate_skills = [
        row["skill_name"]
        for row in candidate_skill_rows
    ]

    result = []

    for job in jobs:

        required_skills = (
            job["required_skills"].split(",")
        )

        match_result = calculate_match(
            candidate_skills,
            required_skills
        )

        result.append({

            "id": job["id"],

            "title": job["title"],

            "company": job["company"],

            "description": job["description"],

            "required_skills": required_skills,

            "location": job["location"],

            "salary": job["salary"],

            "job_type": job["job_type"],

            "created_at": job["created_at"],

            "match": match_result

        })

    return jsonify({

        "success": True,

        "count": len(result),

        "jobs": result

    })


# ==================================================
# API: GET SINGLE JOB
# ==================================================

@api.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    connection = get_db_connection()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        """,
        (job_id,)
    ).fetchone()

    candidate_skill_rows = connection.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE user_id = ?
        ORDER BY id
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    if not job:

        return jsonify({

            "success": False,

            "message": "Job not found."

        }), 404

    candidate_skills = [
        row["skill_name"]
        for row in candidate_skill_rows
    ]

    required_skills = (
        job["required_skills"].split(",")
    )

    match_result = calculate_match(
        candidate_skills,
        required_skills
    )

    return jsonify({

        "success": True,

        "job": {

            "id": job["id"],

            "title": job["title"],

            "company": job["company"],

            "description": job["description"],

            "required_skills": required_skills,

            "location": job["location"],

            "salary": job["salary"],

            "job_type": job["job_type"],

            "created_at": job["created_at"],

            "match": match_result

        }

    })


# ==================================================
# API: PROFILE
# ==================================================

@api.route("/profile", methods=["GET"])
def get_profile():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT
            id,
            name,
            email,
            role,
            education,
            location,
            experience,
            resume_filename
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    skills = connection.execute(
        """
        SELECT
            id,
            skill_name
        FROM skills
        WHERE user_id = ?
        ORDER BY id
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    if not user:

        return jsonify({

            "success": False,

            "message": "User not found."

        }), 404

    return jsonify({

        "success": True,

        "profile": {

            "id": user["id"],

            "name": user["name"],

            "email": user["email"],

            "role": user["role"],

            "education": user["education"],

            "location": user["location"],

            "experience": user["experience"],

            "resume_filename": user["resume_filename"],

            "skills": [
                skill["skill_name"]
                for skill in skills
            ]

        }

    })


# ==================================================
# API: APPLICATIONS
# ==================================================

@api.route("/applications", methods=["GET"])
def get_applications():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    connection = get_db_connection()

    applications = connection.execute(
        """
        SELECT
            applications.id,
            applications.job_id,
            applications.status,
            applications.applied_at,
            jobs.title,
            jobs.company,
            jobs.location,
            jobs.salary,
            jobs.job_type,
            jobs.required_skills
        FROM applications
        JOIN jobs
            ON applications.job_id = jobs.id
        WHERE applications.user_id = ?
        ORDER BY applications.applied_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    skills = connection.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE user_id = ?
        ORDER BY id
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    candidate_skills = [
        skill["skill_name"]
        for skill in skills
    ]

    result = []

    for application in applications:

        required_skills = (
            application["required_skills"].split(",")
        )

        match_result = calculate_match(
            candidate_skills,
            required_skills
        )

        result.append({

            "application_id": application["id"],

            "job_id": application["job_id"],

            "job_title": application["title"],

            "company": application["company"],

            "location": application["location"],

            "salary": application["salary"],

            "job_type": application["job_type"],

            "status": application["status"],

            "applied_at": application["applied_at"],

            "match": match_result

        })

    return jsonify({

        "success": True,

        "count": len(result),

        "applications": result

    })


# ==================================================
# API: RECOMMENDATIONS
# ==================================================

@api.route("/recommendations", methods=["GET"])
def get_recommendations():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    connection = get_db_connection()

    jobs = connection.execute(
        """
        SELECT *
        FROM jobs
        ORDER BY created_at DESC
        """
    ).fetchall()

    candidate_skill_rows = connection.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE user_id = ?
        ORDER BY id
        """,
        (session["user_id"],)
    ).fetchall()

    applied_jobs = connection.execute(
        """
        SELECT job_id
        FROM applications
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    candidate_skills = [
        row["skill_name"]
        for row in candidate_skill_rows
    ]

    applied_job_ids = {
        row["job_id"]
        for row in applied_jobs
    }

    recommendations = []

    for job in jobs:

        if job["id"] in applied_job_ids:

            continue

        required_skills = (
            job["required_skills"].split(",")
        )

        match_result = calculate_match(
            candidate_skills,
            required_skills
        )

        score = match_result["match_score"]

        if score >= 80:

            reason = (
                "Excellent skill match. "
                "This job strongly matches your profile."
            )

        elif score >= 60:

            reason = (
                "Good skill match. "
                "Learning the missing skills could improve your chances."
            )

        else:

            reason = (
                "Some skills match your profile. "
                "Consider this as a skill-building opportunity."
            )

        recommendations.append({

            "job": {

                "id": job["id"],

                "title": job["title"],

                "company": job["company"],

                "location": job["location"],

                "salary": job["salary"],

                "job_type": job["job_type"]

            },

            "match_score": score,

            "matched_skills":
                match_result["matched_skills"],

            "missing_skills":
                match_result["missing_skills"],

            "recommended_skills":
                match_result["recommended_skills"],

            "reason": reason

        })

    recommendations.sort(
        key=lambda item:
            item["match_score"],
        reverse=True
    )

    recommendations = recommendations[:5]

    return jsonify({

        "success": True,

        "count": len(recommendations),

        "recommendations": recommendations

    })