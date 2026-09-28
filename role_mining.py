import sqlite3
import pandas as pd

DB_NAME = "iam_database.db"
THRESHOLD = 0.70

def mine_business_roles():
    conn = sqlite3.connect(DB_NAME)

    query = """
    SELECT 
        e.employee_id,
        e.department,
        ent.entitlement_id,
        ent.entitlement_name
    FROM employees e
    JOIN access_assignments aa ON e.employee_id = aa.employee_id
    JOIN entitlements ent ON aa.entitlement_id = ent.entitlement_id
    WHERE e.status = 'active';
    """
    df_access = pd.read_sql_query(query, conn)

    dept_counts_query = """
    SELECT department, COUNT(employee_id) as total_employees
    FROM employees
    WHERE status = 'active'
    GROUP BY department;
    """
    df_dept_counts = pd.read_sql_query(dept_counts_query, conn)
    dept_total_map = dict(zip(df_dept_counts['department'], df_dept_counts['total_employees']))

    mining_df = df_access.groupby(['department', 'entitlement_name']).agg(
        holders=('employee_id', 'nunique')
    ).reset_index()

    mining_df['total_dept_employees'] = mining_df['department'].map(dept_total_map)
    mining_df['coverage_pct'] = mining_df['holders'] / mining_df['total_dept_employees']

    qualifying_ents = mining_df[mining_df['coverage_pct'] >= THRESHOLD]

    role_proposals = []

    for dept, group in qualifying_ents.groupby('department'):
        role_name = f"{dept} Business Role"
        entitlements_list = ", ".join(group['entitlement_name'].tolist())
        total_staff = dept_total_map[dept]
        
        req_ents = set(group['entitlement_name'])
        dept_user_access = df_access[df_access['department'] == dept]
        
        fully_covered_users = 0
        for emp_id, user_ents in dept_user_access.groupby('employee_id'):
            user_ent_set = set(user_ents['entitlement_name'])
            if req_ents.issubset(user_ent_set):
                fully_covered_users += 1

        coverage_summary = f"{fully_covered_users} / {total_staff} employees ({round((fully_covered_users/total_staff)*100, 1)}%)"

        role_proposals.append({
            "Department": dept,
            "Proposed Role Name": role_name,
            "Entitlements Included": entitlements_list,
            "Employees Covered": coverage_summary
        })

    conn.close()
    
    results_df = pd.DataFrame(role_proposals)
    print("=" * 60)
    print("PROPOSED BUSINESS ROLES (70%+ COVERAGE THRESHOLD)")
    print("=" * 60)
    print(results_df.to_string(index=False))
    
    return results_df

if __name__ == "__main__":
    mine_business_roles()