-- commented columns are created previously by the prod_schema_before_django_migrations.sql

CREATE TABLE public.doc_frise_events (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    project_id uuid,
    type text,
    date_iso date,
    description text,
    created_at timestamp with time zone DEFAULT now(),
    actors json,
    updated_at timestamp with time zone DEFAULT now(),
    attachements json,
    visibility text DEFAULT 'public'::text,
    from_sudocuh integer,
    is_valid boolean DEFAULT true NOT NULL,
    procedure_id uuid,
    is_sudocuh_scot boolean,
    profile_id uuid,
    test boolean DEFAULT false,
    code text,
    from_sudocuh_procedure_id integer
);


CREATE FUNCTION public.set_procedure_status(procedure public.procedures) RETURNS void
    LANGUAGE plpgsql
    AS $$ DECLARE new_status text; event doc_frise_events; current_date_opposable text; BEGIN FOR event IN SELECT * FROM doc_frise_events WHERE procedure_id = procedure.id AND (is_valid = true OR type = 'Abandon') ORDER BY date_iso DESC, type LOOP new_status := get_event_impact(event, procedure.doc_type); IF new_status = 'opposable' THEN current_date_opposable := event.date_iso; END IF; IF new_status IS NOT null then EXIT; END IF; END LOOP; IF new_status IS NULL THEN new_status := 'en cours'; END IF; UPDATE procedures SET status = new_status WHERE id = procedure.id; current_date_opposable := null; new_status := null; END; $$;


CREATE FUNCTION public.one_shot_events() RETURNS void
    LANGUAGE plpgsql
    AS $$ DECLARE procedure procedures; start_time timestamp := clock_timestamp(); end_time timestamp; execution_time interval; i INT := 0; BEGIN RAISE LOG 'Processing One shot events'; UPDATE procedures SET status = null; FOR procedure IN SELECT * FROM procedures WHERE is_principale IS TRUE LOOP i := i + 1; RAISE LOG 'Processing procedure events N: %', i; PERFORM set_procedure_status(procedure); END LOOP; end_time := clock_timestamp(); execution_time := end_time - start_time; RAISE LOG 'FUNCTION ONE SHOT execution time: %', execution_time; END; $$;


CREATE FUNCTION public.procedure_status_handler() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
declare
procedure procedures;
BEGIN
  IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then
    procedure := new;
  else
    procedure := old;
  END IF;

  PERFORM set_procedure_status(procedure);

  -- Perform the HTTP GET request
  -- TODO(cms): API call is disabled here because Nuxt3 does not listen on test mode.
  -- PERFORM http_get('localhost:4000/api/urba/procedures/' || procedure.id || '/update');
  return procedure;
END;
$$;


CREATE FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) RETURNS text
    LANGUAGE plpgsql
    AS $$ declare is_opposable_event bool; is_caduc_event bool; is_abandon_event bool; is_ongoing_event bool; is_annule_event bool; new_status text := NULL; impactful_events jsonb := '{ "CC": { "en cours": ["Délibération de prescription du conseil municipal"], "opposable": ["Approbation du préfet", "Caractère exécutoire", "Retrait de l''annulation totale"], "abandon": ["Abandon", "Retrait de la délibération de prescription"], "annule": ["Annulation TA totale", "Annulation TA", "Abrogation effective"], "caduc": [] }, "SCOT": { "en cours": ["Délibération de l''établissement public qui prescrit", "Retrait de la délibération d''approbation"], "opposable": ["Délibération d''approbation", "Caractère exécutoire", "Retrait de l''annulation totale"], "abandon": ["Abandon", "Retrait de la délibération de prescription"], "annule": ["Annulation TA totale", "Annulation TA"], "caduc": ["Caducité"] }, "SD": { "en cours": ["Délibération de l''établissement public qui prescrit"], "opposable": ["Délibération d''approbation", "Caractère exécutoire"], "abandon": ["Abandon"], "annule": ["Annulation TA totale", "Annulation TA"], "caduc": ["Caducité"] }, "PLU": { "en cours": ["Délibération de prescription du conseil municipal ou communautaire"], "opposable": ["Caractère exécutoire", "Retrait de l''annulation totale", "Délibération d''approbation du municipal ou communautaire", "Délibération d''approbation du conseil municipal ou communautaire", "Délibération d''approbation"], "abandon": ["Abandon", "Retrait de la délibération de prescription"], "annule": ["Annulation TA totale", "Annulation TA", "Abrogation", "Arrêté d''abrogation"], "caduc": ["Caducité"] }, "POS": { "en cours": ["Délibération de prescription du conseil municipal ou communautaire"], "opposable": ["Caractère exécutoire", "Délibération d''approbation du municipal ou communautaire", "Délibération d''approbation du conseil municipal ou communautaire", "Délibération d''approbation"], "abandon": ["Abandon"], "annule": ["Annulation TA", "Annulation TA totale", "Caducité"], "caduc": [] } }'; begin if doc_type ILIKE 'PLU%' then doc_type := 'PLU'; end if; RAISE LOG 'doc_type PASSED IN FUNC: %', doc_type; select (impactful_events->doc_type->'caduc')::jsonb ? event_processed.type into is_caduc_event; if is_caduc_event is true then RAISE LOG 'IS CADUC: %', event_processed.type; return 'caduc'; end if; select (impactful_events->doc_type->'opposable')::jsonb ? event_processed.type into is_opposable_event; if is_opposable_event is true then RAISE LOG 'IS OPPOSABLE: %', event_processed.type; return 'opposable'; end if; select (impactful_events->doc_type->'annule')::jsonb ? event_processed.type into is_annule_event; if is_annule_event is true then RAISE LOG 'IS ANNULE'; return 'annule'; end if; select (impactful_events->doc_type->'en cours')::jsonb ? event_processed.type into is_ongoing_event; if is_ongoing_event is true then RAISE LOG 'IS EN COURS'; return 'en cours'; end if; select (impactful_events->doc_type->'abandon')::jsonb ? event_processed.type into is_abandon_event; if is_abandon_event is true then RAISE LOG 'IS ABANDON'; return 'abandon'; end if; return null; end; $$;


CREATE FUNCTION public.event_procedure_status_handler() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ declare procedure procedures; event_processed doc_frise_events;
    BEGIN
        IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then event_processed := new;
        else event_processed := old;
        END IF;
        SELECT * into procedure FROM procedures WHERE id = event_processed.procedure_id;
        PERFORM set_procedure_status(procedure);
        /* NUXT3_API_URL is hardcoded here because this dump will disappear soon and I don't know how to change it quickly in SQL. */
        PERFORM net.http_get('http://localhost:4000/api/urba/procedures/' || event_processed.procedure_id || '/update');
    return event_processed; END; $$;


CREATE FUNCTION public.events_by_procedures_ids(procedures_ids json) RETURNS SETOF record
    LANGUAGE sql
    AS $$
SELECT *
FROM doc_frise_events
WHERE procedure_id::text IN (SELECT value FROM jsonb_array_elements_text(procedures_ids::jsonb));
$$;


CREATE FUNCTION public.get_event_status(p_id uuid, doc_type text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    event_record doc_frise_events%ROWTYPE;
    new_status TEXT;
    current_date_opposable DATE;
BEGIN
    FOR event_record IN
        SELECT *
        FROM doc_frise_events
        WHERE procedure_id = p_id
          AND (is_valid = true OR type = 'Abandon')
        ORDER BY date_iso DESC, type
    LOOP
        new_status := get_event_impact(event_record, doc_type);

        IF new_status = 'opposable' THEN
            current_date_opposable := event_record.date_iso;
        END IF;

        IF new_status IS NOT NULL THEN
            EXIT;
        END IF;
    END LOOP;

    IF new_status IS NULL THEN
        new_status := 'en cours';
    END IF;

    RETURN new_status;
END $$;


create extension if not exists moddatetime schema extensions;
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON public.doc_frise_events FOR EACH ROW EXECUTE FUNCTION extensions.moddatetime('updated_at');
CREATE TRIGGER trigger_event_procedure_status_handler AFTER INSERT OR DELETE OR UPDATE ON public.doc_frise_events FOR EACH ROW EXECUTE FUNCTION public.event_procedure_status_handler();

CREATE INDEX aaaaa ON public.doc_frise_events USING btree (procedure_id, date_iso DESC, type, is_valid); -- ok
CREATE INDEX doc_frise_events_profile_id_idx ON public.doc_frise_events USING btree (profile_id); -- OK
CREATE INDEX idx_doc_frise_events_procedure_id ON public.doc_frise_events USING btree (procedure_id); -- ok
CREATE INDEX idx_doc_frise_events_procedure_id_date_iso ON public.doc_frise_events USING btree (procedure_id, date_iso DESC); -- OK
CREATE INDEX test_index ON public.doc_frise_events USING btree (procedure_id, date_iso); -- removed

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT doc_frise_events_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(user_id),
    ADD CONSTRAINT public_doc_frise_events_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id) ON DELETE CASCADE,
    ADD CONSTRAINT doc_frise_events_from_sudocuh_key UNIQUE (from_sudocuh),
    ADD CONSTRAINT doc_frise_events_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id),
    ADD CONSTRAINT doc_frise_events_pkey PRIMARY KEY (id);

CREATE POLICY "Users Can Read" ON public.doc_frise_events FOR SELECT USING (true);

CREATE POLICY "Verified Can insert" ON public.doc_frise_events FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

CREATE POLICY "Verified Can Update Events" ON public.doc_frise_events FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

CREATE POLICY "Verified Can delete event" ON public.doc_frise_events FOR DELETE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


ALTER TABLE public.doc_frise_events ENABLE ROW LEVEL SECURITY;


GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO service_role;
GRANT ALL ON FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) TO anon;
GRANT ALL ON FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) TO authenticated;
GRANT ALL ON FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) TO service_role;
GRANT ALL ON FUNCTION public.events_by_procedures_ids(procedures_ids json) TO anon;
GRANT ALL ON FUNCTION public.events_by_procedures_ids(procedures_ids json) TO authenticated;
GRANT ALL ON FUNCTION public.events_by_procedures_ids(procedures_ids json) TO service_role;
GRANT ALL ON FUNCTION public.get_event_status(p_id uuid, doc_type text) TO anon;
GRANT ALL ON FUNCTION public.get_event_status(p_id uuid, doc_type text) TO authenticated;
GRANT ALL ON FUNCTION public.get_event_status(p_id uuid, doc_type text) TO service_role;
GRANT ALL ON FUNCTION public.set_procedure_status(procedure public.procedures) TO anon;
GRANT ALL ON FUNCTION public.set_procedure_status(procedure public.procedures) TO authenticated;
GRANT ALL ON FUNCTION public.set_procedure_status(procedure public.procedures) TO service_role;
GRANT ALL ON FUNCTION public.event_procedure_status_handler() TO anon;
GRANT ALL ON FUNCTION public.event_procedure_status_handler() TO authenticated;
GRANT ALL ON FUNCTION public.event_procedure_status_handler() TO service_role;
GRANT ALL ON FUNCTION public.one_shot_events() TO anon;
GRANT ALL ON FUNCTION public.one_shot_events() TO authenticated;
GRANT ALL ON FUNCTION public.one_shot_events() TO service_role;
GRANT ALL ON FUNCTION public.procedure_status_handler() TO anon;
GRANT ALL ON FUNCTION public.procedure_status_handler() TO authenticated;
GRANT ALL ON FUNCTION public.procedure_status_handler() TO service_role;
