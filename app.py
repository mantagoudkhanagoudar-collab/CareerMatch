import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from dotenv import load_dotenv

from database import (
    get_db_connection,
    create_database
)

from matching import calculate_match

from resume_service import analyze_resume

from adzuna_service import search_adzuna_jobs


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv(override=True)


# ==================================================
# FLASK APP
# ==================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "careermatch-secret-key"
)


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==================================================
# REGISTER
# ==================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            "job_seeker"
        )

        if not name or not email or not password:

            flash(
                "Please fill all required fields.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        hashed_password = generate_password_hash(
            password
        )

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    hashed_password,
                    role
                )
            )

            connection.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except Exception as error:

            if "UNIQUE" in str(error).upper():

                flash(
                    "Email already registered.",
                    "danger"
                )

            else:

                flash(
                    "Registration failed.",
                    "danger"
                )

            return redirect(
                url_for("register")
            )

        finally:

            connection.close()

    return render_template(
        "register.html"
    )


# ==================================================
# LOGIN
# ==================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]

            flash(
                "Login successful!",
                "success"
            )

            if user["role"] == "recruiter":

                return redirect(
                    url_for("recruiter_dashboard")
                )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("home")
    )


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    skills = connection.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "dashboard.html",
        user=user,
        skills=skills
    )


# ==================================================
# PROFILE
# ==================================================

@app.route(
    "/profile",
    methods=["GET", "POST"]
)
def profile():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    if request.method == "POST":

        education = request.form.get(
            "education",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        experience = request.form.get(
            "experience",
            ""
        ).strip()

        connection.execute(
            """
            UPDATE users
            SET education = ?,
                location = ?,
                experience = ?
            WHERE id = ?
            """,
            (
                education,
                location,
                experience,
                session["user_id"]
            )
        )

        connection.commit()

        flash(
            "Profile updated successfully!",
            "success"
        )

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    skills = connection.execute(
        """
        SELECT *
        FROM skills
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "profile.html",
        user=user,
        skills=skills
    )


# ==================================================
# ADD SKILL
# ==================================================

@app.route(
    "/add_skill",
    methods=["POST"]
)
def add_skill():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    skill_name = request.form.get(
        "skill_name",
        ""
    ).strip()

    if not skill_name:

        flash(
            "Please enter a skill.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO skills
        (
            user_id,
            skill_name
        )
        VALUES (?, ?)
        """,
        (
            session["user_id"],
            skill_name
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Skill added successfully!",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# ==================================================
# DELETE SKILL
# ==================================================

@app.route(
    "/delete_skill/<int:skill_id>"
)
def delete_skill(skill_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    connection.execute(
        """
        DELETE FROM skills
        WHERE id = ?
        AND user_id = ?
        """,
        (
            skill_id,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Skill deleted.",
        "success"
    )

    return redirect(
        url_for("profile")
    )


# ==================================================
# RESUME UPLOAD
# ==================================================

@app.route(
    "/upload_resume",
    methods=["POST"]
)
def upload_resume():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    resume = request.files.get(
        "resume"
    )

    if not resume:

        flash(
            "Please select a resume.",
            "danger"
        )

        return redirect(
            url_for("profile")
        )

    upload_folder = os.path.join(
        app.root_path,
        "uploads"
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    filename = resume.filename

    filepath = os.path.join(
        upload_folder,
        filename
    )

    resume.save(filepath)

    try:

        analysis = analyze_resume(
            filepath
        )

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE users
            SET resume_filename = ?
            WHERE id = ?
            """,
            (
                filename,
                session["user_id"]
            )
        )

        connection.commit()

        detected_skills = analysis.get(
            "skills",
            []
        )

        for skill in detected_skills:

            existing = connection.execute(
                """
                SELECT id
                FROM skills
                WHERE user_id = ?
                AND LOWER(skill_name) = LOWER(?)
                """,
                (
                    session["user_id"],
                    skill
                )
            ).fetchone()

            if not existing:

                connection.execute(
                    """
                    INSERT INTO skills
                    (
                        user_id,
                        skill_name
                    )
                    VALUES (?, ?)
                    """,
                    (
                        session["user_id"],
                        skill
                    )
                )

        connection.commit()
        connection.close()

        session["resume_analysis"] = analysis

        flash(
            "Resume uploaded and analyzed successfully!",
            "success"
        )

    except Exception as error:

        flash(
            f"Resume analysis failed: {error}",
            "danger"
        )

    return redirect(
        url_for("profile")
    )


# ==================================================
# JOB SEARCH
# ==================================================

@app.route("/jobs")
def jobs():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    search = request.args.get(
        "search",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    job_type = request.args.get(
        "job_type",
        ""
    ).strip()

    min_match = request.args.get(
        "min_match",
        ""
    ).strip()

    connection = get_db_connection()

    skills = connection.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    candidate_skills = [
        skill["skill_name"]
        for skill in skills
    ]

    query = """
        SELECT *
        FROM jobs
        WHERE 1 = 1
    """

    params = []

    if search:

        query += """
            AND (
                LOWER(title) LIKE LOWER(?)
                OR LOWER(company) LIKE LOWER(?)
                OR LOWER(required_skills) LIKE LOWER(?)
            )
        """

        search_value = f"%{search}%"

        params.extend(
            [
                search_value,
                search_value,
                search_value
            ]
        )

    if location:

        query += """
            AND LOWER(location) LIKE LOWER(?)
        """

        params.append(
            f"%{location}%"
        )

    if job_type:

        query += """
            AND job_type = ?
        """

        params.append(
            job_type
        )

    query += """
        ORDER BY created_at DESC
    """

    local_jobs = connection.execute(
        query,
        params
    ).fetchall()

    connection.close()

    jobs_with_match = []

    for job in local_jobs:

        job_required_skills = [
            job["required_skills"]
        ]

        match_result = calculate_match(
            candidate_skills,
            job_required_skills
        )

        job_data = dict(job)

        job_data["match_score"] = match_result.get(
            "match_score",
            0
        )

        job_data["matched_skills"] = match_result.get(
            "matched_skills",
            []
        )

        job_data["missing_skills"] = match_result.get(
            "missing_skills",
            []
        )

        job_data["recommended_skills"] = match_result.get(
            "recommended_skills",
            []
        )

        jobs_with_match.append(
            job_data
        )

    if min_match:

        try:

            minimum_score = int(
                min_match
            )

            jobs_with_match = [
                job
                for job in jobs_with_match
                if job["match_score"] >= minimum_score
            ]

        except ValueError:

            pass

    jobs_with_match.sort(
        key=lambda job: job["match_score"],
        reverse=True
    )

    return render_template(
        "jobs.html",
        jobs=jobs_with_match,
        search=search,
        location=location,
        job_type=job_type,
        min_match=min_match
    )


# ==================================================
# JOB DETAILS
# ==================================================

@app.route(
    "/job/<int:job_id>"
)
def job_details(job_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    job = connection.execute(
        """
        SELECT jobs.*,
               users.name AS recruiter_name
        FROM jobs
        JOIN users
        ON jobs.recruiter_id = users.id
        WHERE jobs.id = ?
        """,
        (job_id,)
    ).fetchone()

    connection.close()

    if not job:

        flash(
            "Job not found.",
            "danger"
        )

        return redirect(
            url_for("jobs")
        )

    return render_template(
        "job_details.html",
        job=job
    )


# ==================================================
# APPLY FOR JOB
# ==================================================

@app.route(
    "/apply/<int:job_id>",
    methods=["POST"]
)
def apply_job(job_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    try:

        connection.execute(
            """
            INSERT INTO applications
            (
                job_id,
                user_id
            )
            VALUES (?, ?)
            """,
            (
                job_id,
                session["user_id"]
            )
        )

        connection.commit()

        flash(
            "Application submitted successfully!",
            "success"
        )

    except Exception as error:

        if "UNIQUE" in str(error).upper():

            flash(
                "You have already applied for this job.",
                "warning"
            )

        else:

            flash(
                "Could not submit application.",
                "danger"
            )

    finally:

        connection.close()

    return redirect(
        url_for(
            "job_details",
            job_id=job_id
        )
    )


# ==================================================
# MY APPLICATIONS
# ==================================================

@app.route(
    "/applications"
)
def applications():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    applications_data = connection.execute(
        """
        SELECT
            applications.*,
            jobs.title,
            jobs.company,
            jobs.location,
            jobs.salary,
            jobs.job_type
        FROM applications
        JOIN jobs
        ON applications.job_id = jobs.id
        WHERE applications.user_id = ?
        ORDER BY applications.applied_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "applications.html",
        applications=applications_data
    )


# ==================================================
# RECRUITER DASHBOARD
# ==================================================

@app.route(
    "/recruiter/dashboard"
)
def recruiter_dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "recruiter":

        flash(
            "Recruiter access required.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    connection = get_db_connection()

    jobs_data = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE recruiter_id = ?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "recruiter_dashboard.html",
        jobs=jobs_data
    )


# ==================================================
# CREATE JOB
# ==================================================

@app.route(
    "/recruiter/create-job",
    methods=["GET", "POST"]
)
def create_job():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "recruiter":

        flash(
            "Recruiter access required.",
            "danger"
        )

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        company = request.form.get(
            "company",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        required_skills = request.form.get(
            "required_skills",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        salary = request.form.get(
            "salary",
            ""
        ).strip()

        job_type = request.form.get(
            "job_type",
            "Full Time"
        ).strip()

        if not title or not company or not description:

            flash(
                "Please fill all required fields.",
                "danger"
            )

            return redirect(
                url_for("create_job")
            )

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO jobs
            (
                recruiter_id,
                title,
                company,
                description,
                required_skills,
                location,
                salary,
                job_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                title,
                company,
                description,
                required_skills,
                location,
                salary,
                job_type
            )
        )

        connection.commit()
        connection.close()

        flash(
            "Job created successfully!",
            "success"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )

    return render_template(
        "create_job.html"
    )


# ==================================================
# RECRUITER APPLICANTS
# ==================================================

@app.route(
    "/recruiter/job/<int:job_id>/applicants"
)
def applicants(job_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "recruiter":

        return redirect(
            url_for("dashboard")
        )

    connection = get_db_connection()

    job = connection.execute(
        """
        SELECT *
        FROM jobs
        WHERE id = ?
        AND recruiter_id = ?
        """,
        (
            job_id,
            session["user_id"]
        )
    ).fetchone()

    if not job:

        connection.close()

        flash(
            "Job not found.",
            "danger"
        )

        return redirect(
            url_for("recruiter_dashboard")
        )

    applicants_data = connection.execute(
        """
        SELECT
            applications.id AS application_id,
            applications.status,
            applications.applied_at,
            users.id AS user_id,
            users.name,
            users.email,
            users.education,
            users.location,
            users.experience,
            users.resume_filename
        FROM applications
        JOIN users
        ON applications.user_id = users.id
        WHERE applications.job_id = ?
        ORDER BY applications.applied_at DESC
        """,
        (job_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "applicants.html",
        job=job,
        applicants=applicants_data
    )


# ==================================================
# UPDATE APPLICATION STATUS
# ==================================================

@app.route(
    "/recruiter/application/<int:application_id>/status",
    methods=["POST"]
)
def update_application_status(
    application_id
):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    if session.get("user_role") != "recruiter":

        return redirect(
            url_for("dashboard")
        )

    status = request.form.get(
        "status",
        "Applied"
    )

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE applications
        SET status = ?
        WHERE id = ?
        AND job_id IN (
            SELECT id
            FROM jobs
            WHERE recruiter_id = ?
        )
        """,
        (
            status,
            application_id,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Application status updated.",
        "success"
    )

    return redirect(
        request.referrer
        or url_for("recruiter_dashboard")
    )


# ==================================================
# ADZUNA LIVE JOB API
# ==================================================

@app.route(
    "/api/adzuna/jobs"
)
def api_adzuna_jobs():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Login required."
        }), 401

    keyword = request.args.get(
        "search",
        "python"
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    try:

        page = int(
            request.args.get(
                "page",
                1
            )
        )

    except ValueError:

        page = 1

    # --------------------------------------------------
    # GET CANDIDATE SKILLS
    # --------------------------------------------------

    connection = get_db_connection()

    skills = connection.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    candidate_skills = [
        skill["skill_name"]
        for skill in skills
    ]

    # --------------------------------------------------
    # SEARCH ADZUNA
    # --------------------------------------------------

    try:

        result = search_adzuna_jobs(
            keyword=keyword,
            location=location,
            page=page,
            results_per_page=10
        )

        jobs = result.get(
            "jobs",
            []
        )

        # --------------------------------------------------
        # CALCULATE MATCH USING EXTRACTED SKILLS
        # --------------------------------------------------

        for job in jobs:

            required_skills = job.get(
                "required_skills",
                []
            )

            # Safety fallback
            if not required_skills:

                required_skills = [
                    keyword
                ]

            match_result = calculate_match(
                candidate_skills,
                required_skills
            )

            job["match_score"] = match_result.get(
                "match_score",
                0
            )

            job["matched_skills"] = match_result.get(
                "matched_skills",
                []
            )

            job["missing_skills"] = match_result.get(
                "missing_skills",
                []
            )

            job["recommended_skills"] = match_result.get(
                "recommended_skills",
                []
            )

        return jsonify({
            "success": True,
            "source": "Adzuna",
            "search": keyword,
            "location": location,
            "page": page,
            "count": result.get(
                "count",
                0
            ),
            "mean_salary": result.get(
                "mean"
            ),
            "jobs": jobs
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


# ==================================================
# API AUTHENTICATION PLACEHOLDER
# ==================================================

def api_authentication():

    return None


# ==================================================
# ERROR HANDLERS
# ==================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html"
    ), 404


# ==================================================
# START APPLICATION
# ==================================================

if __name__ == "__main__":

    create_database()

    app.run(
        debug=True
    )