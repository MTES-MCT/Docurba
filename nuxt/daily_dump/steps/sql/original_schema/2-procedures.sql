CREATE TABLE procedures (
id uuid DEFAULT gen_random_uuid(),
project_id uuid,
type text,
commentaire text,
created_at timestamp with time zone,
last_updated_at timestamp with time zone,
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
archived boolean,
owner_id uuid,
previous_opposable_procedures_ids uuid,
test boolean,
type_code text,
doc_type_code text
);


ALTER TABLE public.procedures ADD CONSTRAINT procedures_pkey PRIMARY KEY (id);
ALTER TABLE public.procedures ADD CONSTRAINT procedures_previous_opposable_procedure_id_fkey FOREIGN KEY (previous_opposable_procedures_ids) REFERENCES public.procedures(id);
ALTER TABLE public.procedures ADD CONSTRAINT procedures_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);
ALTER TABLE public.procedures ADD CONSTRAINT procedures_secondary_procedure_of_fkey FOREIGN KEY (secondary_procedure_of) REFERENCES public.procedures(id);
ALTER TABLE public.procedures ADD CONSTRAINT procedures_unique_from_sudocuh UNIQUE (from_sudocuh);
