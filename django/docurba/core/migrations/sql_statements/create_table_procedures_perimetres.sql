CREATE TABLE public.procedures_perimetres (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    added_at timestamp with time zone DEFAULT now(),
    collectivite_code text NOT NULL,
    collectivite_type text NOT NULL,
    procedure_id uuid NOT NULL,
    opposable boolean NOT NULL,
    departement text,
    commune_id text GENERATED ALWAYS AS (((collectivite_code || '_'::text) || collectivite_type)) STORED NOT NULL
);

CREATE FUNCTION public.perimetre_by_procedures_ids_and_insee_codes(procedures_ids json, insee_codes json) RETURNS void
    LANGUAGE sql
    AS $$
        UPDATE procedures_perimetres
        SET opposable = true
        WHERE procedure_id::text IN (SELECT value FROM jsonb_array_elements_text(procedures_ids::jsonb))
        AND collectivite_code::text IN (SELECT value FROM jsonb_array_elements_text(insee_codes::jsonb))
    $$
;

CREATE FUNCTION procedures_by_collectivites(codes json)
RETURNS SETOF record
AS $$
    SELECT p.id, array_agg(pp.*) AS procedures_perimetres
    FROM procedures p
    JOIN procedures_perimetres pp ON p.id = pp.procedure_id
    WHERE p.id IN (
        SELECT procedure_id
        FROM procedures_perimetres
        WHERE collectivite_code IN (
            SELECT json_array_elements_text(codes)
        )
    ) GROUP BY p.id;
$$ LANGUAGE sql
SECURITY INVOKER;

CREATE FUNCTION public.procedures_principales_by_collectivites(codes json)
    RETURNS SETOF record
    LANGUAGE sql
    AS $$
        SELECT p.*, array_agg(pp.*) AS procedures_perimetres
        FROM procedures p
        LEFT JOIN procedures_perimetres pp ON p.id = pp.procedure_id
        WHERE ((p.id IN (
            SELECT procedure_id
            FROM procedures_perimetres
            WHERE collectivite_code IN (
                SELECT json_array_elements_text(codes)
            )
        )) AND p.is_principale = true AND p.status IN ('opposable', 'en cours')) GROUP BY p.id;
    $$
;

ALTER TABLE ONLY public.procedures_perimetres
    ADD CONSTRAINT procedures_perimetres_pkey PRIMARY KEY (id);

ALTER TABLE ONLY public.procedures_perimetres
    ADD CONSTRAINT uniq_perimeters_collectivite_procedure_type_couple_ids UNIQUE (collectivite_code, procedure_id, collectivite_type);

ALTER TABLE ONLY public.procedures_perimetres
    ADD CONSTRAINT public_procedures_perimetres_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id) ON DELETE CASCADE;

CREATE INDEX departement_idx ON public.procedures_perimetres USING btree (departement);
CREATE INDEX procedure_including_commune_idx ON public.procedures_perimetres USING btree (procedure_id) INCLUDE (commune_id);
CREATE INDEX procedures_perimetres_commune_id_idx ON public.procedures_perimetres USING btree (commune_id);
CREATE INDEX procedures_perimetres_commune_id_including_procedure ON public.procedures_perimetres USING btree (commune_id) INCLUDE (procedure_id);
CREATE INDEX test_idx ON public.procedures_perimetres USING btree (procedure_id, collectivite_code);

ALTER TABLE public.procedures_perimetres ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.procedures_perimetres FOR SELECT USING (true);

CREATE POLICY "Verified Can Delete" ON public.procedures_perimetres FOR DELETE USING ((
    SELECT profiles.verified
    FROM public.profiles
    WHERE (auth.uid() = profiles.user_id)
));

CREATE POLICY "Verified Can Insert" ON public.procedures_perimetres FOR INSERT WITH CHECK ((
    SELECT profiles.verified
    FROM public.profiles
    WHERE (auth.uid() = profiles.user_id)
));

CREATE POLICY "Verified Can Update" ON public.procedures_perimetres FOR UPDATE USING ((
    SELECT profiles.verified
    FROM public.profiles
    WHERE (auth.uid() = profiles.user_id)
));

GRANT ALL ON FUNCTION public.procedures_by_collectivites(codes json) TO anon;
GRANT ALL ON FUNCTION public.procedures_by_collectivites(codes json) TO authenticated;
GRANT ALL ON FUNCTION public.procedures_by_collectivites(codes json) TO service_role;

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures_perimetres TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures_perimetres TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures_perimetres TO service_role;

GRANT ALL ON FUNCTION public.perimetre_by_procedures_ids_and_insee_codes(procedures_ids json, insee_codes json) TO anon;
GRANT ALL ON FUNCTION public.perimetre_by_procedures_ids_and_insee_codes(procedures_ids json, insee_codes json) TO authenticated;
GRANT ALL ON FUNCTION public.perimetre_by_procedures_ids_and_insee_codes(procedures_ids json, insee_codes json) TO service_role;
