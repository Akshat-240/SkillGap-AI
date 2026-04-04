HARD_SKILL_METADATA = {
    # Core Languages
    "python": {
        "learning_paths": [
            {
                "title": "Python for Everybody (edX)",
                "url": "https://www.edx.org/course/programming-for-everybody-getting-started-with-p",
            },
            {
                "title": "Automate the Boring Stuff with Python",
                "url": "https://automatetheboringstuff.com/",
            },
        ],
        "project": "Build a command-line web scraper to fetch daily news headlines.",
        "implied_by": ["django", "flask", "fastapi"],
    },
    "java": {
        "learning_paths": [
            {
                "title": "Java Programming Basics (Coursera)",
                "url": "https://www.coursera.org/learn/java-programming",
            },
            {
                "title": "Java Tutorial for Complete Beginners",
                "url": "https://www.udemy.com/course/java-tutorial/",
            },
        ],
        "project": "Create a command-line banking system with user accounts and transactions.",
        "implied_by": ["spring", "android"],
    },
    "c++": {
        "learning_paths": [
            {
                "title": "Learn C++ (Codecademy)",
                "url": "https://www.codecademy.com/learn/learn-c-plus-plus",
            },
            {
                "title": "C++ Tutorial (W3Schools)",
                "url": "https://www.w3schools.com/cpp/",
            },
        ],
        "project": "Develop a lightweight text-based RPG game or a custom sorting visualization tool.",
        "implied_by": ["unreal engine", "embedded"],
    },
    "javascript": {
        "learning_paths": [
            {
                "title": "JavaScript Algorithms and Data Structures (FreeCodeCamp)",
                "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/",
            },
            {"title": "JavaScript Info", "url": "https://javascript.info/"},
        ],
        "project": "Build a dynamic to-do list application or a browser-based calculator.",
        "implied_by": ["react", "node.js", "vue", "angular", "typescript"],
    },
    "typescript": {
        "learning_paths": [
            {
                "title": "TypeScript Handbook",
                "url": "https://www.typescriptlang.org/docs/handbook/intro.html",
            },
            {
                "title": "Learn TypeScript (Codecademy)",
                "url": "https://www.codecademy.com/learn/learn-typescript",
            },
        ],
        "project": "Refactor an existing vanilla JavaScript project to use strict typing with TypeScript.",
        "implied_by": ["angular", "next.js"],
    },
    "go": {
        "learning_paths": [
            {"title": "A Tour of Go", "url": "https://go.dev/tour/welcome/1"},
            {"title": "Go by Example", "url": "https://gobyexample.com/"},
        ],
        "project": "Build a simple concurrent web server or a CLI tool that hits a REST API.",
        "implied_by": ["kubernetes", "docker"],
    },
    "rust": {
        "learning_paths": [
            {
                "title": "The Rust Programming Language Book",
                "url": "https://doc.rust-lang.org/book/",
            },
            {"title": "Rustlings", "url": "https://github.com/rust-lang/rustlings"},
        ],
        "project": "Build a CPU-bound multithreaded file compression utility.",
        "implied_by": ["webassembly"],
    },
    # Frontend Frameworks
    "react": {
        "learning_paths": [
            {
                "title": "React Official Tutorial",
                "url": "https://react.dev/learn/tutorial-tic-tac-toe",
            },
            {
                "title": "React Course - Beginner's Tutorial",
                "url": "https://www.freecodecamp.org/news/react-course-for-beginners/",
            },
        ],
        "project": "Build a simple weather dashboard displaying data from an external API.",
        "implied_by": ["next.js", "javascript"],
    },
    "angular": {
        "learning_paths": [
            {
                "title": "Tour of Heroes App and Tutorial",
                "url": "https://angular.io/tutorial",
            },
            {
                "title": "Angular Crash Course",
                "url": "https://www.youtube.com/watch?v=3qBXWUpoPHo",
            },
        ],
        "project": "Create an Employee Directory with CRUD operations and routing.",
        "implied_by": ["typescript"],
    },
    "vue": {
        "learning_paths": [
            {
                "title": "Vue.js Official Guide",
                "url": "https://vuejs.org/guide/introduction.html",
            },
            {
                "title": "Intro to Vue 3 (VueMastery)",
                "url": "https://www.vuemastery.com/courses/intro-to-vue-3/intro-to-vue3",
            },
        ],
        "project": "Build a real-time Markdown editor.",
        "implied_by": ["javascript"],
    },
    "next.js": {
        "learning_paths": [
            {"title": "Learn Next.js", "url": "https://nextjs.org/learn"},
            {
                "title": "Next.js Full Course (FreeCodeCamp)",
                "url": "https://www.youtube.com/watch?v=vwSlYG7hFk0",
            },
        ],
        "project": "Build a server-side rendered blog that fetches posts from Markdown files.",
        "implied_by": ["react", "javascript", "typescript"],
    },
    # Backend
    "node.js": {
        "learning_paths": [
            {
                "title": "Node.js Crash Course",
                "url": "https://www.youtube.com/watch?v=fBNz5xF-Kx4",
            },
            {
                "title": "The Net Ninja: Node.js Tutorial",
                "url": "https://www.youtube.com/playlist?list=PL4cUxeGkcC9jsz4LDYc6kv3ymONOKxwBU",
            },
        ],
        "project": "Build a REST API to manage a library's book inventory.",
        "implied_by": ["express", "javascript"],
    },
    "django": {
        "learning_paths": [
            {
                "title": "Writing your first Django app",
                "url": "https://docs.djangoproject.com/en/stable/intro/tutorial01/",
            },
            {"title": "Django for Everybody", "url": "https://www.dj4e.com/"},
        ],
        "project": "Create a blog platform with user authentication and an admin panel.",
        "implied_by": ["python"],
    },
    "flask": {
        "learning_paths": [
            {
                "title": "Flask Mega-Tutorial",
                "url": "https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world",
            },
            {
                "title": "Flask Documentation Quickstart",
                "url": "https://flask.palletsprojects.com/en/2.3.x/quickstart/",
            },
        ],
        "project": "Build a lightweight microservice that serves JSON data from an SQLite database.",
        "implied_by": ["python"],
    },
    "fastapi": {
        "learning_paths": [
            {
                "title": "FastAPI Official Tutorial",
                "url": "https://fastapi.tiangolo.com/tutorial/",
            },
            {
                "title": "FastAPI Course (FreeCodeCamp)",
                "url": "https://www.youtube.com/watch?v=tLKKmouUams",
            },
        ],
        "project": "Create a high-performance REST API with automatic Swagger documentation.",
        "implied_by": ["python"],
    },
    "spring": {
        "learning_paths": [
            {
                "title": "Spring Boot Tutorial (Amigoscode)",
                "url": "https://www.youtube.com/watch?v=9SGDpanrc8U",
            },
            {"title": "Spring Guides", "url": "https://spring.io/guides"},
        ],
        "project": "Build a secure RESTful API for a school management system.",
        "implied_by": ["java"],
    },
    # Cloud & DevOps
    "docker": {
        "learning_paths": [
            {
                "title": "Docker 101 Tutorial",
                "url": "https://www.docker.com/101-tutorial/",
            },
            {
                "title": "Docker Crash Course for Absolute Beginners",
                "url": "https://www.youtube.com/watch?v=pg19Z8LL06w",
            },
        ],
        "project": "Containerize an existing simple web app and push the image to Docker Hub.",
        "implied_by": ["kubernetes", "ci/cd"],
    },
    "kubernetes": {
        "learning_paths": [
            {
                "title": "Kubernetes Basics (Official)",
                "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/",
            },
            {
                "title": "Kubernetes Crash Course for Absolute Beginners",
                "url": "https://www.youtube.com/watch?v=s_o8dwzRlu4",
            },
        ],
        "project": "Deploy a containerized Node.js or Python app to a local Minikube cluster and expose it as a service.",
        "implied_by": ["cloud", "devops"],
    },
    "aws": {
        "learning_paths": [
            {
                "title": "AWS Skill Builder",
                "url": "https://explore.skillbuilder.aws/learn",
            },
            {
                "title": "AWS Cloud Practitioner Essentials",
                "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/",
            },
        ],
        "project": "Host a static HTML website on an S3 bucket and use let's encrypt for SSL.",
        "implied_by": ["cloud", "devops"],
    },
    "azure": {
        "learning_paths": [
            {
                "title": "Microsoft Learn: Azure Fundamentals",
                "url": "https://learn.microsoft.com/en-us/training/paths/az-900-describe-cloud-concepts/",
            },
            {
                "title": "Azure Full Course (FreeCodeCamp)",
                "url": "https://www.youtube.com/watch?v=NKEFWyqJ5XA",
            },
        ],
        "project": "Deploy a Serverless Azure Function that triggers on HTTP requests to format text.",
        "implied_by": ["cloud", "devops"],
    },
    "git": {
        "learning_paths": [
            {
                "title": "Git and GitHub for Beginners",
                "url": "https://www.freecodecamp.org/news/introduction-to-git-and-github/",
            },
            {
                "title": "Learn Git Branching",
                "url": "https://learngitbranching.js.org/",
            },
        ],
        "project": "Create a repository, make a few commits, create a branch, and merge a pull request.",
        "implied_by": ["github", "gitlab", "ci/cd"],
    },
    # Databases
    "sql": {
        "learning_paths": [
            {
                "title": "Intro to SQL: Querying and managing data",
                "url": "https://www.khanacademy.org/computing/computer-programming/sql",
            },
            {
                "title": "SQL Tutorial (W3Schools)",
                "url": "https://www.w3schools.com/sql/",
            },
        ],
        "project": "Design a relational database schema for a blog and write basic CRUD queries.",
        "implied_by": ["mysql", "postgresql", "database"],
    },
    "postgresql": {
        "learning_paths": [
            {
                "title": "PostgreSQL Tutorial",
                "url": "https://www.postgresqltutorial.com/",
            },
            {
                "title": "PostgreSQL Full Course",
                "url": "https://www.youtube.com/watch?v=qw--VYLpxG4",
            },
        ],
        "project": "Create a database, implement constraints and relationships, and practice complex joins.",
        "implied_by": ["sql", "database"],
    },
    "mongodb": {
        "learning_paths": [
            {"title": "MongoDB University", "url": "https://learn.mongodb.com/"},
            {
                "title": "MongoDB Crash Course",
                "url": "https://www.youtube.com/watch?v=pWbMrx5rVBE",
            },
        ],
        "project": "Build a Node.js backend that stores document-oriented notes in MongoDB.",
        "implied_by": ["nosql", "database"],
    },
    "redis": {
        "learning_paths": [
            {"title": "Redis University", "url": "https://university.redis.com/"},
            {
                "title": "Redis Crash Course",
                "url": "https://www.youtube.com/watch?v=jgpVdJB2sKQ",
            },
        ],
        "project": "Implement a basic caching layer in an existing API using Redis to improve repeated query speed.",
        "implied_by": ["nosql", "database"],
    },
    # AI & ML
    "pandas": {
        "learning_paths": [
            {
                "title": "Data Analysis with Python (Coursera)",
                "url": "https://www.coursera.org/learn/data-analysis-with-python",
            },
            {
                "title": "Pandas in 10 Minutes (Docs)",
                "url": "https://pandas.pydata.org/docs/user_guide/10min.html",
            },
        ],
        "project": "Analyze a Kaggle dataset (e.g. Titanic or Sales) and find statistical trends.",
        "implied_by": ["data analysis", "python", "data science"],
    },
    "numpy": {
        "learning_paths": [
            {
                "title": "NumPy Quickstart Tutorial",
                "url": "https://numpy.org/doc/stable/user/quickstart.html",
            },
            {
                "title": "Learn NumPy in 1 Hour",
                "url": "https://www.youtube.com/watch?v=QUT1VHiLmmI",
            },
        ],
        "project": "Perform matrix operations on a CSV datset to normalize numerical values.",
        "implied_by": ["python", "machine learning"],
    },
    "tensorflow": {
        "learning_paths": [
            {
                "title": "TensorFlow Core Basics",
                "url": "https://www.tensorflow.org/tutorials/quickstart/beginner",
            },
            {
                "title": "Deep Learning with TensorFlow (Coursera)",
                "url": "https://www.coursera.org/specializations/deep-learning",
            },
        ],
        "project": "Build an image classification model for handwritten digits using the MNIST dataset.",
        "implied_by": ["machine learning", "deep learning", "ai"],
    },
    "pytorch": {
        "learning_paths": [
            {
                "title": "PyTorch Official Tutorials",
                "url": "https://pytorch.org/tutorials/",
            },
            {
                "title": "PyTorch for Deep Learning Full Course",
                "url": "https://www.youtube.com/watch?v=V_xro1bcAuA",
            },
        ],
        "project": "Implement a simple Convolutional Neural Network (CNN) in PyTorch and train it on CIFAR-10.",
        "implied_by": ["machine learning", "deep learning", "ai"],
    },
    "scikit-learn": {
        "learning_paths": [
            {
                "title": "Scikit-Learn User Guide",
                "url": "https://scikit-learn.org/stable/user_guide.html",
            },
            {
                "title": "Machine Learning in Python with Scikit-Learn",
                "url": "https://www.datacamp.com/tutorial/machine-learning-python",
            },
        ],
        "project": "Train a Random Forest classifier on housing data to predict home prices.",
        "implied_by": ["machine learning", "data science", "python"],
    },
}


SOFT_SKILL_METADATA = {
    "leadership": {
        "learning_paths": [
            {
                "title": "Inspired Leadership Specialization (Coursera)",
                "url": "https://www.coursera.org/specializations/inspired-leadership",
            },
            {
                "title": "Everyday Leadership",
                "url": "https://www.coursera.org/learn/everyday-leadership",
            },
        ],
        "project": "Lead a small open-source contribution team or mentor a junior developer in a weekend hackathon.",
        "implied_by": ["management", "mentoring"],
    },
    "communication": {
        "learning_paths": [
            {
                "title": "Improving Communication Skills (Coursera)",
                "url": "https://www.coursera.org/learn/wharton-communication-skills",
            },
            {
                "title": "Effective Communication",
                "url": "https://www.edx.org/course/effective-communication",
            },
        ],
        "project": "Write a comprehensive technical blog post or present a lightning talk at a local meetup.",
        "implied_by": ["collaboration", "teamwork"],
    },
    "teamwork": {
        "learning_paths": [
            {
                "title": "Teamwork Skills: Communicating Effectively in Groups",
                "url": "https://www.coursera.org/learn/teamwork-skills-effective-communication",
            }
        ],
        "project": "Join a small project team and rotate responsibilities like planner, reviewer, and presenter.",
        "implied_by": ["collaboration", "communication"],
    },
    "problem solving": {
        "learning_paths": [
            {
                "title": "Effective Problem-Solving and Decision-Making (Coursera)",
                "url": "https://www.coursera.org/learn/problem-solving",
            },
            {
                "title": "Algorithmic Problem Solving",
                "url": "https://leetcode.com/explore/",
            },
        ],
        "project": "Participate in a competitive programming contest or solve a real-world workflow bottleneck using scripts.",
        "implied_by": ["critical thinking", "dsa"],
    },
    "time management": {
        "learning_paths": [
            {
                "title": "Work Smarter, Not Harder: Time Management for Personal & Professional Productivity",
                "url": "https://www.coursera.org/learn/work-smarter-not-harder",
            }
        ],
        "project": "Plan a two-week learning sprint and track delivery against your own deadlines.",
        "implied_by": ["management"],
    },
    "mentoring": {
        "learning_paths": [
            {
                "title": "Coaching Skills for Managers",
                "url": "https://www.coursera.org/learn/coaching-skills-for-managers",
            }
        ],
        "project": "Help a junior teammate or friend through a small project and document the progress together.",
        "implied_by": ["leadership", "communication"],
    },
    "agile": {
        "learning_paths": [
            {
                "title": "Agile Crash Course",
                "url": "https://www.udemy.com/course/agile-crash-course/",
            },
            {
                "title": "Atlassian Agile Coach",
                "url": "https://www.atlassian.com/agile",
            },
        ],
        "project": "Set up a Jira or Trello board with 2-week sprints and a backlog for your next personal project.",
        "implied_by": ["scrum", "sdlc"],
    },
    "scrum": {
        "learning_paths": [
            {
                "title": "Scrum Guide",
                "url": "https://scrumguides.org/",
            }
        ],
        "project": "Run a mock sprint planning, daily standup, and retrospective for a side project.",
        "implied_by": ["agile"],
    },
    "sdlc": {
        "learning_paths": [
            {
                "title": "Software Development Life Cycle Specialization",
                "url": "https://www.coursera.org/specializations/software-development-lifecycle",
            }
        ],
        "project": "Document requirements, design, implementation, testing, and release steps for a mini app.",
        "implied_by": ["agile", "scrum"],
    },
    "collaboration": {
        "learning_paths": [
            {
                "title": "Collaboration, Communication and Teamwork",
                "url": "https://www.coursera.org/learn/collaboration-communication-teamwork",
            }
        ],
        "project": "Build something with a partner and practice structured handoffs and feedback reviews.",
        "implied_by": ["communication", "teamwork"],
    },
    "management": {
        "learning_paths": [
            {
                "title": "Principles of Management",
                "url": "https://www.coursera.org/learn/principles-of-management",
            }
        ],
        "project": "Plan a feature backlog, assign owners, and run weekly check-ins for a small build.",
        "implied_by": ["leadership", "stakeholder management"],
    },
    "critical thinking": {
        "learning_paths": [
            {
                "title": "Critical Thinking Skills for University Success",
                "url": "https://www.coursera.org/learn/critical-thinking-skills",
            }
        ],
        "project": "Write out tradeoffs for two different technical solutions before choosing one.",
        "implied_by": ["problem solving"],
    },
    "adaptability": {
        "learning_paths": [
            {
                "title": "Developing Adaptability as a Manager",
                "url": "https://www.linkedin.com/learning/developing-adaptability-as-a-manager",
            }
        ],
        "project": "Take an existing project and intentionally switch tools or constraints mid-way, then document how you adapted.",
        "implied_by": ["problem solving"],
    },
    "conflict resolution": {
        "learning_paths": [
            {
                "title": "Conflict Resolution Skills",
                "url": "https://www.coursera.org/learn/conflict-resolution-skills",
            }
        ],
        "project": "Role-play a disagreement over priorities and practice resolving it with written action items.",
        "implied_by": ["communication", "empathy"],
    },
    "creativity": {
        "learning_paths": [
            {
                "title": "Creative Thinking: Techniques and Tools for Success",
                "url": "https://www.coursera.org/learn/creative-thinking-techniques-and-tools-for-success",
            }
        ],
        "project": "Redesign an everyday workflow in two very different ways and compare the results.",
        "implied_by": ["adaptability"],
    },
    "stakeholder management": {
        "learning_paths": [
            {
                "title": "Project Management: Stakeholder Management",
                "url": "https://www.coursera.org/learn/project-management-stakeholder-management",
            }
        ],
        "project": "Create a stakeholder map for a product idea and write updates tailored to each audience.",
        "implied_by": ["communication", "management"],
    },
    "troubleshooting": {
        "learning_paths": [
            {
                "title": "Troubleshooting and Debugging Techniques",
                "url": "https://www.linkedin.com/learning/troubleshooting-for-web-developers",
            }
        ],
        "project": "Take a broken sample app, debug it step by step, and write a root-cause summary.",
        "implied_by": ["problem solving", "critical thinking"],
    },
    "empathy": {
        "learning_paths": [
            {
                "title": "Empathy and Emotional Intelligence at Work",
                "url": "https://www.coursera.org/learn/empathy-emotional-intelligence-at-work",
            }
        ],
        "project": "Interview users or teammates about a pain point and summarize their perspective before proposing fixes.",
        "implied_by": ["communication"],
    },
}


SOFT_SKILLS = set(SOFT_SKILL_METADATA.keys())
HARD_SKILLS = set(HARD_SKILL_METADATA.keys())

# Backward-compatible combined view for any older code paths.
SKILL_METADATA = {**HARD_SKILL_METADATA, **SOFT_SKILL_METADATA}
