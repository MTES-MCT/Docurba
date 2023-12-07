create or replace function TEST_update_procedure_status()
returns trigger
language plpgsql
as $$
declare
  event_processed doc_frise_events;
  curr_procedure_id uuid;
  procedure_doc_type text ;
  new_status text;
  event doc_frise_events;

begin
  if TG_OP = 'DELETE' then
    event_processed := old;
  end if;

  select  id, doc_type, status into curr_procedure_id, procedure_doc_type, new_status
  from procedures
  where id = old.procedure_id;

  for event in
    select *
    from doc_frise_events
    where procedure_id = old.procedure_id
    order by date_iso desc
  loop
    new_status := COALESCE(get_event_impact(event, procedure_doc_type), new_status);
  end loop;
  RAISE LOG 'NEW STATUS DELETE: %', new_status;
  return old;
end;
$$;
