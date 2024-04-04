CREATE OR REPLACE FUNCTION set_procedure_status(procedure procedures)
RETURNS void AS $$
DECLARE
  new_status text;
  event doc_frise_events;
  current_date_opposable text;
BEGIN
    FOR event IN
      SELECT *
      FROM doc_frise_events
      WHERE procedure_id = procedure.id
      AND (is_valid = true OR type = 'Abandon')
      ORDER BY date_iso DESC, type
    LOOP
      new_status := get_event_impact(event, procedure.doc_type_code);
      IF new_status = 'opposable' THEN
        current_date_opposable := event.date_iso;
      END IF;

      IF new_status IS NOT null then
        EXIT;
      END IF;
    END LOOP;

    IF new_status IS NULL THEN
      new_status := 'en cours';
    END IF;

    UPDATE procedures
      SET status = new_status, date_opposable = current_date_opposable
      WHERE id = procedure.id;

    current_date_opposable := null;
    new_status := null;
    END;
$$ LANGUAGE plpgsql;
