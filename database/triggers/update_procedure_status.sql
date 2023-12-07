
create or replace function update_procedure_status()
returns trigger
language plpgsql
as $$
declare
  curr_procedure_id uuid;
  procedure_doc_type text ;
  new_status text;
begin

  select  id, doc_type, status into curr_procedure_id, procedure_doc_type, new_status
  from procedures
  where id = new.procedure_id;

  if procedure_doc_type ILIKE 'PLU%' then
    procedure_doc_type = 'PLU';
  end if;

  new_status := COALESCE(get_event_impact(new, procedure_doc_type), new_status);
  RAISE LOG 'NEW STATUS: %', new_status;

  UPDATE procedures
  SET status = new_status
  WHERE id = curr_procedure_id;

  return new;
end;
$$;


