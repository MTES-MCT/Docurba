set statement_timeout to 120000;
CREATE OR REPLACE FUNCTION one_shot_change_status()
RETURNS void AS $$
DECLARE
  new_status text;
  temp text;
  event doc_frise_events_duplicate;
  proc procedures_duplicate;
  procedure procedures_duplicate;
  current_date_opposable text;
  has_been_prev bool;
   start_time timestamp := clock_timestamp();
  end_time timestamp;
  execution_time interval;
  i INT := 0;
BEGIN

  -- Faire un for each chaaque procédure
  -- ajouter la date de l'event qui a changer le status
  -- par la suite, si il y a un changement de status d'opposabilité par un event antérieur, la procédure reste en opposable et celle traité est alors précédent
  FOR procedure IN
    SELECT *
    FROM procedures_duplicate
    WHERE is_principale IS TRUE
  LOOP
  i := i + 1;
  RAISE LOG 'Processing procedure N: %', i;
    -- Determine new status
    FOR event IN
      SELECT *
      FROM doc_frise_events_duplicate
      WHERE procedure_id = procedure.id
      ORDER BY date_iso DESC
    LOOP
      temp := get_event_impact_dup(event, procedure.doc_type);
      IF temp IS NOT NULL THEN
        new_status := temp;
        current_date_opposable := event.date_iso;
        EXIT;
      END IF;
    END LOOP;

    -- On verifie si l'opposabilité a été ajouté
    IF new_status = 'opposable' THEN

      -- Si la procedure a un perimetre communal on met toute (normalement la seule) procedure opposable a précédent
      IF jsonb_array_length(procedure.current_perimetre) = 1 THEN
        FOR proc IN
          SELECT *
          FROM procedures_duplicate
          WHERE status = 'opposable'
          AND proc.date_opposable < current_date_opposable
          AND current_perimetre @> jsonb_build_array(jsonb_build_object('inseeCode', procedure.current_perimetre->0->>'inseeCode'))
          AND jsonb_array_length(procedure.current_perimetre) = 1
        LOOP
          RAISE LOG '[TRIGGER % UPS] PROC. COMMUNAL UPDATE TO PRECEDENT: %',TG_OP, proc.id;
          UPDATE procedures_duplicate
          SET status = 'precedent'
          WHERE id = proc.id;
          has_been_prev := true;
        END LOOP;
      ELSE
        -- On met a precedent tous les PLUi
        FOR proc IN
          SELECT *
          FROM procedures_duplicate
          WHERE status = 'opposable'
          AND proc.date_opposable < current_date_opposable
          AND collectivite_porteuse_id = procedure.collectivite_porteuse_id
          AND jsonb_array_length(current_perimetre) > 1
        LOOP
          RAISE LOG '[TRIGGER % UPS] PROC. INTER UPDATE TO PRECEDENT: %',TG_OP, proc.id;
          UPDATE procedures_duplicate
          SET status = 'precedent'
          WHERE id = proc.id;
          has_been_prev := true;
        END LOOP;
      END IF;

      -- On passe a opposable la procedure si elle a rendu précédente d'autre car ca date event opposable est plus récente que les procédure déjà traité
      UPDATE procedures_duplicate
      SET status = CASE
                    WHEN has_been_prev THEN 'opposable'
                    ELSE 'precedent'
                  END,
          date_opposable = current_date_opposable
      WHERE id = procedure.id;
    ELSE
      -- On change le status de la procédure courante si ce n'est pas de l'opposabilité
      UPDATE procedures_duplicate
        SET status = new_status
        WHERE id = procedure.id;
    END IF;
    --On remet a 0 les temp variables
    new_status := null;
    current_date_opposable := null;
    has_been_prev := false;
  END LOOP;

    -- Calculate execution time
  end_time := clock_timestamp();
  execution_time := end_time - start_time;
  -- Log execution time
  RAISE LOG 'FUNCTION ONE SHOT execution time: %', execution_time;
END;
$$ LANGUAGE plpgsql;
select one_shot_change_status();
