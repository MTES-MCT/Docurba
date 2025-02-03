DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgrelid = 'public.doc_frise_events'::regclass
        AND tgname = 'trigger_event_procedure_status_handler'
    ) THEN
        EXECUTE 'CREATE TRIGGER trigger_event_procedure_status_handler
            AFTER INSERT OR DELETE OR UPDATE ON public.doc_frise_events
            FOR EACH ROW EXECUTE FUNCTION event_procedure_status_handler()';
    END IF;
END $$;
