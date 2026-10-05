import re


# ==================================================
# SKILL DATABASE
# ==================================================

KNOWN_SKILLS = {

    "python": [
        "python",
        "python3",
        "python 3"
    ],

    "java": [
        "java"
    ],

    "c": [
        "c programming",
        "c language"
    ],

    "c++": [
        "c++",
        "cpp"
    ],

    "c#": [
        "c#",
        "c sharp",
        "c-sharp"
    ],

    "javascript": [
        "javascript",
        "java script",
        "js"
    ],

    "typescript": [
        "typescript",
        "ts"
    ],

    "html": [
        "html",
        "html5",
        "html 5"
    ],

    "css": [
        "css",
        "css3",
        "css 3"
    ],

    "react": [
        "react",
        "reactjs",
        "react.js",
        "react js"
    ],

    "node": [
        "node",
        "nodejs",
        "node.js",
        "node js"
    ],

    "express": [
        "express",
        "expressjs",
        "express.js"
    ],

    "flask": [
        "flask"
    ],

    "django": [
        "django"
    ],

    "sql": [
        "sql",
        "sql database"
    ],

    "mysql": [
        "mysql"
    ],

    "postgresql": [
        "postgresql",
        "postgres"
    ],

    "mongodb": [
        "mongodb",
        "mongo db"
    ],

    "numpy": [
        "numpy",
        "num py"
    ],

    "pandas": [
        "pandas"
    ],

    "matplotlib": [
        "matplotlib"
    ],

    "machine learning": [
        "machine learning",
        "ml"
    ],

    "deep learning": [
        "deep learning",
        "dl"
    ],

    "artificial intelligence": [
        "artificial intelligence",
        "ai"
    ],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "docker": [
        "docker"
    ],

    "git": [
        "git"
    ],

    "github": [
        "github"
    ],

    "rest api": [
        "rest api",
        "restful api",
        "rest apis"
    ],

    "api": [
        "api",
        "apis"
    ],

    "power bi": [
        "power bi",
        "powerbi"
    ],

    "tableau": [
        "tableau"
    ],

    "linux": [
        "linux"
    ],

    "azure": [
        "azure"
    ],

    "google cloud": [
        "google cloud",
        "gcp"
    ],

    "kubernetes": [
        "kubernetes",
        "k8s"
    ]
}


# ==================================================
# NORMALIZE TEXT
# ==================================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


# ==================================================
# EXTRACT SKILLS
# ==================================================

def extract_skills(resume_text):

    if not resume_text:

        return []

    normalized_text = normalize_text(
        resume_text
    )

    detected_skills = []

    for skill_name, variations in KNOWN_SKILLS.items():

        for variation in variations:

            variation = variation.lower()

            # ------------------------------------------
            # Word-boundary matching
            # ------------------------------------------

            pattern = (
                r"(?<![a-z0-9+#])"
                + re.escape(variation)
                + r"(?![a-z0-9+#])"
            )

            if re.search(
                pattern,
                normalized_text
            ):

                detected_skills.append(
                    skill_name
                )

                break

    return detected_skills


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "CAREERMATCH RESUME SKILL ANALYZER"
    )

    print("=" * 60)

    print()


    sample_resume = """
    Mahantagouda

    Computer Science Engineering Student

    Skills:
    Python, Flask, SQL, Git, GitHub,
    HTML, CSS, JavaScript, React,
    NumPy, Pandas

    Projects:
    Developed a Student Management System
    using Python, Flask and SQLite.

    Developed an Expense Tracker application
    using Flask and Python.

    Experience:
    Worked with REST API and AWS.
    """

    print(
        "Sample Resume:"
    )

    print(
        sample_resume
    )

    print()

    detected_skills = extract_skills(
        sample_resume
    )

    print(
        "Detected Skills:"
    )

    for skill in detected_skills:

        print(
            "✓",
            skill
        )

    print()

    print(
        "Total Skills Detected:",
        len(detected_skills)
    )

    print()

    print("=" * 60)

    print(
        "TESTING COMPLETE"
    )

    print("=" * 60)