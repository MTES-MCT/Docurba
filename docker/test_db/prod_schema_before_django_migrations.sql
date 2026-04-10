--
-- PostgreSQL database dump of the schema before we start to manage the DB with Django migrations.
-- Generated on 2026, April 2nd.
-- Every change made by a Django migration was removed.
-- The more we transform these tables into Django managed models, the less lines this file will contain.
-- Disabled triggers are at the end.
-- Search for TODO to see differences between the real prod schema and the Django models.

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS 'standard public schema';

--
-- Name: procedures; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.procedures (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid,
    type text,
    commentaire text,
    created_at timestamp with time zone DEFAULT now(),
    last_updated_at timestamp with time zone DEFAULT now(),
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
    owner_id uuid,
    previous_opposable_procedures_ids uuid,
    test boolean DEFAULT false,
    type_code text,
    doc_type_code text,
    comment_dgd text,
    shareable boolean DEFAULT false,
    doublon_cache_de_id uuid,
    soft_delete boolean DEFAULT false NOT NULL,
    archived boolean GENERATED ALWAYS AS (((doublon_cache_de_id IS NOT NULL) OR soft_delete)) STORED,
    comment_from_sudocuh text DEFAULT ''::text NOT NULL
);

--
-- Name: pac_sections_dept; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pac_sections_dept (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    path text NOT NULL,
    titre text,
    text text,
    dept text NOT NULL,
    slug text,
    dir text NOT NULL,
    ordre smallint
);

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: doc_frise_events; Type: TABLE; Schema: public; Owner: -
--

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

--
-- Name: pac_sections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pac_sections (
    path text NOT NULL,
    ref text NOT NULL,
    "order" smallint,
    created_at timestamp with time zone DEFAULT now(),
    attachements json DEFAULT '[]'::json,
    parent_sha text,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);

--
-- Name: admin_users_dept; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admin_users_dept (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    role text DEFAULT 'user'::text NOT NULL,
    dept text NOT NULL,
    user_id uuid NOT NULL,
    user_email text NOT NULL
);


--
-- Name: admin_users_region; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admin_users_region (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    user_email text,
    user_id uuid NOT NULL,
    region character varying NOT NULL,
    role character varying NOT NULL
);

--
-- Name: analytics_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.analytics_events (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    user_id uuid,
    path text,
    category text,
    name text,
    value text,
    data json,
    collectivite_id text,
    project_id text,
    procedure_id text,
    dept text,
    region text
);

--
-- Name: etapes_versement; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.etapes_versement (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    name text,
    amount double precision NOT NULL,
    category text,
    is_done boolean,
    versement_id uuid,
    date date
);


--
-- Name: github_cache; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.github_cache (
    path text NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    etag text NOT NULL,
    data json NOT NULL,
    format text DEFAULT 'default'::text
);


--
-- Name: github_ref_roles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.github_ref_roles (
    user_id uuid NOT NULL,
    ref text NOT NULL,
    role text DEFAULT 'user'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: news_letter_emails; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.news_letter_emails (
    created_at timestamp with time zone DEFAULT now(),
    email text NOT NULL,
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL
);


--
-- Name: pac_sections_data; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pac_sections_data (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    source text NOT NULL,
    url text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    category text,
    links jsonb,
    extra jsonb,
    path text NOT NULL,
    ref text NOT NULL
);


--
-- Name: pac_sections_project; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pac_sections_project (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    path text NOT NULL,
    titre text,
    text text,
    project_id uuid,
    slug text,
    dir text NOT NULL,
    ordre smallint
);


--
-- Name: pac_sections_region; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pac_sections_region (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    path text NOT NULL,
    titre text,
    text text,
    region text NOT NULL,
    slug text,
    dir text NOT NULL,
    ordre smallint
);

--
-- Name: procedures_validations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.procedures_validations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    collectivite_code text NOT NULL,
    procedure_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    status text NOT NULL,
    departement text NOT NULL,
    doc_type text,
    profile_id uuid NOT NULL
);


--
-- Name: profiles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.profiles (
    created_at timestamp with time zone DEFAULT now(),
    firstname text,
    lastname text,
    email text,
    poste text,
    other_poste text[],
    departement text,
    collectivite_id text,
    tel text,
    verified boolean DEFAULT false NOT NULL,
    side text,
    region text,
    user_id uuid NOT NULL,
    no_signup boolean DEFAULT false NOT NULL,
    successfully_logged_once boolean DEFAULT false,
    optin boolean DEFAULT false NOT NULL,
    updated_pipedrive boolean,
    is_admin boolean,
    is_staff boolean DEFAULT false NOT NULL,
    departements text[]
);


--
-- Name: set_procedure_status(public.procedures); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_procedure_status(procedure public.procedures) RETURNS void
    LANGUAGE plpgsql
    AS $$ DECLARE new_status text; event doc_frise_events; current_date_opposable text; BEGIN FOR event IN SELECT * FROM doc_frise_events WHERE procedure_id = procedure.id AND (is_valid = true OR type = 'Abandon') ORDER BY date_iso DESC, type LOOP new_status := get_event_impact(event, procedure.doc_type); IF new_status = 'opposable' THEN current_date_opposable := event.date_iso; END IF; IF new_status IS NOT null then EXIT; END IF; END LOOP; IF new_status IS NULL THEN new_status := 'en cours'; END IF; UPDATE procedures SET status = new_status WHERE id = procedure.id; current_date_opposable := null; new_status := null; END; $$;


--
-- Name: check_project_sharing_permission(uuid, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.check_project_sharing_permission(project_id uuid, user_email text) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM projects_sharing ps
    WHERE ps.project_id = check_project_sharing_permission.project_id
      AND ps.role = 'write_frise'
      AND ps.user_email = check_project_sharing_permission.user_email
  );
END;
$$;


--
-- Name: check_user_access(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.check_user_access() RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $$
BEGIN
    -- Return the result of the wrap_check_user_access function for the authenticated user
    RETURN (
        (SELECT verified
         FROM profiles
         WHERE profiles.user_id = auth.uid())
    );
END;
$$;


--
-- Name: check_user_access(uuid); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.check_user_access(user_id uuid) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if the current authenticated user is verified or matches the provided user_id
    RETURN (
        (SELECT verified
         FROM profiles
         WHERE auth.uid() = profiles.user_id)
        OR (auth.uid() = user_id)
    );
END;
$$;


--
-- Name: events_by_procedures_ids(json); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.events_by_procedures_ids(procedures_ids json) RETURNS SETOF record
    LANGUAGE sql
    AS $$
SELECT *
FROM doc_frise_events
WHERE procedure_id::text IN (SELECT value FROM jsonb_array_elements_text(procedures_ids::jsonb));
$$;


-- TODO(cms): remove me from the DB as the `doc_frise_events_duplicate` does not exist anymore.
--
-- Name: events_duplicate_by_procedures_ids(json); Type: FUNCTION; Schema: public; Owner: -
--

-- CREATE FUNCTION public.events_duplicate_by_procedures_ids(procedures_ids json) RETURNS SETOF record
--     LANGUAGE sql
--     AS $$
-- SELECT *
-- FROM doc_frise_events_duplicate
-- WHERE procedure_id::text IN (SELECT value FROM jsonb_array_elements_text(procedures_ids::jsonb));
-- $$;

--
-- Name: FUNCTION events_duplicate_by_procedures_ids(procedures_ids json); Type: ACL; Schema: public; Owner: -
--

-- GRANT ALL ON FUNCTION public.events_duplicate_by_procedures_ids(procedures_ids json) TO anon;
-- GRANT ALL ON FUNCTION public.events_duplicate_by_procedures_ids(procedures_ids json) TO authenticated;
-- GRANT ALL ON FUNCTION public.events_duplicate_by_procedures_ids(procedures_ids json) TO service_role;


--
-- Name: get_event_impact(public.doc_frise_events, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) RETURNS text
    LANGUAGE plpgsql
    AS $$ declare is_opposable_event bool; is_caduc_event bool; is_abandon_event bool; is_ongoing_event bool; is_annule_event bool; new_status text := NULL; impactful_events jsonb := '{ "CC": { "en cours": ["Délibération de prescription du conseil municipal"], "opposable": ["Approbation du préfet", "Caractère exécutoire", "Retrait de l''annulation totale"], "abandon": ["Abandon", "Retrait de la délibération de prescription"], "annule": ["Annulation TA totale", "Annulation TA", "Abrogation effective"], "caduc": [] }, "SCOT": { "en cours": ["Délibération de l''établissement public qui prescrit", "Retrait de la délibération d''approbation"], "opposable": ["Délibération d''approbation", "Caractère exécutoire", "Retrait de l''annulation totale"], "abandon": ["Abandon", "Retrait de la délibération de prescription"], "annule": ["Annulation TA totale", "Annulation TA"], "caduc": ["Caducité"] }, "SD": { "en cours": ["Délibération de l''établissement public qui prescrit"], "opposable": ["Délibération d''approbation", "Caractère exécutoire"], "abandon": ["Abandon"], "annule": ["Annulation TA totale", "Annulation TA"], "caduc": ["Caducité"] }, "PLU": { "en cours": ["Délibération de prescription du conseil municipal ou communautaire"], "opposable": ["Caractère exécutoire", "Retrait de l''annulation totale", "Délibération d''approbation du municipal ou communautaire", "Délibération d''approbation du conseil municipal ou communautaire", "Délibération d''approbation"], "abandon": ["Abandon", "Retrait de la délibération de prescription"], "annule": ["Annulation TA totale", "Annulation TA", "Abrogation", "Arrêté d''abrogation"], "caduc": ["Caducité"] }, "POS": { "en cours": ["Délibération de prescription du conseil municipal ou communautaire"], "opposable": ["Caractère exécutoire", "Délibération d''approbation du municipal ou communautaire", "Délibération d''approbation du conseil municipal ou communautaire", "Délibération d''approbation"], "abandon": ["Abandon"], "annule": ["Annulation TA", "Annulation TA totale", "Caducité"], "caduc": [] } }'; begin if doc_type ILIKE 'PLU%' then doc_type := 'PLU'; end if; RAISE LOG 'doc_type PASSED IN FUNC: %', doc_type; select (impactful_events->doc_type->'caduc')::jsonb ? event_processed.type into is_caduc_event; if is_caduc_event is true then RAISE LOG 'IS CADUC: %', event_processed.type; return 'caduc'; end if; select (impactful_events->doc_type->'opposable')::jsonb ? event_processed.type into is_opposable_event; if is_opposable_event is true then RAISE LOG 'IS OPPOSABLE: %', event_processed.type; return 'opposable'; end if; select (impactful_events->doc_type->'annule')::jsonb ? event_processed.type into is_annule_event; if is_annule_event is true then RAISE LOG 'IS ANNULE'; return 'annule'; end if; select (impactful_events->doc_type->'en cours')::jsonb ? event_processed.type into is_ongoing_event; if is_ongoing_event is true then RAISE LOG 'IS EN COURS'; return 'en cours'; end if; select (impactful_events->doc_type->'abandon')::jsonb ? event_processed.type into is_abandon_event; if is_abandon_event is true then RAISE LOG 'IS ABANDON'; return 'abandon'; end if; return null; end; $$;


--
-- Name: get_event_status(uuid, text); Type: FUNCTION; Schema: public; Owner: -
--

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


--
-- Name: is_admin(uuid); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.is_admin(user_id uuid) RETURNS boolean
    LANGUAGE plpgsql SECURITY DEFINER
    AS $_$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM profiles
    WHERE profiles.user_id = $1 AND is_admin IS TRUE
  );
END;
$_$;


--
-- Name: jb_to_ta(jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.jb_to_ta(jsonb) RETURNS text[]
    LANGUAGE sql
    AS $_$
    select array_agg(x) from jsonb_array_elements_text( $1 ) x;
$_$;


--
-- Name: one_shot_events(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.one_shot_events() RETURNS void
    LANGUAGE plpgsql
    AS $$ DECLARE procedure procedures; start_time timestamp := clock_timestamp(); end_time timestamp; execution_time interval; i INT := 0; BEGIN RAISE LOG 'Processing One shot events'; UPDATE procedures SET status = null; FOR procedure IN SELECT * FROM procedures WHERE is_principale IS TRUE LOOP i := i + 1; RAISE LOG 'Processing procedure events N: %', i; PERFORM set_procedure_status(procedure); END LOOP; end_time := clock_timestamp(); execution_time := end_time - start_time; RAISE LOG 'FUNCTION ONE SHOT execution time: %', execution_time; END; $$;


--
-- Name: procedures_by_insee_codes(json); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.procedures_by_insee_codes(codes json) RETURNS SETOF record
    LANGUAGE sql
    AS $$
SELECT *
FROM procedures
WHERE EXISTS (
  SELECT id, status, doc_type, current_perimetre, is_pluih
  FROM jsonb_array_elements(current_perimetre) obj
  WHERE ((obj->>'inseeCode')::text IN (
    SELECT jsonb_array_elements_text(codes::jsonb)
  )) and (status in ('opposable', 'en cours')) and (is_principale = true)
);
$$;


--
-- Name: procedures_by_sudocuh_ids(json); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) RETURNS SETOF record
    LANGUAGE sql
    AS $$
SELECT id, from_sudocuh, initial_perimetre, current_perimetre, status
FROM procedures
WHERE from_sudocuh::text IN (SELECT value FROM jsonb_array_elements_text(sudocuh_ids::jsonb));
$$;

--
-- Name: COLUMN pac_sections_dept.ordre; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pac_sections_dept.ordre IS 'ordre dans la hierarchie';


--
-- Name: update_sections_order(json); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_sections_order(payload json) RETURNS SETOF public.pac_sections_dept
    LANGUAGE sql
    AS $$
  update pac_sections_dept as section set ordre = s.ordre
  from (
    select * from json_populate_recordset(null::pac_sections_dept, payload)
  ) as s(id)
  where section.id = s.id
  returning section.*;
$$;


--
-- Name: COLUMN pac_sections.parent_sha; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pac_sections.parent_sha IS 'Le sha validé de la référence parente';


--
-- Name: update_sections_path(json); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_sections_path(payload json) RETURNS SETOF public.pac_sections
    LANGUAGE sql
    AS $$update pac_sections_data set path = s.new_path
from (
  select * from json_to_recordset(payload) as t(path text, ref text, new_path text)
) as s
where (pac_sections_data.path = s.path and pac_sections_data.ref = s.ref);

update pac_sections as section set path = s.new_path
from (
  select * from json_to_recordset(payload) as t(path text, ref text, new_path text)
) as s
where (section.path = s.path and section.ref = s.ref)
returning section.*;$$;


--
-- Name: validated_collectivites(date, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validated_collectivites(since date, departement text) RETURNS TABLE(collectivite_code text, created_at timestamp without time zone, profile_id uuid, email text)
    LANGUAGE sql
    AS $$SELECT
	inn.*,
	pf.email
FROM
	(
		SELECT
			pv.collectivite_code,
			MIN(pv.created_at) AS created_at,
			MIN(pv.profile_id::text)::UUID AS profile_id
		FROM
			procedures_validations pv
		WHERE
			pv.created_at > since
			AND pv.departement = departement
		GROUP BY
			pv.collectivite_code
		ORDER BY
			pv.collectivite_code
	) AS inn
	LEFT JOIN profiles pf ON inn.profile_id = pf.user_id;$$;


--
-- Name: validated_collectivites_by_depts(date); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.validated_collectivites_by_depts(since date) RETURNS TABLE(departement text, unique_collectivites_count bigint)
    LANGUAGE sql SECURITY DEFINER
    AS $$SELECT
	departement,
	COUNT(DISTINCT collectivite_code) AS unique_collectivites_count
FROM
	procedures_validations
WHERE
  created_at > since
GROUP BY
	departement
ORDER BY
	departement;$$;


--
-- Name: wrap_check_user_access(uuid); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.wrap_check_user_access(checked_user_id uuid) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Check if the current authenticated user is verified
    RETURN (
        (SELECT verified
         FROM profiles
         WHERE profiles.user_id = checked_user_id)
    );
END;
$$;


--
-- Name: admin_users_region_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.admin_users_region ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.admin_users_region_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: COLUMN pac_sections_region.ordre; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.pac_sections_region.ordre IS 'ordre dans la hierarchie';


--
-- Name: pac_sections_save_13-03-24; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."pac_sections_save_13-03-24" (
    path text NOT NULL,
    ref text NOT NULL,
    "order" smallint,
    created_at timestamp with time zone DEFAULT now(),
    attachements json DEFAULT '[]'::json,
    parent_sha text,
    id uuid DEFAULT gen_random_uuid() NOT NULL
);


--
-- Name: TABLE "pac_sections_save_13-03-24"; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON TABLE public."pac_sections_save_13-03-24" IS 'This is a duplicate of pac_sections';


--
-- Name: COLUMN "pac_sections_save_13-03-24".parent_sha; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public."pac_sections_save_13-03-24".parent_sha IS 'Le sha validé de la référence parente';


--
-- Name: prescriptions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.prescriptions (
    id bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    epci jsonb,
    attachments json,
    type character varying,
    link_url character varying,
    towns text[],
    acte_type text,
    date date,
    du_type text,
    perimetre text[],
    is_pluih text,
    is_pluim text,
    mandatory_pluim text,
    is_scot text,
    procedure_type text,
    procedure_number text,
    other_acte_type text,
    ms_scope text[],
    project_id uuid,
    user_id uuid,
    email text
);


--
-- Name: COLUMN prescriptions.type; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.prescriptions.type IS 'Can be "link" or "attachments"';


--
-- Name: prescriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.prescriptions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.prescriptions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

--
-- Name: COLUMN profiles.region; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.profiles.region IS 'Si l''utilisateur est une DREAL ou une PPA : région de son périmètre. La colonne peut être remplie pour les autres types.';


--
-- Name: COLUMN profiles.no_signup; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.profiles.no_signup IS 'Si l''utilisateur passe par un depot d''acte, il est autorisé à mettre uniquement son email. Dans ce cas l''utilisateur n''a pas de compte Docurba, et no_signup sera à TRUE.';


--
-- Name: COLUMN profiles.is_admin; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.profiles.is_admin IS 'super admin bypass';


--
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    created_at timestamp with time zone DEFAULT now(),
    name character varying,
    doc_type character varying NOT NULL,
    region character varying,
    "PAC" jsonb,
    owner uuid,
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    towns jsonb,
    epci jsonb,
    trame character varying,
    archived boolean DEFAULT false NOT NULL,
    sudocuh_procedure_id integer,
    collectivite_id text,
    from_sudocuh integer,
    current_perimetre jsonb[],
    initial_perimetre jsonb[],
    collectivite_porteuse_id text,
    is_sudocuh_scot boolean,
    current_perimetre_new jsonb,
    test boolean,
    doc_type_code text,
    from_sudocuh_procedure_id integer
);


--
-- Name: projects_sharing; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects_sharing (
    id uuid DEFAULT extensions.uuid_generate_v4() NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    user_email text NOT NULL,
    project_id uuid NOT NULL,
    shared_by uuid,
    notified boolean DEFAULT false NOT NULL,
    last_update_notification timestamp without time zone DEFAULT now() NOT NULL,
    role character varying DEFAULT 'read'::character varying,
    archived boolean DEFAULT false NOT NULL,
    dev_test boolean DEFAULT false,
    inserted_script boolean DEFAULT false,
    email_notified boolean DEFAULT false NOT NULL
);


--
-- Name: COLUMN projects_sharing.last_update_notification; Type: COMMENT; Schema: public; Owner: -
--

COMMENT ON COLUMN public.projects_sharing.last_update_notification IS 'Timestamp of last notification';


--
-- Name: regions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.regions (
    code text NOT NULL,
    name text NOT NULL
);

--
-- Name: versements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.versements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    amount bigint,
    year text,
    category text,
    comment text,
    procedure_id uuid,
    from_sudocu_procedure_id integer,
    from_sudocu smallint
);


--
-- Name: admin_users_dept admin_users_dept_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_users_dept
    ADD CONSTRAINT admin_users_dept_pkey PRIMARY KEY (id);


--
-- Name: admin_users_region admin_users_region_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_users_region
    ADD CONSTRAINT admin_users_region_pkey PRIMARY KEY (id);


--
-- Name: analytics_events analytics_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT analytics_events_pkey PRIMARY KEY (id);


--
-- Name: doc_frise_events doc_frise_events_from_sudocuh_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT doc_frise_events_from_sudocuh_key UNIQUE (from_sudocuh);


--
-- Name: doc_frise_events doc_frise_events_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT doc_frise_events_pkey PRIMARY KEY (id);


--
-- Name: etapes_versement etapes_versement_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.etapes_versement
    ADD CONSTRAINT etapes_versement_pkey PRIMARY KEY (id);


--
-- Name: github_cache github_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.github_cache
    ADD CONSTRAINT github_cache_pkey PRIMARY KEY (path);


--
-- Name: github_ref_roles github_ref_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.github_ref_roles
    ADD CONSTRAINT github_ref_roles_pkey PRIMARY KEY (user_id, ref);


--
-- Name: news_letter_emails news_letter_emails_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.news_letter_emails
    ADD CONSTRAINT news_letter_emails_email_key UNIQUE (email);


--
-- Name: news_letter_emails news_letter_emails_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.news_letter_emails
    ADD CONSTRAINT news_letter_emails_pkey PRIMARY KEY (id);


--
-- Name: pac_sections_data pac_sections_data_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pac_sections_data
    ADD CONSTRAINT pac_sections_data_pkey PRIMARY KEY (id);


--
-- Name: pac_sections_dept pac_sections_dept_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pac_sections_dept
    ADD CONSTRAINT pac_sections_dept_pkey PRIMARY KEY (id);


--
-- Name: pac_sections pac_sections_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pac_sections
    ADD CONSTRAINT pac_sections_id_key UNIQUE (id);


--
-- Name: pac_sections pac_sections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pac_sections
    ADD CONSTRAINT pac_sections_pkey PRIMARY KEY (path, ref);


--
-- Name: pac_sections_project pac_sections_project_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pac_sections_project
    ADD CONSTRAINT pac_sections_project_pkey PRIMARY KEY (id);


--
-- Name: pac_sections_region pac_sections_region_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pac_sections_region
    ADD CONSTRAINT pac_sections_region_pkey PRIMARY KEY (id);


--
-- Name: pac_sections_save_13-03-24 pac_sections_save_13-03-24_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."pac_sections_save_13-03-24"
    ADD CONSTRAINT "pac_sections_save_13-03-24_id_key" UNIQUE (id);


--
-- Name: pac_sections_save_13-03-24 pac_sections_save_13-03-24_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."pac_sections_save_13-03-24"
    ADD CONSTRAINT "pac_sections_save_13-03-24_pkey" PRIMARY KEY (path, ref);


--
-- Name: prescriptions prescriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_pkey PRIMARY KEY (id);


--
-- Name: procedures procedures_doublon_cache_de_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_doublon_cache_de_id_key UNIQUE (doublon_cache_de_id);


--
-- Name: procedures procedures_from_sudocuh_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_from_sudocuh_key UNIQUE (from_sudocuh);



--
-- Name: procedures procedures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_pkey PRIMARY KEY (id);


--
-- Name: procedures_validations procedures_validation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures_validations
    ADD CONSTRAINT procedures_validation_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (user_id);


--
-- Name: projects_sharing projectsSharing_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects_sharing
    ADD CONSTRAINT "projectsSharing_pkey" PRIMARY KEY (id);


--
-- Name: projects projects_from_sudocuh_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_from_sudocuh_key UNIQUE (from_sudocuh);


--
-- Name: projects projects_from_sudocuh_procedure_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_from_sudocuh_procedure_id_key UNIQUE (from_sudocuh_procedure_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (code);

--
-- Name: projects_sharing unique_project_sharing; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects_sharing
    ADD CONSTRAINT unique_project_sharing UNIQUE (user_email, project_id, role);


--
-- Name: versements versements_from_sudocu_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.versements
    ADD CONSTRAINT versements_from_sudocu_unique UNIQUE (from_sudocu);


--
-- Name: versements versements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.versements
    ADD CONSTRAINT versements_pkey PRIMARY KEY (id);


--
-- Name: aaaaa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX aaaaa ON public.doc_frise_events USING btree (procedure_id, date_iso DESC, type, is_valid);


--
-- Name: category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX category_idx ON public.analytics_events USING btree (category);


--
-- Name: created_at_brin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX created_at_brin ON public.analytics_events USING brin (created_at);


--
-- Name: doc_frise_events_profile_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX doc_frise_events_profile_id_idx ON public.doc_frise_events USING btree (profile_id);


--
-- Name: idx_doc_frise_events_procedure_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_frise_events_procedure_id ON public.doc_frise_events USING btree (procedure_id);


--
-- Name: idx_doc_frise_events_procedure_id_date_iso; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_doc_frise_events_procedure_id_date_iso ON public.doc_frise_events USING btree (procedure_id, date_iso DESC);


--
-- Name: idx_procedures_collectivite_porteuse_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_procedures_collectivite_porteuse_id ON public.procedures USING btree (collectivite_porteuse_id);


--
-- Name: idx_procedures_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_procedures_created_at ON public.procedures USING btree (created_at);


--
-- Name: idx_procedures_doc_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_procedures_doc_type ON public.procedures USING btree (doc_type);


--
-- Name: idx_procedures_is_principale; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_procedures_is_principale ON public.procedures USING btree (id, is_principale, archived);


--
-- Name: idx_procedures_is_principale_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_procedures_is_principale_created_at ON public.procedures USING btree (is_principale, created_at);


--
-- Name: idx_procedures_is_principale_doc_type_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_procedures_is_principale_doc_type_created_at ON public.procedures USING btree (is_principale, doc_type, created_at);


--
-- Name: idx_procedures_secondary_procedure_of; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_procedures_secondary_procedure_of ON public.procedures USING btree (secondary_procedure_of);


--
-- Name: idx_project_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_project_id ON public.procedures USING btree (project_id);


--
-- Name: pac_sections_data_unique_path_ref_url; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX pac_sections_data_unique_path_ref_url ON public.pac_sections_data USING btree (path, ref, url);


--
-- Name: procedure_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX procedure_id_idx ON public.analytics_events USING btree (procedure_id);


--
-- Name: procedures_pkey_secondary_null_not_archived; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX procedures_pkey_secondary_null_not_archived ON public.procedures USING btree (id) WHERE ((secondary_procedure_of IS NULL) AND (NOT archived));




--
-- Name: test_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX test_index ON public.doc_frise_events USING btree (procedure_id, date_iso);


--
-- Name: doc_frise_events doc_frise_events_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT doc_frise_events_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(user_id);


--
-- Name: doc_frise_events doc_frise_events_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT doc_frise_events_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: etapes_versement etapes_versement_versement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.etapes_versement
    ADD CONSTRAINT etapes_versement_versement_id_fkey FOREIGN KEY (versement_id) REFERENCES public.versements(id) ON DELETE CASCADE;


--
-- Name: pac_sections_project pac_sections_project_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pac_sections_project
    ADD CONSTRAINT pac_sections_project_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: prescriptions prescriptions_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: prescriptions prescriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.prescriptions
    ADD CONSTRAINT prescriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id);


--
-- Name: procedures procedures_doublon_cache_de_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_doublon_cache_de_id_fkey FOREIGN KEY (doublon_cache_de_id) REFERENCES public.procedures(id) ON UPDATE CASCADE ON DELETE RESTRICT;


--
-- Name: procedures procedures_previous_opposable_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_previous_opposable_procedure_id_fkey FOREIGN KEY (previous_opposable_procedures_ids) REFERENCES public.procedures(id);


--
-- Name: procedures procedures_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: procedures procedures_secondary_procedure_of_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_secondary_procedure_of_fkey FOREIGN KEY (secondary_procedure_of) REFERENCES public.procedures(id);


--
-- Name: procedures_validations procedures_validations_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures_validations
    ADD CONSTRAINT procedures_validations_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id);


--
-- Name: procedures_validations procedures_validations_profile_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures_validations
    ADD CONSTRAINT procedures_validations_profile_id_fkey FOREIGN KEY (profile_id) REFERENCES public.profiles(user_id);


--
-- Name: projects_sharing projectsSharing_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects_sharing
    ADD CONSTRAINT "projectsSharing_project_id_fkey" FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: analytics_events public_analytics_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT public_analytics_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.profiles(user_id) ON DELETE SET NULL;


--
-- Name: doc_frise_events public_doc_frise_events_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT public_doc_frise_events_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id) ON DELETE CASCADE;


--
-- Name: github_ref_roles public_github_ref_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.github_ref_roles
    ADD CONSTRAINT public_github_ref_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: procedures public_procedures_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT public_procedures_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.profiles(user_id) ON DELETE SET NULL;



--
-- Name: profiles public_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT public_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;


--
-- Name: projects public_projects_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT public_projects_owner_fkey FOREIGN KEY (owner) REFERENCES public.profiles(user_id) ON DELETE SET NULL;


--
-- Name: projects_sharing public_projects_sharing_shared_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects_sharing
    ADD CONSTRAINT public_projects_sharing_shared_by_fkey FOREIGN KEY (shared_by) REFERENCES public.profiles(user_id) ON UPDATE CASCADE ON DELETE CASCADE;

--
-- Name: versements versements_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.versements
    ADD CONSTRAINT versements_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id);

--
-- Name: procedures_validations Enable delete for users based on user_id; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable delete for users based on user_id" ON public.procedures_validations FOR DELETE USING (((( SELECT auth.uid() AS uid) = profile_id) OR public.is_admin(auth.uid())));


--
-- Name: analytics_events Enable insert access for all users; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable insert access for all users" ON public.analytics_events FOR INSERT WITH CHECK (true);


--
-- Name: projects Enable insert for authenticated users only; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable insert for authenticated users only" ON public.projects FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: procedures_validations Enable insert for users based on role; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable insert for users based on role" ON public.procedures_validations FOR INSERT WITH CHECK (((( SELECT profiles.poste
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)) = 'ddt'::text) OR (( SELECT profiles.poste
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)) = 'dreal'::text)));


--
-- Name: news_letter_emails Enable insert to all users; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable insert to all users" ON public.news_letter_emails FOR INSERT WITH CHECK (true);



--
-- Name: projects Enable read for users; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable read for users" ON public.projects FOR SELECT USING (true);


--
-- Name: projects Enable update for users verified; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable update for users verified" ON public.projects FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id))) WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));

--
-- Name: admin_users_dept Insert user request; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Insert user request" ON public.admin_users_dept FOR INSERT WITH CHECK (((auth.uid() = user_id) AND (auth.email() = user_email) AND (role = 'user'::text)));


--
-- Name: etapes_versement Policy with security definer functions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Policy with security definer functions" ON public.etapes_versement USING (true);


--
-- Name: versements Policy with security definer functions; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Policy with security definer functions" ON public.versements TO authenticated USING (true);

--
-- Name: projects_sharing Read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Read" ON public.projects_sharing FOR SELECT USING ((public.is_admin(auth.uid()) OR public.check_user_access()));


--
-- Name: admin_users_region Read own role; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Read own role" ON public.admin_users_region FOR SELECT USING (((auth.uid() = user_id) AND (auth.email() = user_email)));


--
-- Name: admin_users_dept Read own roles; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Read own roles" ON public.admin_users_dept FOR SELECT USING (((auth.uid() = user_id) AND (auth.email() = user_email)));


--
-- Name: procedures_validations Select if DDT or Dreal; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Select if DDT or Dreal" ON public.procedures_validations FOR SELECT USING (((( SELECT profiles.poste
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)) = 'ddt'::text) OR (( SELECT profiles.poste
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)) = 'dreal'::text)));


--
-- Name: projects_sharing Update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Update" ON public.projects_sharing FOR UPDATE USING (((auth.uid() = shared_by) AND (auth.uid() = ( SELECT projects.owner
   FROM public.projects
  WHERE (projects.id = projects_sharing.project_id))))) WITH CHECK (((auth.uid() = shared_by) AND (auth.uid() = ( SELECT projects.owner
   FROM public.projects
  WHERE (projects.id = projects_sharing.project_id)))));


--
-- Name: profiles User can update own profile; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "User can update own profile" ON public.profiles FOR UPDATE USING ((auth.uid() = user_id)) WITH CHECK ((auth.uid() = user_id));


--
-- Name: prescriptions Users Can Insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can Insert" ON public.prescriptions FOR INSERT WITH CHECK (true);


--
-- Name: profiles Users Can Insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can Insert" ON public.profiles FOR INSERT WITH CHECK (true);


--
-- Name: doc_frise_events Users Can Read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can Read" ON public.doc_frise_events FOR SELECT USING (true);


--
-- Name: procedures Users Can Read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can Read" ON public.procedures FOR SELECT USING (true);


--
-- Name: pac_sections Users Can read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can read" ON public.pac_sections FOR SELECT USING (true);


--
-- Name: pac_sections_data Users Can read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can read" ON public.pac_sections_data FOR SELECT USING (true);


--
-- Name: prescriptions Users Can read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can read" ON public.prescriptions FOR SELECT USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: profiles Users Can read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users Can read" ON public.profiles FOR SELECT USING ((public.check_user_access() OR (auth.uid() = user_id)));


--
-- Name: github_ref_roles Users can read; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Users can read" ON public.github_ref_roles FOR SELECT USING (true);


--
-- Name: procedures Verified Can Delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Delete" ON public.procedures FOR DELETE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: github_ref_roles Verified Can Insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Insert" ON public.github_ref_roles FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: pac_sections Verified Can Insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Insert" ON public.pac_sections FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: pac_sections_data Verified Can Insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Insert" ON public.pac_sections_data FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: procedures Verified Can Insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Insert" ON public.procedures FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: pac_sections Verified Can Update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Update" ON public.pac_sections FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: pac_sections_data Verified Can Update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Update" ON public.pac_sections_data FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: procedures Verified Can Update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Update" ON public.procedures FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: doc_frise_events Verified Can Update Events; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can Update Events" ON public.doc_frise_events FOR UPDATE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: pac_sections_data Verified Can delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can delete" ON public.pac_sections_data FOR DELETE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: doc_frise_events Verified Can delete event; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can delete event" ON public.doc_frise_events FOR DELETE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: doc_frise_events Verified Can insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Verified Can insert" ON public.doc_frise_events FOR INSERT WITH CHECK (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: admin_users_dept; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.admin_users_dept ENABLE ROW LEVEL SECURITY;

--
-- Name: admin_users_region; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.admin_users_region ENABLE ROW LEVEL SECURITY;

--
-- Name: analytics_events; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;

--
-- Name: doc_frise_events; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.doc_frise_events ENABLE ROW LEVEL SECURITY;

--
-- Name: etapes_versement; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.etapes_versement ENABLE ROW LEVEL SECURITY;

--
-- Name: github_cache; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.github_cache ENABLE ROW LEVEL SECURITY;

--
-- Name: github_ref_roles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.github_ref_roles ENABLE ROW LEVEL SECURITY;

--
-- Name: news_letter_emails; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.news_letter_emails ENABLE ROW LEVEL SECURITY;

--
-- Name: pac_sections; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.pac_sections ENABLE ROW LEVEL SECURITY;

--
-- Name: pac_sections_data; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.pac_sections_data ENABLE ROW LEVEL SECURITY;

--
-- Name: pac_sections_dept; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.pac_sections_dept ENABLE ROW LEVEL SECURITY;

--
-- Name: pac_sections_project; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.pac_sections_project ENABLE ROW LEVEL SECURITY;

--
-- Name: pac_sections_region; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.pac_sections_region ENABLE ROW LEVEL SECURITY;

--
-- Name: pac_sections_save_13-03-24; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public."pac_sections_save_13-03-24" ENABLE ROW LEVEL SECURITY;

--
-- Name: prescriptions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.prescriptions ENABLE ROW LEVEL SECURITY;

--
-- Name: procedures; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.procedures ENABLE ROW LEVEL SECURITY;

--
-- Name: procedures_validations; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.procedures_validations ENABLE ROW LEVEL SECURITY;

--
-- Name: profiles; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

--
-- Name: projects; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

--
-- Name: projects_sharing; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.projects_sharing ENABLE ROW LEVEL SECURITY;

--
-- Name: regions; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.regions ENABLE ROW LEVEL SECURITY;

--
-- Name: pac_sections verified can delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "verified can delete" ON public.pac_sections FOR DELETE USING (( SELECT profiles.verified
   FROM public.profiles
  WHERE (auth.uid() = profiles.user_id)));


--
-- Name: versements; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.versements ENABLE ROW LEVEL SECURITY;

--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: -
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;
GRANT USAGE ON SCHEMA public TO anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT USAGE ON SCHEMA public TO service_role;


--
-- Name: FUNCTION check_project_sharing_permission(project_id uuid, user_email text); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.check_project_sharing_permission(project_id uuid, user_email text) TO anon;
GRANT ALL ON FUNCTION public.check_project_sharing_permission(project_id uuid, user_email text) TO authenticated;
GRANT ALL ON FUNCTION public.check_project_sharing_permission(project_id uuid, user_email text) TO service_role;


--
-- Name: FUNCTION check_user_access(); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.check_user_access() TO anon;
GRANT ALL ON FUNCTION public.check_user_access() TO authenticated;
GRANT ALL ON FUNCTION public.check_user_access() TO service_role;


--
-- Name: FUNCTION check_user_access(user_id uuid); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.check_user_access(user_id uuid) TO anon;
GRANT ALL ON FUNCTION public.check_user_access(user_id uuid) TO authenticated;
GRANT ALL ON FUNCTION public.check_user_access(user_id uuid) TO service_role;


--
-- Name: FUNCTION events_by_procedures_ids(procedures_ids json); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.events_by_procedures_ids(procedures_ids json) TO anon;
GRANT ALL ON FUNCTION public.events_by_procedures_ids(procedures_ids json) TO authenticated;
GRANT ALL ON FUNCTION public.events_by_procedures_ids(procedures_ids json) TO service_role;

--
-- Name: TABLE doc_frise_events; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.doc_frise_events TO service_role;


--
-- Name: FUNCTION get_event_impact(event_processed public.doc_frise_events, doc_type text); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) TO anon;
GRANT ALL ON FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) TO authenticated;
GRANT ALL ON FUNCTION public.get_event_impact(event_processed public.doc_frise_events, doc_type text) TO service_role;


--
-- Name: FUNCTION get_event_status(p_id uuid, doc_type text); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.get_event_status(p_id uuid, doc_type text) TO anon;
GRANT ALL ON FUNCTION public.get_event_status(p_id uuid, doc_type text) TO authenticated;
GRANT ALL ON FUNCTION public.get_event_status(p_id uuid, doc_type text) TO service_role;


--
-- Name: FUNCTION is_admin(user_id uuid); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.is_admin(user_id uuid) TO anon;
GRANT ALL ON FUNCTION public.is_admin(user_id uuid) TO authenticated;
GRANT ALL ON FUNCTION public.is_admin(user_id uuid) TO service_role;


--
-- Name: FUNCTION jb_to_ta(jsonb); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.jb_to_ta(jsonb) TO anon;
GRANT ALL ON FUNCTION public.jb_to_ta(jsonb) TO authenticated;
GRANT ALL ON FUNCTION public.jb_to_ta(jsonb) TO service_role;


--
-- Name: FUNCTION one_shot_events(); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.one_shot_events() TO anon;
GRANT ALL ON FUNCTION public.one_shot_events() TO authenticated;
GRANT ALL ON FUNCTION public.one_shot_events() TO service_role;


--
-- Name: FUNCTION procedures_by_insee_codes(codes json); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO anon;
GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO authenticated;
GRANT ALL ON FUNCTION public.procedures_by_insee_codes(codes json) TO service_role;


--
-- Name: FUNCTION procedures_by_sudocuh_ids(sudocuh_ids json); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO anon;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO authenticated;
GRANT ALL ON FUNCTION public.procedures_by_sudocuh_ids(sudocuh_ids json) TO service_role;



--
-- Name: TABLE procedures; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures TO service_role;


--
-- Name: FUNCTION set_procedure_status(procedure public.procedures); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.set_procedure_status(procedure public.procedures) TO anon;
GRANT ALL ON FUNCTION public.set_procedure_status(procedure public.procedures) TO authenticated;
GRANT ALL ON FUNCTION public.set_procedure_status(procedure public.procedures) TO service_role;


--
-- Name: TABLE pac_sections_dept; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_dept TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_dept TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_dept TO service_role;


--
-- Name: FUNCTION update_sections_order(payload json); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.update_sections_order(payload json) TO anon;
GRANT ALL ON FUNCTION public.update_sections_order(payload json) TO authenticated;
GRANT ALL ON FUNCTION public.update_sections_order(payload json) TO service_role;


--
-- Name: TABLE pac_sections; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections TO service_role;


--
-- Name: FUNCTION update_sections_path(payload json); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.update_sections_path(payload json) TO anon;
GRANT ALL ON FUNCTION public.update_sections_path(payload json) TO authenticated;
GRANT ALL ON FUNCTION public.update_sections_path(payload json) TO service_role;


--
-- Name: FUNCTION validated_collectivites(since date, departement text); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.validated_collectivites(since date, departement text) TO anon;
GRANT ALL ON FUNCTION public.validated_collectivites(since date, departement text) TO authenticated;
GRANT ALL ON FUNCTION public.validated_collectivites(since date, departement text) TO service_role;


--
-- Name: FUNCTION validated_collectivites_by_depts(since date); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.validated_collectivites_by_depts(since date) TO anon;
GRANT ALL ON FUNCTION public.validated_collectivites_by_depts(since date) TO authenticated;
GRANT ALL ON FUNCTION public.validated_collectivites_by_depts(since date) TO service_role;


--
-- Name: FUNCTION wrap_check_user_access(checked_user_id uuid); Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON FUNCTION public.wrap_check_user_access(checked_user_id uuid) TO anon;
GRANT ALL ON FUNCTION public.wrap_check_user_access(checked_user_id uuid) TO authenticated;
GRANT ALL ON FUNCTION public.wrap_check_user_access(checked_user_id uuid) TO service_role;


--
-- Name: TABLE admin_users_dept; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.admin_users_dept TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.admin_users_dept TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.admin_users_dept TO service_role;


--
-- Name: TABLE admin_users_region; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.admin_users_region TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.admin_users_region TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.admin_users_region TO service_role;


--
-- Name: SEQUENCE admin_users_region_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.admin_users_region_id_seq TO anon;
GRANT ALL ON SEQUENCE public.admin_users_region_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.admin_users_region_id_seq TO service_role;


--
-- Name: TABLE analytics_events; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.analytics_events TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.analytics_events TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.analytics_events TO service_role;


--
-- Name: TABLE etapes_versement; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.etapes_versement TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.etapes_versement TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.etapes_versement TO service_role;


--
-- Name: TABLE github_cache; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.github_cache TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.github_cache TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.github_cache TO service_role;


--
-- Name: TABLE github_ref_roles; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.github_ref_roles TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.github_ref_roles TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.github_ref_roles TO service_role;


--
-- Name: TABLE news_letter_emails; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.news_letter_emails TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.news_letter_emails TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.news_letter_emails TO service_role;


--
-- Name: TABLE pac_sections_data; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_data TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_data TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_data TO service_role;


--
-- Name: TABLE pac_sections_project; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_project TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_project TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_project TO service_role;


--
-- Name: TABLE pac_sections_region; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_region TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_region TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.pac_sections_region TO service_role;


--
-- Name: TABLE "pac_sections_save_13-03-24"; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public."pac_sections_save_13-03-24" TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public."pac_sections_save_13-03-24" TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public."pac_sections_save_13-03-24" TO service_role;


--
-- Name: TABLE prescriptions; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.prescriptions TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.prescriptions TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.prescriptions TO service_role;


--
-- Name: SEQUENCE prescriptions_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.prescriptions_id_seq TO anon;
GRANT ALL ON SEQUENCE public.prescriptions_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.prescriptions_id_seq TO service_role;


--
-- Name: TABLE procedures_validations; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures_validations TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures_validations TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.procedures_validations TO service_role;


--
-- Name: TABLE profiles; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.profiles TO anon;
GRANT SELECT,REFERENCES,DELETE,TRIGGER,TRUNCATE ON TABLE public.profiles TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.profiles TO service_role;


--
-- Name: COLUMN profiles.created_at; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(created_at),INSERT(created_at),UPDATE(created_at) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.firstname; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(firstname),INSERT(firstname),UPDATE(firstname) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.lastname; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(lastname),INSERT(lastname),UPDATE(lastname) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.email; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(email),INSERT(email),UPDATE(email) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.poste; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(poste),INSERT(poste),UPDATE(poste) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.other_poste; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(other_poste),INSERT(other_poste),UPDATE(other_poste) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.departement; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(departement),INSERT(departement),UPDATE(departement) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.collectivite_id; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(collectivite_id),INSERT(collectivite_id),UPDATE(collectivite_id) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.tel; Type: ACL; Schema: public; Owner: -
--

GRANT INSERT(tel),UPDATE(tel) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.verified; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(verified) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.side; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(side),INSERT(side),UPDATE(side) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.region; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(region),INSERT(region),UPDATE(region) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.user_id; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(user_id),INSERT(user_id),UPDATE(user_id) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.no_signup; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(no_signup),INSERT(no_signup),UPDATE(no_signup) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.successfully_logged_once; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(successfully_logged_once),INSERT(successfully_logged_once),UPDATE(successfully_logged_once) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.optin; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(optin),INSERT(optin),UPDATE(optin) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.updated_pipedrive; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(updated_pipedrive),INSERT(updated_pipedrive),UPDATE(updated_pipedrive) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.is_admin; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(is_admin) ON TABLE public.profiles TO authenticated;


--
-- Name: COLUMN profiles.is_staff; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT(is_staff) ON TABLE public.profiles TO authenticated;


--
-- Name: TABLE projects; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects TO service_role;


--
-- Name: TABLE projects_sharing; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects_sharing TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects_sharing TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.projects_sharing TO service_role;


--
-- Name: TABLE regions; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.regions TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.regions TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.regions TO service_role;

--
-- Name: TABLE versements; Type: ACL; Schema: public; Owner: -
--

GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.versements TO anon;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.versements TO authenticated;
GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLE public.versements TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;


--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON FUNCTIONS TO service_role;



--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO service_role;

--
-- Name: doc_frise_events handle_updated_at; Type: TRIGGER; Schema: public; Owner: -
--
create extension if not exists moddatetime schema extensions;
CREATE TRIGGER handle_updated_at BEFORE UPDATE ON public.doc_frise_events FOR EACH ROW EXECUTE FUNCTION extensions.moddatetime('updated_at');



--- TODO(cms)
--- Triggers disabled because they run HTTP queries we can't manage locally or in tests for the moment.

-- Performs an HTTP query on Nuxt3.
--
-- Name: event_procedure_status_handler(); Type: FUNCTION; Schema: public; Owner: -
--

-- CREATE FUNCTION public.event_procedure_status_handler() RETURNS trigger
--     LANGUAGE plpgsql
--     AS $$ declare procedure procedures; event_processed doc_frise_events; BEGIN IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then event_processed := new; else event_processed := old; END IF; SELECT * into procedure FROM procedures WHERE id = event_processed.procedure_id; PERFORM set_procedure_status(procedure); /* NUXT3_API_URL is hardcoded here because this dump will disappear soon and I don't know how to change it quickly in SQL. */ PERFORM net.http_get('api/urba/procedures/' || event_processed.procedure_id || '/update'); return event_processed; END; $$;

--
-- Name: doc_frise_events trigger_event_procedure_status_handler; Type: TRIGGER; Schema: public; Owner: -
--
-- CREATE TRIGGER trigger_event_procedure_status_handler AFTER INSERT OR DELETE OR UPDATE ON public.doc_frise_events FOR EACH ROW EXECUTE FUNCTION public.event_procedure_status_handler();

--
-- Name: FUNCTION event_procedure_status_handler(); Type: ACL; Schema: public; Owner: -
--

-- GRANT ALL ON FUNCTION public.event_procedure_status_handler() TO anon;
-- GRANT ALL ON FUNCTION public.event_procedure_status_handler() TO authenticated;
-- GRANT ALL ON FUNCTION public.event_procedure_status_handler() TO service_role;



-- Performs an HTTP query.
--
-- Name: procedure_status_handler(); Type: FUNCTION; Schema: public; Owner: -
--

-- CREATE FUNCTION public.procedure_status_handler() RETURNS trigger
--     LANGUAGE plpgsql
--     AS $$
-- declare
-- procedure procedures;
-- BEGIN
--   IF TG_OP = 'UPDATE' OR TG_OP = 'INSERT' then
--     procedure := new;
--   else
--     procedure := old;
--   END IF;

--   PERFORM set_procedure_status(procedure);

--   -- Perform the HTTP GET request
--   PERFORM http_get('api/urba/procedures/' || procedure.id || '/update');
--   return procedure;
-- END;
-- $$;

-- Performs an HTTP request on Pipedrive.
--
-- Name: projects_sharing Pipedrive Sharing Update; Type: TRIGGER; Schema: public; Owner: -
--

-- CREATE TRIGGER "Pipedrive Sharing Update" AFTER INSERT ON public.projects_sharing FOR EACH ROW EXECUTE FUNCTION supabase_functions.http_request('pipedrive/sharing', 'POST', '{"Content-type":"application/json"}', '{}', '10000');


-- Performs an HTTP request on Pipedrive.
--
-- Name: profiles Pipedrive Update; Type: TRIGGER; Schema: public; Owner: -
--

-- CREATE TRIGGER "Pipedrive Update" AFTER INSERT OR UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION supabase_functions.http_request('pipedrive/profiles', 'POST', '{"Content-type":"application/json"}', '{}', '1000');


-- The `auth.jwt()` function does not exist. It is installed by the `auth` Supabase service.
-- See https://github.com/supabase/auth/blob/master/migrations/00_init_auth_schema.up.sql
--
-- Name: projects_sharing Delete; Type: POLICY; Schema: public; Owner: -
--

-- CREATE POLICY "Delete" ON public.projects_sharing FOR DELETE USING ((public.is_admin(auth.uid()) OR (((auth.uid() = shared_by) OR (shared_by IS NULL)) AND ((auth.uid() = ( SELECT projects.owner
--    FROM public.projects
--   WHERE (projects.id = projects_sharing.project_id))) OR (EXISTS ( SELECT 1
--    FROM (public.projects p
--      JOIN public.profiles prof ON ((prof.user_id = auth.uid())))
--   WHERE ((p.id = projects_sharing.project_id) AND (prof.departement = (p.trame)::text)))) OR public.check_project_sharing_permission(project_id, (auth.jwt() ->> 'email'::text))))));


-- The `auth.jwt()` function does not exist. It is installed by the `auth` Supabase service.
-- See https://github.com/supabase/auth/blob/master/migrations/00_init_auth_schema.up.sql
--
-- Name: projects_sharing Insert; Type: POLICY; Schema: public; Owner: -
--

-- CREATE POLICY "Insert" ON public.projects_sharing FOR INSERT WITH CHECK ((public.is_admin(auth.uid()) OR ((auth.uid() = shared_by) AND ((auth.uid() = ( SELECT projects.owner
--    FROM public.projects
--   WHERE (projects.id = projects_sharing.project_id))) OR (EXISTS ( SELECT 1
--    FROM (public.projects p
--      JOIN public.profiles prof ON ((prof.user_id = auth.uid())))
--   WHERE ((p.id = projects_sharing.project_id) AND (prof.departement = (p.trame)::text)))) OR public.check_project_sharing_permission(project_id, (auth.jwt() ->> 'email'::text))))));



-- The `procedures_duplicate` seems to have been deleted. Remove me from the prod DB.
--
-- Name: procedures_duplicate_by_insee_codes(json); Type: FUNCTION; Schema: public; Owner: -
--

-- CREATE FUNCTION public.procedures_duplicate_by_insee_codes(codes json) RETURNS SETOF record
--     LANGUAGE sql
--     AS $$
-- SELECT *
-- FROM procedures_duplicate
-- WHERE EXISTS (
--   SELECT id, status, doc_type, current_perimetre, is_pluih
--   FROM jsonb_array_elements(current_perimetre) obj
--   WHERE ((obj->>'inseeCode')::text IN (
--     SELECT jsonb_array_elements_text(codes::jsonb)
--   )) and (status in ('opposable', 'en cours')) and (is_principale = true)
-- );
-- $$;

-- See procedures_duplicate_by_insee_codes
--
-- Name: FUNCTION procedures_duplicate_by_insee_codes(codes json); Type: ACL; Schema: public; Owner: -
--

-- GRANT ALL ON FUNCTION public.procedures_duplicate_by_insee_codes(codes json) TO anon;
-- GRANT ALL ON FUNCTION public.procedures_duplicate_by_insee_codes(codes json) TO authenticated;
-- GRANT ALL ON FUNCTION public.procedures_duplicate_by_insee_codes(codes json) TO service_role;

--
-- Name: FUNCTION procedure_status_handler(); Type: ACL; Schema: public; Owner: -
--

-- GRANT ALL ON FUNCTION public.procedure_status_handler() TO anon;
-- GRANT ALL ON FUNCTION public.procedure_status_handler() TO authenticated;
-- GRANT ALL ON FUNCTION public.procedure_status_handler() TO service_role;


--
-- Name: FUNCTION procedures_principales_by_collectivites(codes json); Type: ACL; Schema: public; Owner: -
--

-- GRANT ALL ON FUNCTION public.procedures_principales_by_collectivites(codes json) TO anon;
-- GRANT ALL ON FUNCTION public.procedures_principales_by_collectivites(codes json) TO authenticated;
-- GRANT ALL ON FUNCTION public.procedures_principales_by_collectivites(codes json) TO service_role;


-- ERROR:  must be member of role "supabase_admin"
--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: -
--

-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO postgres;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO anon;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO authenticated;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO service_role;

-- ERROR:  must be member of role "supabase_admin"
--
-- Name: DEFAULT PRIVILEGES FOR FUNCTIONS; Type: DEFAULT ACL; Schema: public; Owner: -
--

-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO postgres;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO anon;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO authenticated;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT ALL ON FUNCTIONS TO service_role;

-- ERROR:  must be member of role "supabase_admin"
--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: -
--

-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO postgres;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO anon;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO authenticated;
-- ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO service_role;

-- This is an ugly hack to know when the script is finished.
CREATE TABLE public.only_exists_in_test (
);


--
-- PostgreSQL database dump complete
--
