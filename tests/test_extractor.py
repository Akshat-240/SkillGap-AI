import pypdf
import os


# ---  Extraction Function ---
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            print("No text found in the PDF.")

        return text

    except FileNotFoundError:
        return "Error: The file was not found at the specified path."
    except Exception as e:
        return f"Error processing PDF: {str(e)}"


def test_extractor_script():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    test_filename = os.path.join(script_directory, "my_notes.pdf")

    print(f"\n--- Extracting Text from: {test_filename} ---")

    # 3. Run the extractor
    result = extract_text_from_pdf(test_filename)
    print(result)
