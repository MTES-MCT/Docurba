-- Obligatoire pour toute nouvelle branche Supabase.
-- https://stackoverflow.com/a/73107153
grant usage on schema public to postgres, anon, authenticated, service_role;
grant usage on schema extensions to postgres, anon, authenticated, service_role;

grant all privileges on all tables in schema public to postgres, anon, authenticated, service_role, supabase_admin;
grant all privileges on all functions in schema public to postgres, anon, authenticated, service_role, supabase_admin;
grant all privileges on all sequences in schema public to postgres, anon, authenticated, service_role, supabase_admin;

alter default privileges in schema public grant all on tables to postgres, anon, authenticated, service_role;
alter default privileges in schema public grant all on functions to postgres, anon, authenticated, service_role;
alter default privileges in schema public grant all on sequences to postgres, anon, authenticated, service_role;

alter role anon set statement_timeout = '3s';
alter role authenticated set statement_timeout = '8s';

-- https://supabase.com/docs/guides/troubleshooting/refresh-postgrest-schema
notify pgrst, 'reload schema';
