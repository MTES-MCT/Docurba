CREATE TABLE public.projects (
    created_at timestamp with time zone DEFAULT now(),
    name character varying,
    doc_type character varying NOT NULL,
    region character varying,
    "PAC" jsonb,
    owner uuid,
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    towns jsonb,
    epci jsonb,
    trame character varying,
    archived boolean DEFAULT false NOT NULL,
    sudocuh_procedure_id integer,
    collectivite_id text,
    from_sudocuh integer,
    current_perimetre jsonb[],
    initial_perimetre jsonb[],
    collectivite_porteuse_id text,
    is_sudocuh_scot boolean,
    current_perimetre_new jsonb,
    test boolean,
    doc_type_code text,
    from_sudocuh_procedure_id integer
);

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_from_sudocuh_key UNIQUE (from_sudocuh),
    ADD CONSTRAINT projects_from_sudocuh_procedure_id_key UNIQUE (from_sudocuh_procedure_id),
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id),
    ADD CONSTRAINT public_projects_owner_fkey FOREIGN KEY (owner) REFERENCES public.profiles(user_id) ON DELETE SET NULL;


CREATE POLICY "Enable insert for authenticated users only" ON public.projects FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

CREATE POLICY "Enable read for users" ON public.projects FOR SELECT USING (true);

CREATE POLICY "Enable update for users verified" ON public.projects FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id))) WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


CREATE POLICY "Update" ON public.projects_sharing FOR UPDATE USING (((auth.uid() = shared_by) AND (auth.uid() = ( SELECT projects.owner
   FROM public.projects
  WHERE (projects.id = projects_sharing.project_id))))) WITH CHECK (((auth.uid() = shared_by) AND (auth.uid() = ( SELECT projects.owner
   FROM public.projects
  WHERE (projects.id = projects_sharing.project_id)))));


ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects TO service_role;



-------------------------------------
----------- OTHER TABLES ------------
-------------------------------------
-- These modifications are here because they depend on the projects table.


-- CREATE POLICY "Delete" ON public.projects_sharing FOR DELETE USING ((public.is_admin(auth.uid()) OR (((auth.uid() = shared_by) OR (shared_by IS NULL)) AND ((auth.uid() = ( SELECT projects.owner
--    FROM public.projects
--   WHERE (projects.id = projects_sharing.project_id))) OR (EXISTS ( SELECT 1
--    FROM (public.projects p
--      JOIN public.profiles prof ON ((prof.user_id = auth.uid())))
--   WHERE ((p.id = projects_sharing.project_id) AND (prof.departement = (p.trame)::text)))) OR public.check_project_sharing_permission(project_id, (auth.jwt() ->> 'email'::text))))));


-- The `auth.jwt()` function does not exist. It is installed by the `auth` Supabase service.
-- See https://github.com/supabase/auth/blob/master/migrations/00_init_auth_schema.up.sql
--
-- Name: projects_sharing Insert; Type: POLICY; Schema: public; Owner: -
--

-- CREATE POLICY "Insert" ON public.projects_sharing FOR INSERT WITH CHECK ((public.is_admin(auth.uid()) OR ((auth.uid() = shared_by) AND ((auth.uid() = ( SELECT projects.owner
--    FROM public.projects
--   WHERE (projects.id = projects_sharing.project_id))) OR (EXISTS ( SELECT 1
--    FROM (public.projects p
--      JOIN public.profiles prof ON ((prof.user_id = auth.uid())))
--   WHERE ((p.id = projects_sharing.project_id) AND (prof.departement = (p.trame)::text)))) OR public.check_project_sharing_permission(project_id, (auth.jwt() ->> 'email'::text))))));


ALTER TABLE ONLY public.pac_sections_project
    ADD CONSTRAINT pac_sections_project_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);

ALTER TABLE ONLY public.projects_sharing
    ADD CONSTRAINT "projectsSharing_project_id_fkey" FOREIGN KEY (project_id) REFERENCES public.projects(id);
