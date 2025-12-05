from typing import Dict

from .utils import setup_logger

logger = setup_logger("glossary")


DEFAULT_GLOSSARY = {
    "Python": "Python",
    "Java": "Java",
    "JavaScript": "JavaScript",
    "TypeScript": "TypeScript",
    "Dart": "Dart",
    "Kotlin": "Kotlin",
    "Swift": "Swift",
    "C": "C",
    "C++": "C++",
    "CSharp": "CSharp",
    "C#": "C#",
    "Go": "Go",
    "Rust": "Rust",
    "Ruby": "Ruby",
    "PHP": "PHP",
    "SQL": "SQL",
    "HTML": "HTML",
    "CSS": "CSS",

    "React": "React",
    "React Native": "React Native",
    "NextJS": "NextJS",
    "Node": "Node",
    "NodeJS": "NodeJS",
    "Express": "Express",
    "Vue": "Vue",
    "Nuxt": "Nuxt",
    "Angular": "Angular",
    "Svelte": "Svelte",

    "Flutter": "Flutter",
    "Android": "Android",
    "iOS": "iOS",
    "Xcode": "Xcode",
    "SwiftUI": "SwiftUI",
    "Jetpack": "Jetpack",
    "Compose": "Compose",

    "Machine Learning": "Machine Learning",
    "Deep Learning": "Deep Learning",
    "Neural Network": "Neural Network",
    "AI": "AI",
    "ML": "ML",
    "DL": "DL",
    "NLP": "NLP",
    "LSTM": "LSTM",
    "CNN": "CNN",
    "RNN": "RNN",
    "Transformer": "Transformer",
    "Whisper": "Whisper",
    "OpenAI": "OpenAI",

    "API": "API",
    "REST": "REST",
    "GraphQL": "GraphQL",
    "Webhook": "Webhook",
    "WebSocket": "WebSocket",
    "HTTP": "HTTP",
    "HTTPS": "HTTPS",
    "JSON": "JSON",
    "YAML": "YAML",
    "XML": "XML",

    "Database": "Database",
    "MongoDB": "MongoDB",
    "MySQL": "MySQL",
    "PostgreSQL": "PostgreSQL",
    "SQL Server": "SQL Server",
    "Redis": "Redis",
    "Firebase": "Firebase",
    "Supabase": "Supabase",
    "Prisma": "Prisma",
    "Mongoose": "Mongoose",
    "ORM": "ORM",
    "ODM": "ODM",

    "Docker": "Docker",
    "Kubernetes": "Kubernetes",
    "Container": "Container",
    "CI": "CI",
    "CD": "CD",
    "CI/CD": "CI/CD",
    "Jenkins": "Jenkins",
    "GitHub Actions": "GitHub Actions",
    "GitLab": "GitLab",
    "Terraform": "Terraform",
    "AWS": "AWS",
    "Azure": "Azure",
    "GCP": "GCP",
    "Cloud": "Cloud",
    "Serverless": "Serverless",

    "Git": "Git",
    "GitHub": "GitHub",
    "Bitbucket": "Bitbucket",
    "Version Control": "Version Control",
    "Branch": "Branch",
    "Fork": "Fork",
    "Pull Request": "Pull Request",
    "Commit": "Commit",
    "Merge": "Merge",
    "Rebase": "Rebase",
    "Clone": "Clone",

    "Frontend": "Frontend",
    "Backend": "Backend",
    "Fullstack": "Fullstack",
    "UI": "UI",
    "UX": "UX",
    "Design System": "Design System",
    "Component": "Component",
    "State Management": "State Management",
    "Redux": "Redux",
    "MobX": "MobX",
    "Zustand": "Zustand",
    "Bloc": "Bloc",
    "Cubit": "Cubit",
    "Provider": "Provider",
    "Riverpod": "Riverpod",

    "Testing": "Testing",
    "Unit Test": "Unit Test",
    "Integration Test": "Integration Test",
    "End to End Test": "End to End Test",
    "Jest": "Jest",
    "Mocha": "Mocha",
    "PyTest": "PyTest",
    "Selenium": "Selenium",
    "Cypress": "Cypress",

    "Data Science": "Data Science",
    "Pandas": "Pandas",
    "NumPy": "NumPy",
    "SciPy": "SciPy",
    "Matplotlib": "Matplotlib",
    "Seaborn": "Seaborn",
    "TensorFlow": "TensorFlow",
    "PyTorch": "PyTorch",
    "OpenCV": "OpenCV",

    "DevOps": "DevOps",
    "SRE": "SRE",
    "Load Balancer": "Load Balancer",
    "Reverse Proxy": "Reverse Proxy",
    "Nginx": "Nginx",
    "Apache": "Apache",

    "Security": "Security",
    "OAuth": "OAuth",
    "JWT": "JWT",
    "Encryption": "Encryption",
    "Hashing": "Hashing",
    "SSL": "SSL",
    "TLS": "TLS",

    "LLM": "LLM",
    "Embedding": "Embedding",
    "Vector DB": "Vector DB",
    "RAG": "RAG",
    "Fine Tuning": "Fine Tuning",
    "Quantization": "Quantization",
    "Inference": "Inference",

    "VS Code": "VS Code",
    "IDE": "IDE",
    "Debugger": "Debugger",
    "Compiler": "Compiler",
    "Runtime": "Runtime",
    "CLI": "CLI",
    "Terminal": "Terminal",

    "Agile": "Agile",
    "Scrum": "Scrum",
    "Kanban": "Kanban",
    "Sprint": "Sprint",
    "Jira": "Jira",
    "Confluence": "Confluence",

    "Microservices": "Microservices",
    "Monolith": "Monolith",
    "Event Driven": "Event Driven",
    "Message Queue": "Message Queue",
    "Kafka": "Kafka",
    "RabbitMQ": "RabbitMQ",

    "GPU": "GPU",
    "CPU": "CPU",
    "RAM": "RAM",
    "SSD": "SSD",
    "HDD": "HDD",

    # Core Software Development
    "Software Development": "Software Development",
    "Software Developer": "Software Developer",
    "Programmer": "Programmer",
    "Coder": "Coder",
    "Application Developer": "Application Developer",
    "Mobile App Developer": "Mobile App Developer",
    "Web Developer": "Web Developer",
    "Frontend Developer": "Frontend Developer",
    "Backend Developer": "Backend Developer",
    "Fullstack Developer": "Fullstack Developer",
    "Game Developer": "Game Developer",
    "AR Developer": "AR Developer",
    "VR Developer": "VR Developer",
    "Unity Developer": "Unity Developer",
    "Unreal Developer": "Unreal Developer",

    # Languages
    "Python": "Python",
    "Java": "Java",
    "JavaScript": "JavaScript",
    "TypeScript": "TypeScript",
    "Dart": "Dart",
    "Kotlin": "Kotlin",
    "Swift": "Swift",
    "Go": "Go",
    "Rust": "Rust",
    "Ruby": "Ruby",
    "PHP": "PHP",
    "C": "C",
    "C++": "C++",
    "C#": "C#",

    # Web Stack
    "React": "React",
    "NextJS": "NextJS",
    "NodeJS": "NodeJS",
    "Express": "Express",
    "Angular": "Angular",
    "Vue": "Vue",
    "Svelte": "Svelte",
    "Tailwind": "Tailwind",
    "Bootstrap": "Bootstrap",

    # Mobile
    "Flutter": "Flutter",
    "React Native": "React Native",
    "Android": "Android",
    "iOS": "iOS",
    "Xcode": "Xcode",
    "SwiftUI": "SwiftUI",
    "Android Studio": "Android Studio",

    # Databases
    "SQL": "SQL",
    "MySQL": "MySQL",
    "MongoDB": "MongoDB",
    "PostgreSQL": "PostgreSQL",
    "SQLite": "SQLite",
    "Redis": "Redis",
    "Firebase": "Firebase",
    "Supabase": "Supabase",
    "Prisma": "Prisma",

    # DevOps & Cloud
    "DevOps": "DevOps",
    "SRE": "SRE",
    "Docker": "Docker",
    "Kubernetes": "Kubernetes",
    "CI/CD": "CI/CD",
    "Jenkins": "Jenkins",
    "Nginx": "Nginx",
    "AWS": "AWS",
    "Azure": "Azure",
    "Google Cloud": "Google Cloud",
    "Cloud Engineer": "Cloud Engineer",
    "DevOps Engineer": "DevOps Engineer",
    "Site Reliability Engineer": "Site Reliability Engineer",

    # AI & ML
    "Artificial Intelligence": "Artificial Intelligence",
    "Machine Learning": "Machine Learning",
    "Deep Learning": "Deep Learning",
    "Data Scientist": "Data Scientist",
    "Data Analyst": "Data Analyst",
    "AI Engineer": "AI Engineer",
    "ML Engineer": "ML Engineer",
    "LLM": "LLM",
    "GPT": "GPT",
    "Whisper": "Whisper",
    "Transformers": "Transformers",
    "OpenAI": "OpenAI",
    "HuggingFace": "HuggingFace",

    # Cybersecurity
    "Cyber Security": "Cyber Security",
    "Ethical Hacker": "Ethical Hacker",
    "Pen Tester": "Pen Tester",
    "Security Analyst": "Security Analyst",
    "Network Security": "Network Security",
    "Encryption": "Encryption",

    # Networking
    "Network Engineer": "Network Engineer",
    "Network Administrator": "Network Administrator",
    "LAN": "LAN",
    "WAN": "WAN",
    "VPN": "VPN",
    "Router": "Router",
    "Firewall": "Firewall",

    # Testing & QA
    "QA Engineer": "QA Engineer",
    "Quality Assurance": "Quality Assurance",
    "Testing Engineer": "Testing Engineer",
    "Automation Tester": "Automation Tester",
    "Manual Tester": "Manual Tester",
    "Selenium": "Selenium",
    "Cypress": "Cypress",

    # Product & Management Roles
    "Product Manager": "Product Manager",
    "Project Manager": "Project Manager",
    "Scrum Master": "Scrum Master",
    "Business Analyst": "Business Analyst",
    "UI Designer": "UI Designer",
    "UX Designer": "UX Designer",
    "UI UX Designer": "UI UX Designer",
    "Graphic Designer": "Graphic Designer",
    "Content Writer": "Content Writer",
    "Technical Writer": "Technical Writer",

    # Tech Support
    "IT Support": "IT Support",
    "Technical Support Engineer": "Technical Support Engineer",
    "Helpdesk Engineer": "Helpdesk Engineer",
    "System Administrator": "System Administrator",

    # AI Agent & Automation Roles
    "Automation Engineer": "Automation Engineer",
    "RPA Developer": "RPA Developer",
    "AI Automation Engineer": "AI Automation Engineer",
    "Chatbot Developer": "Chatbot Developer",
    "Agentic AI Developer": "Agentic AI Developer",

    # General IT Job Titles
    "Software Engineer": "Software Engineer",
    "Senior Software Engineer": "Senior Software Engineer",
    "Lead Engineer": "Lead Engineer",
    "Tech Lead": "Tech Lead",
    "Architect": "Architect",
    "Solution Architect": "Solution Architect",
    "Cloud Architect": "Cloud Architect",

    # Misc Workplace Terms
    "Intern": "Intern",
    "Fresher": "Fresher",
    "Manager": "Manager",
    "Team Leader": "Team Leader",
    "HR": "HR",
    "Recruiter": "Recruiter",
    "Interview": "Interview",
    "Resume": "Resume",
    "Portfolio": "Portfolio",

    # Industry Domains
    "Healthcare": "Healthcare",
    "FinTech": "FinTech",
    "EdTech": "EdTech",
    "AgriTech": "AgriTech",
    "TravelTech": "TravelTech",
    "Ecommerce": "Ecommerce",
    "Banking": "Banking",
    "Insurance": "Insurance",

    # General Job Roles (Non-IT)
    "Driver": "Driver",
    "Truck Driver": "Truck Driver",
    "Cab Driver": "Cab Driver",
    "Delivery Boy": "Delivery Boy",
    "Mechanic": "Mechanic",
    "Electrician": "Electrician",
    "Plumber": "Plumber",
    "Carpenter": "Carpenter",
    "Chef": "Chef",
    "Cook": "Cook",
    "Waiter": "Waiter",
    "Teacher": "Teacher",
    "Professor": "Professor",
    "Doctor": "Doctor",
    "Nurse": "Nurse",
    "Pharmacist": "Pharmacist",
    "Engineer": "Engineer",
    "Civil Engineer": "Civil Engineer",
    "Mechanical Engineer": "Mechanical Engineer",
    "Electrical Engineer": "Electrical Engineer",

    # Digital Marketing & Business
    "Digital Marketing": "Digital Marketing",
    "SEO": "SEO",
    "SEM": "SEM",
    "Social Media Manager": "Social Media Manager",
    "Brand Manager": "Brand Manager",
    "Sales Executive": "Sales Executive",
    "Marketing Manager": "Marketing Manager",

    # Freelancing Roles
    "Freelancer": "Freelancer",
    "Video Editor": "Video Editor",
    "Photographer": "Photographer",
    "Videographer": "Videographer",
    "Animator": "Animator",
    "3D Artist": "3D Artist",

    # Misc Tech Words
    "API": "API",
    "SDK": "SDK",
    "IDE": "IDE",
    "Open Source": "Open Source",
    "Repository": "Repository",
    "Pipeline": "Pipeline",
    "Deployment": "Deployment",
    "Cloud Computing": "Cloud Computing",
    "Data Pipeline": "Data Pipeline",
    "Debugging": "Debugging",
    "Version Control": "Version Control"
}



def merge_glossaries(base: Dict[str, str], rag: Dict[str, str]) -> Dict[str, str]:
    merged = dict(base or {})
    merged.update(rag or {})
    return merged


def clean_transcript(text: str, glossary: Dict[str, str]) -> str:
    if not text:
        return text

    cleaned = text
    # Normalize whitespace
    cleaned = " ".join(cleaned.split())

    # Replace mapped terms with canonical forms
    # Simple token-based replacement; preserves "tech words" by mapping to themselves
    for k, v in glossary.items():
        # Case-insensitive replace while preserving case of the value
        cleaned = cleaned.replace(k, v)
        cleaned = cleaned.replace(k.lower(), v)
        cleaned = cleaned.replace(k.upper(), v)

    return cleaned