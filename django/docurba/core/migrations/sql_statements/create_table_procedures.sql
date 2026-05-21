-- commented columns are created previously by the prod_schema_before_django_migrations.sql

ALTER TABLE public.procedures
    -- ADD COLUMN id uuid DEFAULT gen_random_uuid() NOT NULL,
    -- ADD COLUMN project_id uuid,
    ADD COLUMN type text,
    ADD COLUMN commentaire text,
    ADD COLUMN created_at timestamp with time zone DEFAULT now(),
    ADD COLUMN last_updated_at timestamp with time zone DEFAULT now(),
    ADD COLUMN from_sudocuh integer,
    ADD COLUMN collectivite_porteuse_id text,
    ADD COLUMN is_principale boolean,
    ADD COLUMN status text,
    ADD COLUMN secondary_procedure_of uuid,
    ADD COLUMN doc_type text,
    -- ADD COLUMN is_sectoriel boolean,
    ADD COLUMN is_scot boolean,
    ADD COLUMN is_pluih boolean,
    ADD COLUMN is_pdu boolean,
    ADD COLUMN mandatory_pdu boolean,
    -- ADD COLUMN moe jsonb,
    -- ADD COLUMN volet_qualitatif jsonb,
    -- ADD COLUMN sudocu_secondary_procedure_of integer,
    -- ADD COLUMN departements text[],
    ADD COLUMN current_perimetre jsonb,
    ADD COLUMN initial_perimetre jsonb,
    ADD COLUMN name text,
    -- ADD COLUMN is_sudocuh_scot boolean,
    -- ADD COLUMN testing boolean,
    ADD COLUMN numero text,
    ADD COLUMN owner_id uuid,
    -- ADD COLUMN previous_opposable_procedures_ids uuid,
    -- ADD COLUMN test boolean DEFAULT false,
    -- ADD COLUMN type_code text,
    -- ADD COLUMN doc_type_code text,
    -- ADD COLUMN comment_dgd text,
    -- ADD COLUMN shareable boolean DEFAULT false,
    -- ADD COLUMN doublon_cache_de_id uuid,
    ADD COLUMN soft_delete boolean DEFAULT false NOT NULL,
    ADD COLUMN archived boolean GENERATED ALWAYS AS (((doublon_cache_de_id IS NOT NULL) OR soft_delete)) STORED
;

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
    ADD CONSTRAINT public_procedures_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.profiles(user_id) ON DELETE SET NULL
;

CREATE INDEX idx_procedures_collectivite_porteuse_id ON public.procedures USING btree (collectivite_porteuse_id);
CREATE INDEX idx_procedures_created_at ON public.procedures USING btree (created_at);
CREATE INDEX idx_procedures_doc_type ON public.procedures USING btree (doc_type);
CREATE INDEX idx_procedures_is_principale ON public.procedures USING btree (id, is_principale, archived);
CREATE INDEX idx_procedures_is_principale_created_at ON public.procedures USING btree (is_principale, created_at);
CREATE INDEX idx_procedures_is_principale_doc_type_created_at ON public.procedures USING btree (is_principale, doc_type, created_at);
CREATE INDEX idx_procedures_secondary_procedure_of ON public.procedures USING btree (secondary_procedure_of);
CREATE UNIQUE INDEX procedures_pkey_secondary_null_not_archived ON public.procedures USING btree (id) WHERE ((secondary_procedure_of IS NULL) AND (NOT archived));

GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO anon;
GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO authenticated;
GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO service_role;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO anon;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO authenticated;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO service_role;

