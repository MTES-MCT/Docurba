
declare
  curr_procedure_id uuid;
  procedure_doc_type text ;
  is_opposable_event bool;
  is_abandon_event bool;
  is_ongoing_event bool;
  is_annule_event bool;
  new_status text;
  impactful_events jsonb := '{
      "CC": {
        "en cours": ["Délibération de prescription du conseil municipal"],
        "opposable": ["Approbation du préfet"],
        "abandon": ["Abandon"],
        "annule": ["Annulation TA totale"]
      },
      "SCOT": {
        "en cours": ["Délibération de l''établissement public qui prescrit"],
        "opposable": ["Délibération d''approbation", "Caractère exécutoire"],
        "abandon": ["Abandon"],
        "annule": ["Annulation TA totale"]
      },
      "PLU": {
        "en cours": ["Délibération de prescription du conseil municipal ou communautaire"],
        "opposable": ["Caractère exécutoire", "Délibération d''approbation du municipal ou communautaire"],
        "abandon": ["Abandon"],
        "annule": ["Annulation TA totale"]
      }
    }';
begin

  select  id, doc_type, status into curr_procedure_id, procedure_doc_type, new_status
  from procedures
  where project_id = new.project_id;
  RAISE LOG 'DOC TYPE: % - EVENT NAME: %', procedure_doc_type, new.type;
  select  (impactful_events->procedure_doc_type->'opposable')::jsonb ? new.type into is_opposable_event;
  select  (impactful_events->procedure_doc_type->'annule')::jsonb ? new.type into is_annule_event;
  select  (impactful_events->procedure_doc_type->'en cours')::jsonb ? new.type into is_ongoing_event;
  select  (impactful_events->procedure_doc_type->'abandon')::jsonb ? new.type into is_abandon_event;
  RAISE LOG 'is_opposable_event: %', is_opposable_event;
  if is_opposable_event is true then
    RAISE LOG 'IS OPPOSABLE';
    new_status := 'opposable';
  elsif is_annule_event then
    RAISE LOG 'IS ANNULE';
    new_status := 'annule';
  elsif is_ongoing_event then
    RAISE LOG 'IS EN COURS';
    new_status := 'en cours';
  elsif is_abandon_event then
    RAISE LOG 'IS ABANDON';
    new_status := 'abandon';
  end if;
  RAISE LOG 'NOUVEAU STATUS: %', new_status;
  RAISE LOG 'READY TO UPDATE PROC ID: %', curr_procedure_id;

  UPDATE procedures
  SET status = new_status
  WHERE id = curr_procedure_id;

  return new;
end;
