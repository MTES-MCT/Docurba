CREATE OR REPLACE FUNCTION check_project_sharing_permission(project_id uuid, user_email text)
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM projects_sharing ps
    WHERE ps.project_id = check_project_sharing_permission.project_id
      AND ps.role = 'write_frise'
      AND ps.user_email = check_project_sharing_permission.user_email
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
