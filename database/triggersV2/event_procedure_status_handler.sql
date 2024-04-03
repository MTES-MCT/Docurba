CREATE OR REPLACE FUNCTION event_procedure_status_handler()
RETURNS trigger AS $$
declare
procedure procedures;
event_processed doc_frise_events;
BEGIN
-- On va chercher la procedure de l'event
  IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then
    event_processed := new;
  else
    event_processed := old;
  END IF;

  SELECT * into procedure
  FROM procedures
  WHERE id = event_processed.procedure_id;

  SELECT set_procedure_status(procedure);
END;
$$ LANGUAGE plpgsql;
