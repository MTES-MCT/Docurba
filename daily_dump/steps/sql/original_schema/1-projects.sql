CREATE TABLE projects (
created_at timestamp with time zone,
name character varying,
doc_type character varying,
region character varying,
PAC jsonb,
owner uuid,
id uuid,
towns jsonb,
epci jsonb,
trame character varying,
archived boolean,
sudocuh_procedure_id integer,
collectivite_id text,
from_sudocuh integer,
current_perimetre text[],
initial_perimetre text[],
collectivite_porteuse_id text,
is_sudocuh_scot boolean,
current_perimetre_new jsonb,
test boolean,
doc_type_code text,
from_sudocuh_procedure_id integer
);

ALTER TABLE public.projects ADD CONSTRAINT projects_pkey PRIMARY KEY (id);
