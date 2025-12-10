-- Mise à jour de la colonne `updated_at` lors de chaque modification.
create extension if not exists moddatetime schema extensions;
DROP TRIGGER IF EXISTS "handle_updated_at" ON public.doc_frise_events;
create trigger handle_updated_at before update on public.doc_frise_events
  for each row execute procedure moddatetime (updated_at);

-- Pipedrive n'est pas configuré dans les recettes jetables.
DROP TRIGGER IF EXISTS "Pipedrive Sharing Update" ON public.projects_sharing;
DROP TRIGGER IF EXISTS "Pipedrive Update" ON public.profiles;
