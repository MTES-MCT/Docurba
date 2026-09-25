
ALTER TABLE public.pac_sections_project
    DROP CONSTRAINT pac_sections_project_project_id_fkey;

ALTER TABLE public.prescriptions
    DROP CONSTRAINT prescriptions_project_id_fkey;

DROP TABLE public.projects;
