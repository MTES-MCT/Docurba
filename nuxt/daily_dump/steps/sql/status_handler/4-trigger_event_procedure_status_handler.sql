CREATE OR REPLACE FUNCTION event_procedure_status_handler()
RETURNS trigger AS $$
declare
procedure procedures;
event_processed doc_frise_events;
BEGIN
  IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then
    event_processed := new;
  else
    event_processed := old;
  END IF;

  SELECT * into procedure
  FROM procedures
  WHERE id = event_processed.procedure_id;

  PERFORM set_procedure_status(procedure);
  -- NUXT3_API_URL is hardcoded here because this dump will disappear soon and I don't know how to change it quickly in SQL.
  PERFORM net.http_get('https://nuxt3.docurba.incubateur.net/api/urba/procedures/' || event_processed.procedure_id || '/update');
  return event_processed;
END;
$$ LANGUAGE plpgsql;
