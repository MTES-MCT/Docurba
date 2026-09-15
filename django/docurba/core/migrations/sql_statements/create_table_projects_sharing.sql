CREATE TABLE public.projects_sharing (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    user_email text NOT NULL,
    project_id uuid NOT NULL,
    shared_by uuid,
    notified boolean DEFAULT false NOT NULL,
    last_update_notification timestamp without time zone DEFAULT now() NOT NULL,
    role character varying DEFAULT 'read'::character varying,
    archived boolean DEFAULT false NOT NULL,
    dev_test boolean DEFAULT false,
    inserted_script boolean DEFAULT false,
    email_notified boolean DEFAULT false NOT NULL
);

COMMENT ON COLUMN public.projects_sharing.last_update_notification IS 'Timestamp of last notification';

ALTER TABLE ONLY public.projects_sharing
    ADD CONSTRAINT "projectsSharing_pkey" PRIMARY KEY (id),
    ADD CONSTRAINT "projectsSharing_project_id_fkey" FOREIGN KEY (project_id) REFERENCES public.projects(id),
    ADD CONSTRAINT unique_project_sharing UNIQUE (user_email, project_id, role),
    ADD CONSTRAINT public_projects_sharing_shared_by_fkey FOREIGN KEY (shared_by) REFERENCES public.profiles(user_id) ON UPDATE CASCADE ON DELETE CASCADE;

CREATE POLICY "Update" ON public.projects_sharing FOR UPDATE USING (((auth.uid() = shared_by) AND (auth.uid() = ( SELECT projects.owner
   FROM public.projects
  WHERE (projects.id = projects_sharing.project_id))))) WITH CHECK (((auth.uid() = shared_by) AND (auth.uid() = ( SELECT projects.owner
   FROM public.projects
  WHERE (projects.id = projects_sharing.project_id)))));

CREATE FUNCTION public.check_project_sharing_permission(project_id uuid, user_email text) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM projects_sharing ps
    WHERE ps.project_id = check_project_sharing_permission.project_id
      AND ps.role = 'write_frise'
      AND ps.user_email = check_project_sharing_permission.user_email
  );
END;
$$;


CREATE POLICY "Read" ON public.projects_sharing FOR SELECT USING ((public.is_admin(auth.uid()) OR public.check_user_access()));

ALTER TABLE public.projects_sharing ENABLE ROW LEVEL SECURITY;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects_sharing TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects_sharing TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects_sharing TO service_role;

--
-- Name: projects_sharing Pipedrive Sharing Update; Type: TRIGGER; Schema: public; Owner: -
--

-- CREATE TRIGGER "Pipedrive Sharing Update" AFTER INSERT ON public.projects_sharing FOR EACH ROW EXECUTE FUNCTION supabase_functions.http_request('pipedrive/sharing', 'POST', '{"Content-type":"application/json"}', '{}', '10000');

-- The `auth.jwt()` function does not exist. It is installed by the `auth` Supabase service.
-- See https://github.com/supabase/auth/blob/master/migrations/00_init_auth_schema.up.sql
--
-- Name: projects_sharing Delete; Type: POLICY; Schema: public; Owner: -
--
