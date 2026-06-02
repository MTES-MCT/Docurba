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

DROP TABLE IF EXISTS public.doc_frise_events;
