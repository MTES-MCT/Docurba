create or replace function get_event_impact(event_processed jsonb, doc_type text)
returns text
language plpgsql
as $$
declare
  is_opposable_event bool;
  is_abandon_event bool;
  is_ongoing_event bool;
  is_annule_event bool;
  new_status text := NULL;
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
  is_opposable_event := (impactful_events->doc_type->'opposable') @> jsonb_build_array(event_processed->>'type');
  if is_opposable_event is true then
    RAISE LOG 'IS OPPOSABLE';
    return 'opposable';
  end if;

  is_annule_event := (impactful_events->doc_type->'annule') @> jsonb_build_array(event_processed->>'type');
  if is_annule_event is true then
    RAISE LOG 'IS ANNULE';
    return 'annule';
  end if;

  is_ongoing_event := (impactful_events->doc_type->'en cours') @> jsonb_build_array(event_processed->>'type');
  if is_ongoing_event is true then
    RAISE LOG 'IS EN COURS';
    return 'en cours';
  end if;

  is_abandon_event := (impactful_events->doc_type->'abandon') @> jsonb_build_array(event_processed->>'type');
  if is_abandon_event is true then
    RAISE LOG 'IS ABANDON';
    return 'abandon';
  end if;
  return new_status;
end;
$$;
