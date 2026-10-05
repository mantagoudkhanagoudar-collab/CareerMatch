import re


# =========================================================
# SKILL ALIASES
# =========================================================

SKILL_ALIASES = {
    "python3": "python",
    "python 3": "python",

    "java programming": "java",

    "javascript": "javascript",
    "java script": "javascript",
    "js": "javascript",

    "typescript": "typescript",
    "ts": "typescript",

    "html5": "html",
    "html 5": "html",

    "css3": "css",
    "css 3": "css",

    "reactjs": "react",
    "react.js": "react",
    "react js": "react",

    "nodejs": "node",
    "node.js": "node",
    "node js": "node",

    "expressjs": "express",
    "express.js": "express",

    "nextjs": "next",
    "next.js": "next",

    "vuejs": "vue",
    "vue.js": "vue",

    "angularjs": "angular",
    "angular.js": "angular",

    "num py": "numpy",

    "postgres": "postgresql",
    "postgresql": "postgresql",

    "mysql database": "mysql",

    "mongodb database": "mongodb",
    "mongo db": "mongodb",

    "amazon web services": "aws",

    "git version control": "git",
    "github": "github",

    "machine learning": "machine learning",
    "ml": "machine learning",

    "artificial intelligence": "artificial intelligence",
    "ai": "artificial intelligence",

    "deep learning": "deep learning",
    "dl": "deep learning",

    "c programming": "c",
    "c language": "c",

    "c++ programming": "c++ programming",

    "c sharp": "c#",
    "c-sharp": "c#",

    "sql database": "sql",

    "power bi": "power bi",

    "rest api": "rest api",
    "restful api": "rest api",

    "pyspark": "pyspark",

    "spark": "spark",

    "flask": "flask",
    "django": "django",
    "fastapi": "fastapi",

    "docker": "docker",
    "kubernetes": "kubernetes",
    "jenkins": "jenkins",

    "linux": "linux",

    "gitlab": "gitlab",

    "firebase": "firebase",

    "oracle": "oracle",

    "sqlite": "sqlite",

    "sql server": "sql server",

    "redis": "redis",

    "aws": "aws",
    "azure": "azure",
    "gcp": "gcp",
}


# =========================================================
# IMPORTANT SKILLS
# =========================================================

KNOWN_SKILLS = [
    "python",
    "java",
    "javascript",
    "typescript",

    "html",
    "css",

    "react",
    "node",
    "express",
    "next",
    "vue",
    "angular",

    "flask",
    "django",
    "fastapi",

    "numpy",
    "pandas",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "sqlite",
    "sql server",
    "oracle",
    "redis",

    "power bi",

    "machine learning",
    "artificial intelligence",
    "deep learning",

    "c++",
    "c#",

    "git",
    "github",
    "gitlab",

    "docker",
    "kubernetes",
    "jenkins",

    "linux",

    "rest api",

    "firebase",

    "aws",
    "azure",
    "gcp",

    "spark",
    "pyspark",
]


# =========================================================
# NORMALIZE SKILL
# =========================================================

def normalize_skill(skill):

    skill = skill.strip().lower()

    skill = re.sub(r"\s+", " ", skill)

    return SKILL_ALIASES.get(skill, skill)


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(skills):

    result = []
    seen = set()

    for skill in skills:

        skill = normalize_skill(skill)

        if not skill:
            continue

        if skill not in seen:

            seen.add(skill)
            result.append(skill)

    return result


# =========================================================
# EXTRACT SKILLS FROM TEXT
# =========================================================

def extract_skills_from_text(text):

    if not text:
        return []

    text = text.lower()

    found = []

    # Check longer skills first
    skills_sorted = sorted(
        KNOWN_SKILLS,
        key=len,
        reverse=True
    )

    for skill in skills_sorted:

        pattern = (
            r"(?<![a-zA-Z0-9+#])"
            + re.escape(skill)
            + r"(?![a-zA-Z0-9+#])"
        )

        if re.search(pattern, text):

            normalized = normalize_skill(skill)

            if normalized not in found:

                found.append(normalized)

    return found


# =========================================================
# DETECT LONG JOB DESCRIPTION
# =========================================================

def is_job_description(text):

    if not text:
        return False

    text_lower = text.lower()

    indicators = [
        "job description",
        "responsibilities",
        "qualification",
        "qualifications",
        "requirements",
        "experience",
        "candidate",
        "we are looking",
        "about the job",
        "what you will do",
        "role",
        "developer",
        "engineer",
    ]

    if len(text) > 150:
        return True

    for word in indicators:

        if word in text_lower:
            return True

    return False


# =========================================================
# PARSE REQUIRED SKILLS
# =========================================================

def parse_required_skills(required_skills):

    groups = []

    if not required_skills:
        return groups

    if isinstance(required_skills, str):
        required_skills = [required_skills]

    for item in required_skills:

        if not item:
            continue

        item = str(item).strip()

        if not item:
            continue

        # -------------------------------------------------
        # FULL JOB DESCRIPTION
        # -------------------------------------------------

        if is_job_description(item):

            extracted = extract_skills_from_text(item)

            for skill in extracted:

                if [skill] not in groups:

                    groups.append([skill])

            continue

        # -------------------------------------------------
        # NORMAL SKILL LIST
        # -------------------------------------------------

        parts = item.split(",")

        for part in parts:

            part = part.strip()

            if not part:
                continue

            # -------------------------------------------------
            # Alternative skills
            # Example: Python/Java
            # -------------------------------------------------

            if "/" in part:

                alternatives = []

                for value in part.split("/"):

                    value = value.strip()

                    if value:

                        value = normalize_skill(value)

                        if value not in alternatives:

                            alternatives.append(value)

                if alternatives:

                    groups.append(alternatives)

            else:

                normalized = normalize_skill(part)

                if normalized:

                    groups.append([normalized])

    return groups


# =========================================================
# CALCULATE MATCH
# =========================================================

def calculate_match(candidate_skills, required_skills):

    candidate_skills = remove_duplicates(candidate_skills)

    candidate_set = set(candidate_skills)

    groups = parse_required_skills(required_skills)

    if not groups:

        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "recommended_skills": []
        }

    matched = []
    missing = []

    for group in groups:

        found = None

        for skill in group:

            if skill in candidate_set:

                found = skill
                break

        if found:

            matched.append(found)

        else:

            if len(group) > 1:

                missing.append(" / ".join(group))

            else:

                missing.append(group[0])

    total = len(groups)

    score = round(
        (len(matched) / total) * 100
    )

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recommended_skills": missing.copy()
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("\nTEST 1")

    print(
        calculate_match(
            ["python", "flask", "sql", "git"],
            ["python", "flask", "sql", "git"]
        )
    )


    print("\nTEST 2")

    print(
        calculate_match(
            ["python"],
            ["python/java", "react", "numpy"]
        )
    )


    print("\nTEST 3 - ADZUNA")

    description = """
    We are looking for a Python Developer.

    The candidate should have experience with
    Python, Flask, SQL, PostgreSQL, Docker and AWS.

    Experience with REST API development is required.
    """

    print(
        calculate_match(
            ["python", "flask", "sql", "git"],
            [description]
        )
    )