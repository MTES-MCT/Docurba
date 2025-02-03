CREATE TABLE procedures_perimetres (
id uuid DEFAULT gen_random_uuid(),
created_at timestamp with time zone,
added_at timestamp with time zone,
collectivite_code text,
collectivite_type text,
procedure_id uuid,
opposable boolean,
departement text
);

ALTER TABLE public.procedures_perimetres ADD CONSTRAINT procedures_perimetres_pkey PRIMARY KEY (id);
ALTER TABLE public.procedures_perimetres ADD CONSTRAINT public_procedures_perimetres_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id);
