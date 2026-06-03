-- commented columns are created previously by the prod_schema_before_django_migrations.sql

CREATE TABLE public.procedures (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid,
    type text,
    commentaire text,
    created_at timestamp with time zone DEFAULT now(),
    last_updated_at timestamp with time zone DEFAULT now(),
    from_sudocuh integer,
    collectivite_porteuse_id text,
    is_principale boolean,
    status text,
    secondary_procedure_of uuid,
    doc_type text,
    is_sectoriel boolean,
    is_scot boolean,
    is_pluih boolean,
    is_pdu boolean,
    mandatory_pdu boolean,
    moe jsonb,
    volet_qualitatif jsonb,
    sudocu_secondary_procedure_of integer,
    departements text[],
    current_perimetre jsonb,
    initial_perimetre jsonb,
    name text,
    is_sudocuh_scot boolean,
    testing boolean,
    numero text,
    owner_id uuid,
    previous_opposable_procedures_ids uuid,
    test boolean DEFAULT false,
    type_code text,
    doc_type_code text,
    comment_dgd text,
    shareable boolean DEFAULT false,
    doublon_cache_de_id uuid,
    soft_delete boolean DEFAULT false NOT NULL,
    archived boolean GENERATED ALWAYS AS (((doublon_cache_de_id IS NOT NULL) OR soft_delete)) STORED
);

CREATE FUNCTION public.procedures_by_insee_codes(codes json) RETURNS SETOF record
    LANGUAGE sql
    AS $$
SELECT *
FROM procedures
WHERE EXISTS (
  SELECT id, status, doc_type, current_perimetre, is_pluih
  FROM jsonb_array_elements(current_perimetre) obj
  WHERE ((obj->>'inseeCode')::text IN (
    SELECT jsonb_array_elements_text(codes::jsonb)
  )) and (status in ('opposable', 'en cours')) and (is_principale = true)
);
$$;

CREATE FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) RETURNS SETOF record
    LANGUAGE sql
    AS $$
SELECT id, from_sudocuh, initial_perimetre, current_perimetre, status
FROM procedures
WHERE from_sudocuh::text IN (SELECT value FROM jsonb_array_elements_text(sudocuh_ids::jsonb));
$$;

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_from_sudocuh_key UNIQUE (from_sudocuh),
    ADD CONSTRAINT procedures_secondary_procedure_of_fkey FOREIGN KEY (secondary_procedure_of) REFERENCES public.procedures(id),
    ADD CONSTRAINT public_procedures_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.profiles(user_id) ON DELETE SET NULL,
    ADD CONSTRAINT procedures_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE,
    ADD CONSTRAINT procedures_pkey PRIMARY KEY (id),
    ADD CONSTRAINT procedures_doublon_cache_de_id_fkey FOREIGN KEY (doublon_cache_de_id) REFERENCES public.procedures(id) ON UPDATE CASCADE ON DELETE RESTRICT, -- not present on the Procedure model.
    ADD CONSTRAINT procedures_previous_opposable_procedure_id_fkey FOREIGN KEY (previous_opposable_procedures_ids) REFERENCES public.procedures(id),
    ADD CONSTRAINT procedures_doublon_cache_de_id_key UNIQUE (doublon_cache_de_id)
;

CREATE INDEX idx_procedures_collectivite_porteuse_id ON public.procedures USING btree (collectivite_porteuse_id);
CREATE INDEX idx_procedures_created_at ON public.procedures USING btree (created_at);
CREATE INDEX idx_procedures_doc_type ON public.procedures USING btree (doc_type);
CREATE INDEX idx_procedures_is_principale ON public.procedures USING btree (id, is_principale, archived);
CREATE INDEX idx_procedures_is_principale_created_at ON public.procedures USING btree (is_principale, created_at);
CREATE INDEX idx_procedures_is_principale_doc_type_created_at ON public.procedures USING btree (is_principale, doc_type, created_at);
CREATE INDEX idx_procedures_secondary_procedure_of ON public.procedures USING btree (secondary_procedure_of);
CREATE UNIQUE INDEX procedures_pkey_secondary_null_not_archived ON public.procedures USING btree (id) WHERE ((secondary_procedure_of IS NULL) AND (NOT archived));
CREATE INDEX idx_project_id ON public.procedures USING btree (project_id);


GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO anon;
GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO authenticated;
GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO service_role;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO anon;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO authenticated;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO service_role;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures TO service_role;


ALTER TABLE ONLY public.procedures_validations
    ADD CONSTRAINT procedures_validations_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id);

ALTER TABLE ONLY public.versements
    ADD CONSTRAINT versements_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id);


CREATE POLICY "Users Can Read" ON public.procedures FOR SELECT USING (true);

CREATE POLICY "Verified Can Delete" ON public.procedures FOR DELETE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

CREATE POLICY "Verified Can Insert" ON public.procedures FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

CREATE POLICY "Verified Can Update" ON public.procedures FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


ALTER TABLE public.procedures ENABLE ROW LEVEL SECURITY;
