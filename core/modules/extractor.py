import json
import time
from pathlib import Path

import pypdf

PDF_DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / "debug-aedf66.log"


class PDFExtractionError(Exception):
    pass


def _write_debug_log(
    hypothesis_id: str, message: str, data: dict, run_id: str = "initial"
):
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
        with PDF_DEBUG_LOG_PATH.open("a", encoding="utf-8") as file_obj:
            file_obj.write(json.dumps(payload) + "\n")
    except Exception:
        # Logging must never break main logic.
        pass


def extract_text_from_pdf(file_path):
    _write_debug_log(
        hypothesis_id="H4",
        message="extract_text_from_pdf called",
        data={"file_path": str(file_path)},
    )

    text = ""
    path = Path(file_path)

    try:
        with path.open("rb") as file_obj:
            reader = pypdf.PdfReader(file_obj)

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
            raise PDFExtractionError(
                "No extractable text was found in the uploaded PDF."
            )

        _write_debug_log(
            hypothesis_id="H4",
            message="extract_text_from_pdf completed",
            data={"text_length": len(text)},
        )
        return text

    except FileNotFoundError as exc:
        _write_debug_log(
            hypothesis_id="H4",
            message="extract_text_from_pdf file_not_found",
            data={"file_path": str(file_path)},
        )
        raise PDFExtractionError("The uploaded PDF could not be found.") from exc
    except pypdf.errors.PyPdfError as exc:
        _write_debug_log(
            hypothesis_id="H4",
            message="extract_text_from_pdf pdf_error",
            data={"error": str(exc)},
        )
        raise PDFExtractionError(
            "The uploaded file is not a readable PDF document."
        ) from exc
    except PDFExtractionError:
        raise
    except Exception as exc:
        _write_debug_log(
            hypothesis_id="H4",
            message="extract_text_from_pdf exception",
            data={"error": str(exc)},
        )
        raise PDFExtractionError(
            "Something went wrong while processing the uploaded PDF."
        ) from exc
