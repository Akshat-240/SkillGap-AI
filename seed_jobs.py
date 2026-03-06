import mysql.connector

def seed_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="sg_ai"
        )
        cursor = db.cursor()

        # 1. Clear existing jobs to ensure no duplicates using DELETE
        print("Clearing existing jobs to remove duplicates...")
        cursor.execute("DELETE FROM jobs;")
        cursor.execute("ALTER TABLE jobs AUTO_INCREMENT = 1;")
        
        # 2. Define our "Famous Jobs"
        # We use the 'company' column to store the short description as requested: "Name (Description)"
        famous_jobs = [
            (
                "Software Engineer", 
                "Builds scalable applications and backend systems.", 
                "Python, Java, C++, SQL, Git, REST APIs, Microservices, Agile, Problem Solving, System Design"
            ),
            (
                "Frontend Developer", 
                "Creates user-facing web interfaces and precise layouts.", 
                "HTML, CSS, JavaScript, React, Vue, UI/UX, Responsive Design, Webpack, Communication, Creativity"
            ),
            (
                "Data Scientist", 
                "Analyzes complex data to build predictive machine learning models.", 
                "Python, R, SQL, Machine Learning, Pandas, Scikit-Learn, Statistics, Data Visualization, Critical Thinking"
            ),
            (
                "Product Manager", 
                "Guides the success of a product and leads the cross-functional team.", 
                "Agile, Jira, Roadmap Planning, Stakeholder Management, User Research, Communication, Leadership, Analytics"
            ),
            (
                "DevOps Engineer", 
                "Bridges development and operations by automating deployment pipelines.", 
                "Docker, Kubernetes, AWS, CI/CD, Linux, Jenkins, Terraform, Bash, Networking, Troubleshooting"
            ),
            (
                "UX/UI Designer", 
                "Designs intuitive and aesthetically pleasing user experiences.", 
                "Figma, Adobe XD, Wireframing, Prototyping, User Testing, Typography, Color Theory, Empathy"
            )
        ]

        # 3. Insert into the jobs table
        sql = "INSERT INTO jobs (title, company, description_text) VALUES (%s, %s, %s)"
        cursor.executemany(sql, famous_jobs)
        db.commit()

        print(f"Successfully inserted {cursor.rowcount} famous job profiles.")

        cursor.close()
        db.close()
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    seed_database()
