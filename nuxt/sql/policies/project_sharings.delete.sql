CREATE POLICY delete_projects_sharing ON projects_sharing
  FOR INSERT TO authenticated
  WITH CHECK (
    ((auth.uid() = shared_by) OR (shared_by IS NULL))
    AND (
      (auth.uid() = (SELECT owner FROM projects WHERE id = project_id))
      OR EXISTS (
        SELECT 1
        FROM projects p
        JOIN profiles prof ON prof.user_id = auth.uid()
        WHERE p.id = project_id AND prof.departement = p.trame::text
      )
      OR check_project_sharing_permission(project_id, auth.jwt()->>'email')
    )
  );
