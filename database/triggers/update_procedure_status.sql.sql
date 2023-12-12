create or replace function update_procedure_status()
returns trigger
language plpgsql
as $$
declare
  event_processed doc_frise_events;
  curr_procedure_id uuid;
  procedure_doc_type text ;
  new_status text;
  temp text;
  event doc_frise_events;

begin
  if TG_OP = 'DELETE' then
    event_processed := old;
  else
    event_processed := new;
  end if;

  select  id, doc_type, status into curr_procedure_id, procedure_doc_type, new_status
  from procedures
  where id = event_processed.procedure_id;

  for event in
    select *
    from doc_frise_events
    where procedure_id = event_processed.procedure_id
    order by date_iso desc
  loop
    temp := get_event_impact(event, procedure_doc_type);
    RAISE LOG 'LOOP TEMP: % - % - DOC TYPE: %', temp, event.type, procedure_doc_type;
    if temp is not null then
      new_status := temp;
      exit;
    end if;
  end loop;
  RAISE LOG 'NEW STATUS DELETE: %', new_status;

  UPDATE procedures
  SET status = new_status
  WHERE id = curr_procedure_id;
  RAISE LOG 'UPATED % WITH NEW STATUS: %', curr_procedure_id, new_status;
  return event_processed;
end;
$$;
