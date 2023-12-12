create or replace function previous_checker()
returns trigger
language plpgsql
as $$
declare
  original_jsonb JSONB := new->current_perimetre;
  modified_jsonb JSONB;
begin

    modified_jsonb := (
        SELECT jsonb_object_agg(key, value)
        FROM jsonb_each(original_jsonb)
        WHERE key = 'inseeCode'
    );


  RAISE LOG "UPDATE PROCEDURE %", new
  RAISE NOTICE 'Original JSONB: %', original_jsonb;
  RAISE NOTICE 'Modified JSONB: %', modified_jsonb;
  -- select *
  -- from procedures
  -- where current_perimetre  @> jsonb_build_array(new.->>'type');
end;
$$;
