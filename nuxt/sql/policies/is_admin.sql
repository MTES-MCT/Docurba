CREATE OR REPLACE FUNCTION is_admin(user_id uuid)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM profiles
    WHERE user_id = $1 AND is_admin IS TRUE
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
