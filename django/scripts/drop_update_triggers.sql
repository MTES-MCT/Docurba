-- Pipedrive n'est pas configuré dans les recettes jetables.
drop trigger if exists "Pipedrive Sharing Update" on public.projects_sharing;
drop trigger if exists "Pipedrive Update" on public.profiles;

-- Mise à jour de la colonne `updated_at` lors de chaque modification.
drop trigger if exists "handle_updated_at" on public.doc_frise_events;
create trigger handle_updated_at before update on public.doc_frise_events
  for each row execute procedure extensions.moddatetime (updated_at);
