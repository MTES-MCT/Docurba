-- Pipedrive n'est pas configuré dans les recettes jetables.
DROP TRIGGER IF EXISTS "Pipedrive Sharing Update" ON public.projects_sharing;
DROP TRIGGER IF EXISTS "Pipedrive Update" ON public.profiles;
