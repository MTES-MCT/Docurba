CREATE TABLE doc_frise_events (
id uuid,
project_id uuid,
type text,
date_iso character varying,
description text,
created_at timestamp with time zone,
actors json,
updated_at timestamp with time zone,
attachements json,
visibility text,
from_sudocuh integer,
is_valid boolean,
procedure_id uuid,
is_sudocuh_scot boolean,
profile_id uuid,
test boolean,
code text,
from_sudocuh_procedure_id integer
);
ALTER TABLE public.doc_frise_events ADD CONSTRAINT doc_frise_events_pkey PRIMARY KEY (id);
ALTER TABLE public.doc_frise_events ADD CONSTRAINT doc_frise_events_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);
ALTER TABLE public.doc_frise_events ADD CONSTRAINT public_doc_frise_events_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id);
