CREATE OR REPLACE FUNCTION update_procedure_status()
RETURNS TRIGGER AS $$
DECLARE
  event_processed doc_frise_events;
  curr_procedure_id uuid;
  procedure_doc_type text;
  new_status text;
  curr_status text;
  temp text;
  event doc_frise_events;
  curr_procedure_perimetre jsonb;
  curr_procedure_collec_porteuse text;
  proc procedures;
  temp_previous_opposables_procedures_ids uuid[];
  curr_previous_opposable_procedures_ids uuid[];
  prev_proc_opp_id uuid;
  commune jsonb;
BEGIN
RAISE LOG '[TRIGGER UPS START] ACTION: %', TG_OP;
  --TODO: Review the DELETE and UPDATE
  IF TG_OP = 'DELETE' OR TG_OP = 'UPDATE' THEN
    -- Retrieve procedure of the deleted event
    SELECT id, doc_type, status, current_perimetre, collectivite_porteuse_id, previous_opposable_procedures_ids
    INTO curr_procedure_id, procedure_doc_type, curr_status, curr_procedure_perimetre, curr_procedure_collec_porteuse, curr_previous_opposable_procedures_ids
    FROM procedures
    WHERE id = old.procedure_id;

    -- Determine new status
    FOR event IN
      SELECT *
      FROM doc_frise_events
      WHERE procedure_id = old.procedure_id
      ORDER BY date_iso DESC
    LOOP
      temp := get_event_impact(event, procedure_doc_type);
      RAISE LOG '[TRIGGER % UPS] LOOP TEMP: % - % - DOC TYPE: %', TG_OP, temp, event.type, procedure_doc_type;
      IF temp IS NOT NULL THEN
        new_status := temp;
        EXIT;
      END IF;
    END LOOP;
    RAISE LOG '[TRIGGER % UPS] curr_status: % - new_status: %',TG_OP, curr_status, new_status;
    -- On verifie si l'opposabilité a été supprimé
    IF curr_status = 'opposable' AND (new_status IS NULL OR new_status <> 'opposable') THEN
      RAISE LOG '[TRIGGER % UPS] DELETE AN OPPOSABLE EVENT', TG_OP;

        --TODO: Dans ce cas, très simple, la procedure courante passe précédente et toutes les procedures contenu dans previous_opposable_ids passent en opposable (et on set leur propre previous_opposable a l'id de la courante)

      --TODO: surement moyen de faire l'update directement sans boucle
      UPDATE procedures
        SET status = 'en cours'
        WHERE id = curr_procedure_id;

      FOR prev_proc_opp_id IN
        SELECT * FROM unnest(curr_previous_opposable_procedures_ids)
      LOOP
        UPDATE procedures
          SET status = 'opposable'
          WHERE id = prev_proc_opp_id;
      END LOOP;

    END IF;
  END IF;

  IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
  RAISE LOG '[TRIGGER UPS] ENTERING CONDITION';
    -- Retrieve procedure of the inserted event
    SELECT id, doc_type, status, current_perimetre, collectivite_porteuse_id
    INTO curr_procedure_id, procedure_doc_type, curr_status, curr_procedure_perimetre, curr_procedure_collec_porteuse
    FROM procedures
    WHERE id = new.procedure_id;

    -- Determine new status
    FOR event IN
      SELECT *
      FROM doc_frise_events
      WHERE procedure_id = new.procedure_id
      ORDER BY date_iso DESC
    LOOP
      temp := get_event_impact(event, procedure_doc_type);
      IF temp IS NOT NULL THEN
        new_status := temp;
        EXIT;
      END IF;
    END LOOP;

    RAISE LOG '[TRIGGER % UPS] curr_status: % - new_status: %',TG_OP, curr_status, new_status;
    -- On verifie si l'opposabilité a été ajouté
    IF curr_status <> 'opposable' AND new_status = 'opposable' THEN
    RAISE LOG '[TRIGGER % UPS] INSERT AN NEW OPPOSABLE EVENT', TG_OP ;
      -- Si la procedure a un perimetre communal on met toute (normalement la seule) procedure opposable a précédent
      RAISE LOG '[TRIGGER UPS] curr_procedure_perimetre: % -- %',  curr_procedure_perimetre, jsonb_array_length(curr_procedure_perimetre);
      IF jsonb_array_length(curr_procedure_perimetre) = 1 THEN
        FOR proc IN
          SELECT *
          FROM procedures
          WHERE status = 'opposable'
          AND current_perimetre @> jsonb_build_array(jsonb_build_object('inseeCode', curr_procedure_perimetre->0->>'inseeCode'))
          AND jsonb_array_length(curr_procedure_perimetre) = 1
        LOOP
          RAISE LOG '[TRIGGER % UPS] PROC. COMMUNAL UPDATE TO PRECEDENT: %',TG_OP, proc.id;
          UPDATE procedures
          SET status = 'precedent'
          WHERE id = proc.id;

          --On concat tous les ids de procedures precedentes dans un tableau
          temp_previous_opposables_procedures_ids := temp_previous_opposables_procedures_ids || ARRAY[proc.id];
        END LOOP;
        RAISE LOG '[TRIGGER % UPS] temp_previous_opposables_procedures_ids: %',TG_OP, temp_previous_opposables_procedures_ids;
      ELSE
        -- On met a precedent tous les PLUi
        FOR proc IN
          SELECT *
          FROM procedures
          WHERE status = 'opposable'
          AND collectivite_porteuse_id = curr_procedure_collec_porteuse
          AND jsonb_array_length(current_perimetre) > 1
        LOOP
          RAISE LOG '[TRIGGER % UPS] PROC. INTER UPDATE TO PRECEDENT: %',TG_OP, proc.id;
          UPDATE procedures
          SET status = 'precedent'
          WHERE id = proc.id;

          --On concat tous les ids de procedures precedentes dans un tableau
          temp_previous_opposables_procedures_ids := temp_previous_opposables_procedures_ids || ARRAY[proc.id];
        END LOOP;

        WITH updated_procedures_cte AS (
            UPDATE procedures
            SET status = CASE
                            WHEN status = 'en cours' THEN 'abandon'
                            WHEN status = 'opposable' THEN 'precedent'
                            ELSE status
                        END
            WHERE (status = 'en cours' OR status = 'opposable')
                AND jsonb_array_length(current_perimetre) = 1
                AND EXISTS (
                    SELECT 1
                    FROM jsonb_array_elements(curr_procedure_perimetre) AS communecte
                    WHERE jsonb_exists(communecte, 'inseeCode')
                        AND current_perimetre @> jsonb_build_array(jsonb_build_object('inseeCode', communecte->>'inseeCode'))
                )
            RETURNING id, status
        )
        SELECT ARRAY_CAT(temp_previous_opposables_procedures_ids, ARRAY_AGG(id)) INTO temp_previous_opposables_procedures_ids
        FROM updated_procedures_cte
        WHERE status = 'precedent';
      END IF;

      -- On passe a opposable la procedure courante
      UPDATE procedures
        SET status = 'opposable', previous_opposable_procedures_ids = temp_previous_opposables_procedures_ids
        WHERE id = curr_procedure_id;
      --RAISE LOG '[TRIGGER % UPS] UPATED % WITH NEW STATUS: %',TG_OP, curr_procedure_id, new_status;
    END IF;
  END IF;
  RETURN COALESCE(new, old);
END;
$$ LANGUAGE plpgsql;
