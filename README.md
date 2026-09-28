# Access Cleanup & Role Mining Tool

An automated Identity and Access Management (IAM) analysis tool built with Python, SQL, and pandas. This tool audits access assignments, detects policy violations (offboarding failures, privilege creep, dormant access), identifies unassigned applications, and mines role baselines for Role-Based Access Control (RBAC).

> **Note:** All data analyzed by this project is **100% synthetic** generated with fixed seeds for demonstration and portfolio purposes. No real enterprise or employee data is used.

---

## Repository Structure

```text
access-cleanup-tool/
│
├── generate_data.py          # Synthetic data generator (SQLite)
├── queries.sql               # IAM audit SQL queries
├── run_queries.py            # Executes SQL queries into pandas DataFrames
├── role_mining.py            # Role mining algorithm (70% coverage threshold)
├── generate_report.py        # Excel report builder with openpyxl formatting
├── iam_database.db           # SQLite database
├── access_review_report.xlsx # Final executive audit report
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
