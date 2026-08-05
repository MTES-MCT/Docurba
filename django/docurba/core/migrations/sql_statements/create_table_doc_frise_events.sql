-- commented columns are created previously by the prod_schema_before_django_migrations.sql

CREATE TABLE public.doc_frise_events (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    project_id uuid,
    type text,
    date_iso date,
    description text,
    created_at timestamp with time zone DEFAULT now(),
    actors json,
    updated_at timestamp with time zone DEFAULT now(),
    attachements json,
    visibility text DEFAULT 'public'::text,
    from_sudocuh integer,
    is_valid boolean DEFAULT true NOT NULL,
    procedure_id uuid,
    is_sudocuh_scot boolean,
    profile_id uuid,
    test boolean DEFAULT false,
    code text,
    from_sudocuh_procedure_id integer
);


CREATE INDEX aaaaa ON public.doc_frise_events USING btree (procedure_id, date_iso DESC, type, is_valid); -- ok
CREATE INDEX doc_frise_events_profile_id_idx ON public.doc_frise_events USING btree (profile_id); -- OK
CREATE INDEX idx_doc_frise_events_procedure_id ON public.doc_frise_events USING btree (procedure_id); -- ok
CREATE INDEX idx_doc_frise_events_procedure_id_date_iso ON public.doc_frise_events USING btree (procedure_id, date_iso DESC); -- OK
CREATE INDEX test_index ON public.doc_frise_events USING btree (procedure_id, date_iso); -- removed

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT doc_frise_events_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(user_id),
    ADD CONSTRAINT public_doc_frise_events_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id) ON DELETE CASCADE,
    ADD CONSTRAINT doc_frise_events_from_sudocuh_key UNIQUE (from_sudocuh),
    ADD CONSTRAINT doc_frise_events_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id),
    ADD CONSTRAINT doc_frise_events_pkey PRIMARY KEY (id);

CREATE POLICY "Users Can Read" ON public.doc_frise_events FOR SELECT USING (true);

CREATE POLICY "Verified Can insert" ON public.doc_frise_events FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

CREATE POLICY "Verified Can Update Events" ON public.doc_frise_events FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

CREATE POLICY "Verified Can delete event" ON public.doc_frise_events FOR DELETE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


ALTER TABLE public.doc_frise_events ENABLE ROW LEVEL SECURITY;


GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO service_role;
