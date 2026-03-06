import mysql.connector
import json
import time

DB_DEBUG_LOG_PATH = r"c:\Users\aksha\Desktop\SG_AI\debug-aedf66.log"


def _write_debug_log(
    hypothesis_id: str, message: str, data: dict, run_id: str = "initial"
):
    # region agent log
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
        with open(DB_DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        # Logging must never break main logic
        pass
    # endregion


try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345",
        database="sg_ai",
    )
    cursor = db.cursor()
    _write_debug_log(
        hypothesis_id="H0",
        message="db_connection_success",
        data={"host": "localhost", "database": "sg_ai"},
    )
except mysql.connector.Error as err:
    _write_debug_log(
        hypothesis_id="H0",
        message="db_connection_error",
        data={"error": str(err)},
    )
    raise


def add_candidate_to_db(name, email, resume_text):
    sql = "INSERT INTO CANDIDATES(name, email, resume_text) VALUES (%s, %s, %s)"
    val = (name, email, resume_text)
    _write_debug_log(
        hypothesis_id="H1",
        message="add_candidate_to_db called",
        data={"name": name, "email": email},
    )
    try:
        cursor.execute(sql, val)
        db.commit()
        print(f"Candidate '{name}' added successfully.")
        _write_debug_log(
            hypothesis_id="H1",
            message="add_candidate_to_db committed",
            data={"rowcount": cursor.rowcount},
        )
    except mysql.connector.Error as err:
        _write_debug_log(
            hypothesis_id="H1",
            message="add_candidate_to_db error",
            data={"error": str(err)},
        )
        print(f"Error: {err}")


def print_all_candidates():
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    for candidate in candidates:
        _write_debug_log(
            hypothesis_id="H2",
            message="print_all_candidates row",
            data={"id": candidate[0], "uploaded_at_type": str(type(candidate[4]))},
        )
        formatted_time = candidate[4].strftime("%d-%b-%Y %H:%M")
        print(f"ID:{candidate[0]} | Name:{candidate[1]} | Uploaded: {formatted_time}")


def add_job_to_db(title, company, description_text):
    sql = "INSERT INTO jobs (title, company, description_text) VALUES (%s, %s, %s)"
    val = (title, company, description_text)
    _write_debug_log(
        hypothesis_id="H3",
        message="add_job_to_db called",
        data={"title": title, "company": company},
    )
    try:
        cursor.execute(sql, val)
        db.commit()
        print(f"Job '{title}' added successfully.")
        _write_debug_log(
            hypothesis_id="H3",
            message="add_job_to_db committed",
            data={"rowcount": cursor.rowcount},
        )
    except mysql.connector.Error as err:
        _write_debug_log(
            hypothesis_id="H3",
            message="add_job_to_db error",
            data={"error": str(err)},
        )
        print(f"Error: {err}")


def print_all_jobs():
    cursor.execute("SELECT * FROM jobs")
    all_jobs = cursor.fetchall()

    print("\n--- Current Job Openings ---")
    for job in all_jobs:
        # job[0]=id, job[1]=title, job[2]=company
        print(f"ID: {job[0]} | Title: {job[1]} | Description: {job[2]}")


def get_all_jobs():
    try:
        cursor.execute("SELECT id, title, company FROM jobs")
        jobs = cursor.fetchall()
        # Convert to list of dicts for easy template rendering
        return [{"id": j[0], "title": j[1], "company": j[2]} for j in jobs]
    except mysql.connector.Error as err:
        print(f"Error fetching jobs: {err}")
        return []

def get_job_by_id(job_id):
    try:
        cursor.execute("SELECT title, description_text FROM jobs WHERE id = %s", (job_id,))
        job = cursor.fetchone()
        if job:
            return {"title": job[0], "description_text": job[1]}
    except mysql.connector.Error as err:
        print(f"Error fetching job by ID: {err}")
    return None
