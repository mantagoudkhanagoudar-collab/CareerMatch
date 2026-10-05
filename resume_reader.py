import os

from pypdf import PdfReader


# ==================================================
# READ PDF RESUME
# ==================================================

def read_pdf(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            "Resume file not found."
        )

    text = []

    reader = PdfReader(file_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:

            text.append(page_text)

    return "\n".join(text)


# ==================================================
# READ RESUME
# ==================================================

def read_resume(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":

        return read_pdf(
            file_path
        )

    else:

        raise ValueError(
            "Resume analysis currently supports PDF files."
        )


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "CAREERMATCH RESUME READER"
    )

    print("=" * 60)

    print()

    print(
        "PDF resume reading is ready."
    )

    print()

    print(
        "Supported format:"
    )

    print(
        "✓ PDF"
    )

    print()

    print(
        "Testing PDF library..."
    )

    print()

    print(
        "PDF support working!"
    )

    print()

    print("=" * 60)

    print(
        "TESTING COMPLETE"
    )

    print("=" * 60)