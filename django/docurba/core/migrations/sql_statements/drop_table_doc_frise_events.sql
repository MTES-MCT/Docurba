-- commented columns are created previously by the prod_schema_before_django_migrations.sql
DROP POLICY "Users Can Read" ON public.doc_frise_events;
DROP POLICY "Verified Can insert" ON public.doc_frise_events;
DROP POLICY "Verified Can Update Events" ON public.doc_frise_events;
DROP POLICY "Verified Can delete event" ON public.doc_frise_events;

DROP TABLE IF EXISTS public.doc_frise_events;
