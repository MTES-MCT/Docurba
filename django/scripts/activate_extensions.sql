create extension if not exists moddatetime schema extensions;
create extension if not exists pg_net schema extensions;

-- https://supabase.com/docs/guides/troubleshooting/refresh-postgrest-schema
notify pgrst, 'reload schema';
