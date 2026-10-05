import os

from resume_service import analyze_resume


# ==================================================
# FIND PDF RESUME
# ==================================================

UPLOAD_FOLDER = "uploads"


def find_resume():

    if not os.path.exists(UPLOAD_FOLDER):

        print("uploads folder not found.")

        return None

    files = os.listdir(
        UPLOAD_FOLDER
    )

    pdf_files = [
        file
        for file in files
        if file.lower().endswith(".pdf")
    ]

    if not pdf_files:

        print(
            "No PDF resume found in uploads folder."
        )

        return None

    return os.path.join(
        UPLOAD_FOLDER,
        pdf_files[0]
    )


# ==================================================
# MAIN TEST
# ==================================================

print()

print("=" * 60)

print(
    "CAREERMATCH RESUME AI TEST"
)

print("=" * 60)

print()


resume_path = find_resume()


if resume_path:

    print(
        "Resume found:"
    )

    print(
        resume_path
    )

    print()

    try:

        result = analyze_resume(
            resume_path
        )

        print(
            "Resume successfully analyzed!"
        )

        print()

        print(
            "Detected Skills:"
        )

        print(
            "-" * 40
        )

        if result["detected_skills"]:

            for skill in result[
                "detected_skills"
            ]:

                print(
                    "✓",
                    skill
                )

        else:

            print(
                "No known skills detected."
            )

        print()

        print(
            "Total Skills Detected:",
            result["skill_count"]
        )

        print()

        print(
            "Extracted Resume Text:"
        )

        print(
            "-" * 40
        )

        print(
            result["resume_text"][:1000]
        )

        if len(
            result["resume_text"]
        ) > 1000:

            print(
                "\n... (text truncated for testing)"
            )

    except Exception as error:

        print(
            "Resume analysis failed."
        )

        print(
            "Error:",
            error
        )


print()

print("=" * 60)

print(
    "TEST COMPLETE"
)

print("=" * 60)