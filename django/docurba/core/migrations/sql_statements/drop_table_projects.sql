
ALTER TABLE public.pac_sections_project
    DROP CONSTRAINT pac_sections_project_project_id_fkey;

ALTER TABLE public.prescriptions
    DROP CONSTRAINT prescriptions_project_id_fkey;

ALTER TABLE public.projects_sharing
    DROP CONSTRAINT "projectsSharing_project_id_fkey";

DROP POLICY "Update" ON public.projects_sharing;

DROP TABLE public.projects;
