-- DROP FUNCTION procedures_by_insee_codes(codes json);
CREATE OR REPLACE FUNCTION procedures_by_insee_codes(codes json)
RETURNS SETOF procedures AS $$
BEGIN
RETURN QUERY
  SELECT *
  FROM procedures
  WHERE EXISTS (
    SELECT id, status, doc_type_code as doc_type, current_perimetre, is_pluih
    FROM jsonb_array_elements(current_perimetre) obj
    WHERE ((obj->>'inseeCode')::text IN (
      SELECT jsonb_array_elements_text(codes::jsonb)
    )) and (status in ('opposable', 'en cours')) and (is_principale = true)
  );
  RETURN;
END;
$$ LANGUAGE plpgsql;
