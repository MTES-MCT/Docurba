create or replace function get_event_impact(event_processed doc_frise_events, doc_type text)
returns text
language plpgsql
as $$
declare
  is_opposable_event bool;
  is_caduc_event bool;
  is_abandon_event bool;
  is_ongoing_event bool;
  is_annule_event bool;
  new_status text := NULL;

  impactful_events jsonb := '{
      "CC": {
        "en cours": ["Délibération de prescription du conseil municipal"],
        "opposable": ["Approbation du préfet", "Caractère exécutoire", "Retrait de l''annulation totale"],
        "abandon": ["Abandon", "Retrait de la délibération de prescription"],
        "annule": ["Annulation TA totale", "Annulation TA", "Abrogation effective"],
        "caduc": []
      },
      "SCOT": {
        "en cours": ["Délibération de l''établissement public qui prescrit", "Retrait de la délibération d''approbation"],
        "opposable": ["Délibération d''approbation", "Caractère exécutoire", "Retrait de l''annulation totale"],
        "abandon": ["Abandon", "Retrait de la délibération de prescription"],
        "annule": ["Annulation TA totale", "Annulation TA"],
        "caduc": ["Caducité"]
      },
      "SD": {
        "en cours": ["Délibération de l''établissement public qui prescrit"],
        "opposable": ["Délibération d''approbation", "Caractère exécutoire"],
        "abandon": ["Abandon"],
        "annule": ["Annulation TA totale", "Annulation TA"],
        "caduc": ["Caducité"]
      },
      "PLU": {
        "en cours": ["Délibération de prescription du conseil municipal ou communautaire"],
        "opposable": ["Caractère exécutoire", "Retrait de l''annulation totale", "Délibération d''approbation du municipal ou communautaire", "Délibération d''approbation du conseil municipal ou communautaire", "Délibération d''approbation"],
        "abandon": ["Abandon", "Retrait de la délibération de prescription"],
        "annule": ["Annulation TA totale", "Annulation TA", "Abrogation", "Arrêté d''abrogation"],
        "caduc": ["Caducité"]
      },
      "POS": {
        "en cours": ["Délibération de prescription du conseil municipal ou communautaire"],
        "opposable": ["Caractère exécutoire", "Délibération d''approbation du municipal ou communautaire", "Délibération d''approbation du conseil municipal ou communautaire", "Délibération d''approbation"],
        "abandon": ["Abandon"],
        "annule": ["Annulation TA", "Annulation TA totale", "Caducité"],
        "caduc": []
      }
    }';
begin

  if doc_type ILIKE 'PLU%' then
    doc_type := 'PLU';
  end if;
  RAISE LOG 'doc_type PASSED IN FUNC: %', doc_type;

  select  (impactful_events->doc_type->'caduc')::jsonb ? event_processed.type into is_caduc_event;
  if is_caduc_event is true then
    RAISE LOG 'IS CADUC: %', event_processed.type;
    return 'caduc';
  end if;

  select  (impactful_events->doc_type->'opposable')::jsonb ? event_processed.type into is_opposable_event;
  if is_opposable_event is true then
    RAISE LOG 'IS OPPOSABLE: %', event_processed.type;
    return 'opposable';
  end if;

  select  (impactful_events->doc_type->'annule')::jsonb ? event_processed.type into is_annule_event;
  if is_annule_event is true then
    RAISE LOG 'IS ANNULE';
    return 'annule';
  end if;

  select  (impactful_events->doc_type->'en cours')::jsonb ? event_processed.type into is_ongoing_event;

  if is_ongoing_event is true then
    RAISE LOG 'IS EN COURS';
    return 'en cours';
  end if;

  select  (impactful_events->doc_type->'abandon')::jsonb ? event_processed.type into is_abandon_event;
  if is_abandon_event is true then
    RAISE LOG 'IS ABANDON';
    return 'abandon';
  end if;
  return null;
end;
$$;
