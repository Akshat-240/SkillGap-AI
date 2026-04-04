import json
import os
import time
from pathlib import Path

import mysql.connector

DB_DEBUG_LOG_PATH = Path(__file__).resolve().parents[2] / "debug-aedf66.log"
_last_connection_error = None


def _write_debug_log(
    hypothesis_id: str, message: str, data: dict, run_id: str = "initial"
):
    try:
        payload = {
            "sessionId": "aedf66",
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "location": "core/modules/database_manager.py",
            "message": message,
            "data": data,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
        }
        with DB_DEBUG_LOG_PATH.open("a", encoding="utf-8") as file_obj:
            file_obj.write(json.dumps(payload) + "\n")
    except Exception:
        # Logging must never break main logic.
        pass


def _db_config():
    return {
        "host": os.getenv("SG_AI_DB_HOST", "localhost"),
        "user": os.getenv("SG_AI_DB_USER", "root"),
        "password": os.getenv("SG_AI_DB_PASSWORD", "12345"),
        "database": os.getenv("SG_AI_DB_NAME", "sg_ai"),
    }


def get_connection():
    global _last_connection_error

    try:
        config = _db_config()
        connection = mysql.connector.connect(**config)
        _last_connection_error = None
        _write_debug_log(
            hypothesis_id="H0",
            message="db_connection_success",
            data={"host": config["host"], "database": config["database"]},
        )
        return connection
    except mysql.connector.Error as err:
        _last_connection_error = str(err)
        _write_debug_log(
            hypothesis_id="H0",
            message="db_connection_error",
            data={"error": _last_connection_error},
        )
        return None


def get_database_status():
    return _last_connection_error


def add_candidate_to_db(name, email, resume_text):
    connection = get_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    sql = "INSERT INTO candidates(name, email, resume_text) VALUES (%s, %s, %s)"
    values = (name, email, resume_text)

    _write_debug_log(
        hypothesis_id="H1",
        message="add_candidate_to_db called",
        data={"name": name, "email": email},
    )

    try:
        cursor.execute(sql, values)
        connection.commit()
        _write_debug_log(
            hypothesis_id="H1",
            message="add_candidate_to_db committed",
            data={"rowcount": cursor.rowcount},
        )
        return True
    except mysql.connector.Error as err:
        _write_debug_log(
            hypothesis_id="H1",
            message="add_candidate_to_db error",
            data={"error": str(err)},
        )
        return False
    finally:
        cursor.close()
        connection.close()


def add_job_to_db(title, company, description_text):
    connection = get_connection()
    if connection is None:
        return False

    cursor = connection.cursor()
    sql = "INSERT INTO jobs (title, company, description_text) VALUES (%s, %s, %s)"
    values = (title, company, description_text)

    _write_debug_log(
        hypothesis_id="H3",
        message="add_job_to_db called",
        data={"title": title, "company": company},
    )

    try:
        cursor.execute(sql, values)
        connection.commit()
        _write_debug_log(
            hypothesis_id="H3",
            message="add_job_to_db committed",
            data={"rowcount": cursor.rowcount},
        )
        return True
    except mysql.connector.Error as err:
        _write_debug_log(
            hypothesis_id="H3",
            message="add_job_to_db error",
            data={"error": str(err)},
        )
        return False
    finally:
        cursor.close()
        connection.close()


def get_all_jobs():
    connection = get_connection()
    if connection is None:
        return []

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, title, company FROM jobs ORDER BY title ASC")
        jobs = cursor.fetchall()
        return [{"id": row[0], "title": row[1], "company": row[2]} for row in jobs]
    except mysql.connector.Error as err:
        _write_debug_log(
            hypothesis_id="H5",
            message="get_all_jobs error",
            data={"error": str(err)},
        )
        return []
    finally:
        cursor.close()
        connection.close()


def get_job_by_id(job_id):
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT title, description_text FROM jobs WHERE id = %s",
            (job_id,),
        )
        job = cursor.fetchone()
        if job:
            return {"title": job[0], "description_text": job[1]}
        return None
    except mysql.connector.Error as err:
        _write_debug_log(
            hypothesis_id="H6",
            message="get_job_by_id error",
            data={"error": str(err), "job_id": job_id},
        )
        return None
    finally:
        cursor.close()
        connection.close()
