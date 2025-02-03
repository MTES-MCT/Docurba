
-- DROP FUNCTION events_by_procedures_ids(json);
CREATE OR REPLACE FUNCTION events_by_procedures_ids(procedures_ids json)
RETURNS SETOF doc_frise_events AS $$
BEGIN
RETURN QUERY
  SELECT *
  FROM doc_frise_events
  WHERE procedure_id::text IN (SELECT value FROM jsonb_array_elements_text(procedures_ids::jsonb));
RETURN;
END;
$$ LANGUAGE plpgsql;
