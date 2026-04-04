from core.modules.database_manager import get_connection


def seed_database():
    connection = get_connection()
    if connection is None:
        print(
            "Could not connect to the database. "
            "Set SG_AI_DB_* environment variables or start MySQL first."
        )
        return

    cursor = connection.cursor()

    try:
        print("Clearing existing jobs to remove duplicates...")
        cursor.execute("DELETE FROM jobs;")
        cursor.execute("ALTER TABLE jobs AUTO_INCREMENT = 1;")

        famous_jobs = [
            (
                "Software Engineer",
                "Builds scalable applications and backend systems.",
                (
                    "Python, Java, C++, SQL, Git, REST APIs, Microservices, "
                    "Agile, Problem Solving, System Design"
                ),
            ),
            (
                "Frontend Developer",
                "Creates user-facing web interfaces and precise layouts.",
                (
                    "HTML, CSS, JavaScript, React, Vue, UI/UX, Responsive "
                    "Design, Webpack, Communication, Creativity"
                ),
            ),
            (
                "Data Scientist",
                "Analyzes complex data to build predictive machine learning "
                "models.",
                (
                    "Python, R, SQL, Machine Learning, Pandas, "
                    "Scikit-Learn, Statistics, Data Visualization, "
                    "Critical Thinking"
                ),
            ),
            (
                "Product Manager",
                "Guides the success of a product and leads the cross-"
                "functional team.",
                (
                    "Agile, Jira, Roadmap Planning, Stakeholder Management, "
                    "User Research, Communication, Leadership, Analytics"
                ),
            ),
            (
                "DevOps Engineer",
                "Bridges development and operations by automating deployment "
                "pipelines.",
                (
                    "Docker, Kubernetes, AWS, CI/CD, Linux, Jenkins, "
                    "Terraform, Bash, Networking, Troubleshooting"
                ),
            ),
            (
                "UX/UI Designer",
                "Designs intuitive and aesthetically pleasing user "
                "experiences.",
                (
                    "Figma, Adobe XD, Wireframing, Prototyping, User "
                    "Testing, Typography, Color Theory, Empathy"
                ),
            ),
        ]

        sql = "INSERT INTO jobs (title, company, description_text) VALUES (%s, %s, %s)"
        cursor.executemany(sql, famous_jobs)
        connection.commit()
        print(f"Successfully inserted {cursor.rowcount} famous job profiles.")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    seed_database()
