import mysql.connector

try:
    # Connect to your database
    db = mysql.connector.connect(
        host="localhost", user="root", password="12345", database="sg_ai"
    )
    cursor = db.cursor()

    # The new job requiring web development skills
    new_title = "Web Developer"
    new_description = "We need a developer who knows React, HTML, CSS, and Python."

    # Insert it into the jobs table
    cursor.execute(
        "INSERT INTO jobs (title, description_text) VALUES (%s, %s)",
        (new_title, new_description),
    )

    db.commit()
    print("🔥 New Web Developer job added successfully!")
    db.close()

except mysql.connector.Error as err:
    print(f"Database error: {err}")
