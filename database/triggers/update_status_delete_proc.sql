CREATE OR REPLACE FUNCTION update_status_delete_proc()
RETURNS TRIGGER AS $$
DECLARE
  prev_proc_opp_id uuid;
BEGIN
RAISE LOG '[TRIGGER DELETE PROC.] % ', TG_OP;
  IF TG_OP = 'UPDATE' AND  new.archived IS TRUE THEN
    IF old.status = 'opposable' THEN
      RAISE LOG '[TRIGGER DELETE PROC.] DELETE AN OPPOSABLE PROCEDURE ID: %', old.id;
      UPDATE procedures
      SET archived = true
      WHERE id = old.id;

      FOR prev_proc_opp_id IN
        SELECT * FROM unnest(old.previous_opposable_procedures_ids)
      LOOP
        RAISE LOG 'OLD PROCEDURE % PASSING BACK TO OPPOSABLE: ', prev_proc_opp_id;
        UPDATE procedures
          SET status = 'opposable'
          WHERE id = prev_proc_opp_id;
      END LOOP;
    END IF;
  END IF;
  RETURN new;
END;
$$ LANGUAGE plpgsql;
