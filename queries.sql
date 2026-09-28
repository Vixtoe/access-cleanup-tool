-- Query 1: Leavers who still have active access assignments
SELECT 
    e.employee_id,
    e.name AS employee_name,
    e.department,
    e.leave_date,
    a.app_name,
    ent.entitlement_name,
    aa.granted_date,
    aa.last_used_date
FROM access_assignments aa
JOIN employees e ON aa.employee_id = e.employee_id
JOIN entitlements ent ON aa.entitlement_id = ent.entitlement_id
JOIN applications a ON ent.app_id = a.app_id
WHERE e.status = 'leaver'
ORDER BY e.leave_date DESC;

-- Query 2: Access assignments not used in 180+ days
SELECT 
    e.employee_id,
    e.name AS employee_name,
    e.department,
    a.app_name,
    ent.entitlement_name,
    aa.last_used_date,
    CAST((JULIANDAY('2026-09-01') - JULIANDAY(aa.last_used_date)) AS INTEGER) AS days_inactive
FROM access_assignments aa
JOIN employees e ON aa.employee_id = e.employee_id
JOIN entitlements ent ON aa.entitlement_id = ent.entitlement_id
JOIN applications a ON ent.app_id = a.app_id
WHERE aa.last_used_date IS NOT NULL 
  AND JULIANDAY('2026-09-01') - JULIANDAY(aa.last_used_date) >= 180
ORDER BY days_inactive DESC;

-- Query 3: Applications with zero active users (Cleanup Candidates)
SELECT 
    a.app_id,
    a.app_name,
    a.owner_department,
    a.status AS app_status
FROM applications a
LEFT JOIN entitlements ent ON a.app_id = ent.app_id
LEFT JOIN access_assignments aa ON ent.entitlement_id = aa.entitlement_id
LEFT JOIN employees e ON aa.employee_id = e.employee_id AND e.status = 'active'
GROUP BY a.app_id, a.app_name, a.owner_department, a.status
HAVING COUNT(e.employee_id) = 0
ORDER BY a.app_id;

-- Query 4: Movers holding access from their previous department
SELECT 
    e.employee_id,
    e.name AS employee_name,
    e.department AS current_department,
    a.owner_department AS app_owner_department,
    a.app_name,
    ent.entitlement_name,
    aa.granted_date
FROM access_assignments aa
JOIN employees e ON aa.employee_id = e.employee_id
JOIN entitlements ent ON aa.entitlement_id = ent.entitlement_id
JOIN applications a ON ent.app_id = a.app_id
WHERE e.status = 'mover'
  AND a.owner_department != e.department
  AND a.owner_department != 'IT Ops'
ORDER BY e.employee_id;

-- Query 5: Number of entitlements per application
SELECT 
    a.app_id,
    a.app_name,
    a.owner_department,
    COUNT(ent.entitlement_id) AS total_entitlements
FROM applications a
LEFT JOIN entitlements ent ON a.app_id = ent.app_id
GROUP BY a.app_id, a.app_name, a.owner_department
ORDER BY total_entitlements DESC;