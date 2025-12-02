-- Pipedrive n'est pas configuré dans les recettes jetables.
DROP TRIGGER IF EXISTS "Pipedrive Sharing Update" ON "projects_sharing";
DROP TRIGGER IF EXISTS "Pipedrive Update" ON "profiles";
