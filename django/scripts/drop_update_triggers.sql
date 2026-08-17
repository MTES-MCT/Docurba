-- Pipedrive n'est pas configuré dans les recettes jetables.
drop trigger if exists "Pipedrive Sharing Update" on public.projects_sharing;
drop trigger if exists "Pipedrive Update" on public.profiles;
