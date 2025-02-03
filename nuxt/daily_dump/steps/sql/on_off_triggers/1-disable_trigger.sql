DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgrelid = 'public.doc_frise_events'::regclass
        AND tgname = 'trigger_event_procedure_status_handler'
    ) THEN
        EXECUTE 'ALTER TABLE public.doc_frise_events DISABLE TRIGGER trigger_event_procedure_status_handler';
    END IF;
END $$;
