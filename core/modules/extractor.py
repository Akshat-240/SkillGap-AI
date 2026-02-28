import pypdf
import json
import time

PDF_DEBUG_LOG_PATH = r"c:\Users\aksha\Desktop\SG_AI\debug-aedf66.log"


def _write_debug_log(
    hypothesis_id: str, message: str, data: dict, run_id: str = "initial"
):
    # region agent log
    try:
        payload = {
            "sessionId": "aedf66",
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "location": "core/modules/extractor.py",
            "message": message,
            "data": data,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
        }
        with open(PDF_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        # Logging must never break main logic
        pass
    # endregion


def extract_text_from_pdf(file_path):  # Function to extract text from a PDF file
    _write_debug_log(
        hypothesis_id="H4",
        message="extract_text_from_pdf called",
        data={"file_path": file_path},
    )
    text = ""
    try:
        with open(file_path, "rb") as file:  # read as binary
            reader = pypdf.PdfReader(file)

            for page_index, page in enumerate(reader.pages):
                page_text = page.extract_text()
                _write_debug_log(
                    hypothesis_id="H4",
                    message="page_extracted",
                    data={"page_index": page_index, "has_text": bool(page_text)},
                )
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            print("No text found in the PDF.")

        _write_debug_log(
            hypothesis_id="H4",
            message="extract_text_from_pdf completed",
            data={"text_length": len(text)},
        )
        return text

    except FileNotFoundError:
        _write_debug_log(
            hypothesis_id="H4",
            message="extract_text_from_pdf file_not_found",
            data={"file_path": file_path},
        )
        return "Error: The file was not found at the specified path."

    except Exception as e:
        _write_debug_log(
            hypothesis_id="H4",
            message="extract_text_from_pdf exception",
            data={"error": str(e)},
        )
        return f"Error processing PDF: {str(e)}"
