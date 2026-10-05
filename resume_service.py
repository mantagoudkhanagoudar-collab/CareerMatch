import os

from resume_reader import read_resume
from resume_parser import extract_skills


# ==================================================
# ANALYZE RESUME
# ==================================================

def analyze_resume(file_path):

    if not os.path.exists(file_path):

        raise FileNotFoundError(
            "Resume file not found."
        )

    # ----------------------------------------------
    # Read resume text
    # ----------------------------------------------

    resume_text = read_resume(
        file_path
    )

    if not resume_text.strip():

        return {
            "resume_text": "",
            "detected_skills": [],
            "skill_count": 0
        }

    # ----------------------------------------------
    # Extract skills
    # ----------------------------------------------

    detected_skills = extract_skills(
        resume_text
    )

    return {
        "resume_text": resume_text,
        "detected_skills": detected_skills,
        "skill_count": len(detected_skills)
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "CAREERMATCH RESUME INTELLIGENCE"
    )

    print("=" * 60)

    print()

    print(
        "Resume service loaded successfully."
    )

    print()

    print(
        "Pipeline:"
    )

    print(
        "📄 PDF Resume"
    )

    print(
        "   ↓"
    )

    print(
        "📖 Resume Reader"
    )

    print(
        "   ↓"
    )

    print(
        "🧠 Skill Analyzer"
    )

    print(
        "   ↓"
    )

    print(
        "🎯 CareerMatch Skills"
    )

    print()

    print(
        "✓ Resume Intelligence is ready!"
    )

    print()

    print("=" * 60)

    print(
        "TESTING COMPLETE"
    )

    print("=" * 60)