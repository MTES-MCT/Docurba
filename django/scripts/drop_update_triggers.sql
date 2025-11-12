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
  PERFORM net.http_get('${NUXT3_API_URL}' || '/api/urba/procedures/' || event_processed.procedure_id || '/update');
  return event_processed;
END;
$$ LANGUAGE plpgsql;

-- Il semble pas être utilisé mais modifions-le au cas où.
CREATE OR REPLACE FUNCTION procedure_status_handler()
RETURNS trigger AS $$
declare
  procedure procedures;
BEGIN
  IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then
    procedure := new;
  else
    procedure := old;
  END IF;

  PERFORM set_procedure_status(procedure);
  PERFORM http_get('${NUXT3_API_URL}' || '/api/urba/procedures/' || procedure.id || '/update');
  return procedure;
END;
$$ LANGUAGE plpgsql;


-- Mise à jour de la colonne `updated_at` lors de chaque modification.
create extension if not exists moddatetime schema extensions;
DROP TRIGGER IF EXISTS "handle_updated_at" ON public.doc_frise_events;
create trigger handle_updated_at before update on public.doc_frise_events
  for each row execute procedure moddatetime (updated_at);

-- Pipedrive n'est pas configuré dans les recettes jetables.
DROP TRIGGER IF EXISTS "Pipedrive Sharing Update" ON public.projects_sharing;
DROP TRIGGER IF EXISTS "Pipedrive Update" ON public.profiles;
