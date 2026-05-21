-- commented columns are created previously by the prod_schema_before_django_migrations.sql
DROP TRIGGER handle_updated_at ON public.doc_frise_events;
DROP TRIGGER trigger_event_procedure_status_handler ON public.doc_frise_events;

DROP FUNCTION public.set_procedure_status;
DROP FUNCTION public.get_event_impact;
DROP FUNCTION public.event_procedure_status_handler;
DROP FUNCTION public.events_by_procedures_ids;
DROP FUNCTION public.get_event_status;
DROP FUNCTION public.one_shot_events;
DROP FUNCTION public.procedure_status_handler;

DROP POLICY "Users Can Read" ON public.doc_frise_events;
DROP POLICY "Verified Can insert" ON public.doc_frise_events;
DROP POLICY "Verified Can Update Events" ON public.doc_frise_events;
DROP POLICY "Verified Can delete event" ON public.doc_frise_events;


ALTER TABLE public.doc_frise_events
    -- DROP COLUMN id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    -- DROP COLUMN project_id uuid,
    DROP COLUMN type,
    DROP COLUMN date_iso,
    -- DROP COLUMN description,
    -- DROP COLUMN created_at,
    -- DROP COLUMN actors,
    -- DROP COLUMN updated_at,
    -- DROP COLUMN attachements,
    DROP COLUMN visibility ,
    -- DROP COLUMN from_sudocuh,
    DROP COLUMN is_valid,
    DROP COLUMN procedure_id,
    -- DROP COLUMN is_sudocuh_scot,
    DROP COLUMN profile_id
    -- DROP COLUMN test boolean,
    -- DROP COLUMN code,
    -- DROP COLUMN from_sudocuh_procedure_id
;
