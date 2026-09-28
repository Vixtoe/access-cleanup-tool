import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)
DB_NAME = "iam_database.db"

def init_db(conn):
    cursor = conn.cursor()
    cursor.executescript("""
    DROP TABLE IF EXISTS access_assignments;
    DROP TABLE IF EXISTS entitlements;
    DROP TABLE IF EXISTS applications;
    DROP TABLE IF EXISTS employees;

    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        job_title TEXT NOT NULL,
        status TEXT NOT NULL,
        hire_date TEXT NOT NULL,
        leave_date TEXT
    );

    CREATE TABLE applications (
        app_id INTEGER PRIMARY KEY,
        app_name TEXT NOT NULL,
        owner_department TEXT NOT NULL,
        onboarded_date TEXT NOT NULL,
        status TEXT NOT NULL
    );

    CREATE TABLE entitlements (
        entitlement_id INTEGER PRIMARY KEY,
        app_id INTEGER NOT NULL,
        entitlement_name TEXT NOT NULL,
        FOREIGN KEY (app_id) REFERENCES applications (app_id)
    );

    CREATE TABLE access_assignments (
        employee_id INTEGER NOT NULL,
        entitlement_id INTEGER NOT NULL,
        granted_date TEXT NOT NULL,
        last_used_date TEXT,
        PRIMARY KEY (employee_id, entitlement_id),
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id),
        FOREIGN KEY (entitlement_id) REFERENCES entitlements (entitlement_id)
    );
    """)
    conn.commit()

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"]

DEPARTMENTS = ["Finance", "Human Resources", "Engineering", "Sales", "Marketing", "Customer Support", "Legal", "IT Ops"]

TITLES_BY_DEPT = {
    "Finance": ["Financial Analyst", "Accountant", "Payroll Specialist", "Finance Director"],
    "Human Resources": ["HR Generalist", "Recruiter", "HRBP", "Compensation Analyst"],
    "Engineering": ["Software Engineer", "DevOps Engineer", "QA Engineer", "Engineering Manager"],
    "Sales": ["Account Executive", "Sales Manager", "BDR", "Sales Operations Analyst"],
    "Marketing": ["Marketing Manager", "Content Specialist", "SEO Analyst", "Graphic Designer"],
    "Customer Support": ["Support Specialist", "Support Lead", "Customer Success Rep"],
    "Legal": ["Legal Counsel", "Compliance Analyst", "Paralegal"],
    "IT Ops": ["System Administrator", "Network Engineer", "IT Support Specialist", "Security Analyst"]
}

APPLICATIONS = [
    ("Workday", "Human Resources"), ("Salesforce", "Sales"), ("Jira", "Engineering"),
    ("GitHub", "Engineering"), ("SAP Finance", "Finance"), ("Concur", "Finance"),
    ("Zendesk", "Customer Support"), ("Slack", "IT Ops"), ("Google Workspace", "IT Ops"),
    ("Marketo", "Marketing"), ("HubSpot", "Marketing"), ("DocuSign", "Legal"),
    ("ServiceNow", "IT Ops"), ("Tableau", "Finance"), ("Snowflake", "Engineering"),
    ("Datadog", "Engineering"), ("AWS Console", "Engineering"), ("Zoom", "IT Ops"),
    ("Office 365", "IT Ops"), ("ADP Payroll", "Human Resources"), ("BambooHR", "Human Resources"),
    ("Legacy Portal", "IT Ops"), ("Old CRM", "Sales"), ("Archived Docs", "Legal"), ("DeprecDB", "Engineering")
]

def random_date(start_year=2020, end_year=2025):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).strftime("%Y-%m-%d")

def populate_data():
    conn = sqlite3.connect(DB_NAME)
    init_db(conn)
    cursor = conn.cursor()

    app_id_counter = 1
    entitlement_id_counter = 1
    app_entitlements_map = {}
    dept_app_map = {dept: [] for dept in DEPARTMENTS}

    for app_name, owner_dept in APPLICATIONS:
        app_status = "retired" if app_id_counter >= 23 else "active"
        onboarded = random_date(2020, 2022)
        cursor.execute("INSERT INTO applications VALUES (?, ?, ?, ?, ?)", (app_id_counter, app_name, owner_dept, onboarded, app_status))
        dept_app_map[owner_dept].append(app_id_counter)

        roles = ["User", "Admin", "Viewer", "Manager"]
        app_entitlements_map[app_id_counter] = []
        for role in roles[:random.randint(2, 4)]:
            ent_name = f"{app_name} - {role}"
            cursor.execute("INSERT INTO entitlements VALUES (?, ?, ?)", (entitlement_id_counter, app_id_counter, ent_name))
            app_entitlements_map[app_id_counter].append(entitlement_id_counter)
            entitlement_id_counter += 1
        app_id_counter += 1

    shared_apps = [8, 9, 18, 19]
    employees = []
    status_pool = ["active"] * 240 + ["leaver"] * 30 + ["mover"] * 30
    random.shuffle(status_pool)
    mover_old_depts = {}

    for emp_id in range(1, 301):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        dept = random.choice(DEPARTMENTS)
        title = random.choice(TITLES_BY_DEPT[dept])
        status = status_pool[emp_id - 1]
        hire_d = random_date(2021, 2024)
        leave_d = None

        if status == "leaver":
            hire_dt = datetime.strptime(hire_d, "%Y-%m-%d")
            leave_d = (hire_dt + timedelta(days=random.randint(100, 500))).strftime("%Y-%m-%d")
        elif status == "mover":
            mover_old_depts[emp_id] = random.choice([d for d in DEPARTMENTS if d != dept])

        employees.append((emp_id, name, dept, title, status, hire_d, leave_d))

    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)", employees)

    assignments = set()
    reference_date = datetime(2026, 9, 1)

    for emp_id, name, current_dept, title, status, hire_d, leave_d in employees:
        relevant_apps = list(shared_apps) + dept_app_map[current_dept]
        if status == "mover":
            relevant_apps.extend(dept_app_map[mover_old_depts[emp_id]])

        for app_id in set(relevant_apps):
            if app_id in [23, 24, 25]:
                continue
            available_ents = app_entitlements_map[app_id]
            if random.random() < 0.75:
                chosen_ent = random.choice(available_ents)
                granted_d = hire_d
                days_ago = random.randint(1, 60)
                last_used_dt = reference_date - timedelta(days=days_ago)

                if random.random() < 0.15:
                    last_used_dt = reference_date - timedelta(days=random.randint(185, 400))

                last_used_d = last_used_dt.strftime("%Y-%m-%d")

                if status == "leaver":
                    if random.random() < 0.50:
                        assignments.add((emp_id, chosen_ent, granted_d, last_used_d))
                else:
                    assignments.add((emp_id, chosen_ent, granted_d, last_used_d))

    cursor.executemany("INSERT INTO access_assignments VALUES (?, ?, ?, ?)", list(assignments))
    conn.commit()
    conn.close()
    print("Database successfully generated and populated: iam_database.db")

if __name__ == "__main__":
    populate_data()