/*
Fichier généré à partir de la commande suivante :
pg_dump --schema-only --no-owner --no-acl --no-policies --no-security-labels \
  --table=procedures \
  --table=doc_frise_events \
  --table=procedures_perimetres \
  --table=profiles \
  --table=projects \
  --table=auth.users

Puis :
1. Supprime \restrict et \unrestrict
2. Supprime les SET initiaux
3. Supprime `extensions.`
4. Supprime trigger "Pipedrive Update" car utilise une fonction Supabase
5. Remplace trigger_event_procedure_status_handler car la fonction appellée utilise une fonction Supabase. Le trigger remplaçant n'est jamais appelé (WHEN (false)).
6. Ajoute la création du schéma auth

*/

--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1 (Ubuntu 15.1-1.pgdg20.04+1)
-- Dumped by pg_dump version 18.2 (Homebrew)

--
-- Name: doc_frise_events; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.doc_frise_events (
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
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
    archived boolean GENERATED ALWAYS AS (((doublon_cache_de_id IS NOT NULL) OR soft_delete)) STORED
);


--
-- Name: auth; Type: SCHEMA; Schema: -; Owner: -
--
-- ⚠️ Ajout manuel
CREATE SCHEMA auth;


--
-- Name: users; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE auth.users (
    instance_id uuid,
    id uuid NOT NULL,
    aud character varying(255),
    role character varying(255),
    email character varying(255),
    encrypted_password character varying(255),
    email_confirmed_at timestamp with time zone,
    invited_at timestamp with time zone,
    confirmation_token character varying(255),
    confirmation_sent_at timestamp with time zone,
    recovery_token character varying(255),
    recovery_sent_at timestamp with time zone,
    email_change_token_new character varying(255),
    email_change character varying(255),
    email_change_sent_at timestamp with time zone,
    last_sign_in_at timestamp with time zone,
    raw_app_meta_data jsonb,
    raw_user_meta_data jsonb,
    is_super_admin boolean,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    phone text DEFAULT NULL::character varying,
    phone_confirmed_at timestamp with time zone,
    phone_change text DEFAULT ''::character varying,
    phone_change_token character varying(255) DEFAULT ''::character varying,
    phone_change_sent_at timestamp with time zone,
    confirmed_at timestamp with time zone GENERATED ALWAYS AS (LEAST(email_confirmed_at, phone_confirmed_at)) STORED,
    email_change_token_current character varying(255) DEFAULT ''::character varying,
    email_change_confirm_status smallint DEFAULT 0,
    banned_until timestamp with time zone,
    reauthentication_token character varying(255) DEFAULT ''::character varying,
    reauthentication_sent_at timestamp with time zone,
    is_sso_user boolean DEFAULT false NOT NULL,
    deleted_at timestamp with time zone,
    is_anonymous boolean DEFAULT false NOT NULL,
    CONSTRAINT users_email_change_confirm_status_check CHECK (((email_change_confirm_status >= 0) AND (email_change_confirm_status <= 2)))
);


--
-- Name: TABLE users; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE auth.users IS 'Auth: Stores user login data within a secure schema.';


--
-- Name: COLUMN users.is_sso_user; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN auth.users.is_sso_user IS 'Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.';


--
-- Name: procedures_perimetres; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.procedures_perimetres (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    added_at timestamp with time zone DEFAULT now(),
    collectivite_code text NOT NULL,
    collectivite_type text NOT NULL,
    procedure_id uuid NOT NULL,
    opposable boolean NOT NULL,
    departement text,
    commune_id text GENERATED ALWAYS AS (((collectivite_code || '_'::text) || collectivite_type)) STORED NOT NULL
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
    id uuid DEFAULT uuid_generate_v4() NOT NULL,
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
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_phone_key UNIQUE (phone);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY auth.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


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
-- Name: procedures_perimetres procedures_perimetres_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures_perimetres
    ADD CONSTRAINT procedures_perimetres_pkey PRIMARY KEY (id);


--
-- Name: procedures procedures_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT procedures_pkey PRIMARY KEY (id);


--
-- Name: profiles profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (user_id);


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
-- Name: procedures_perimetres uniq_perimeters_collectivite_procedure_type_couple_ids; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures_perimetres
    ADD CONSTRAINT uniq_perimeters_collectivite_procedure_type_couple_ids UNIQUE (collectivite_code, procedure_id, collectivite_type);


--
-- Name: confirmation_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX confirmation_token_idx ON auth.users USING btree (confirmation_token) WHERE ((confirmation_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: email_change_token_current_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX email_change_token_current_idx ON auth.users USING btree (email_change_token_current) WHERE ((email_change_token_current)::text !~ '^[0-9 ]*$'::text);


--
-- Name: email_change_token_new_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX email_change_token_new_idx ON auth.users USING btree (email_change_token_new) WHERE ((email_change_token_new)::text !~ '^[0-9 ]*$'::text);


--
-- Name: reauthentication_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX reauthentication_token_idx ON auth.users USING btree (reauthentication_token) WHERE ((reauthentication_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: recovery_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX recovery_token_idx ON auth.users USING btree (recovery_token) WHERE ((recovery_token)::text !~ '^[0-9 ]*$'::text);


--
-- Name: users_email_partial_key; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX users_email_partial_key ON auth.users USING btree (email) WHERE (is_sso_user = false);


--
-- Name: INDEX users_email_partial_key; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON INDEX auth.users_email_partial_key IS 'Auth: A partial unique index that applies only when is_sso_user is false';


--
-- Name: users_instance_id_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_instance_id_email_idx ON auth.users USING btree (instance_id, lower((email)::text));


--
-- Name: users_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_instance_id_idx ON auth.users USING btree (instance_id);


--
-- Name: users_is_anonymous_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX users_is_anonymous_idx ON auth.users USING btree (is_anonymous);


--
-- Name: aaaaa; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX aaaaa ON public.doc_frise_events USING btree (procedure_id, date_iso DESC, type, is_valid);


--
-- Name: departement_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX departement_idx ON public.procedures_perimetres USING btree (departement);


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
-- Name: procedure_including_commune_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX procedure_including_commune_idx ON public.procedures_perimetres USING btree (procedure_id) INCLUDE (commune_id);


--
-- Name: procedures_perimetres_commune_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX procedures_perimetres_commune_id_idx ON public.procedures_perimetres USING btree (commune_id);


--
-- Name: procedures_perimetres_commune_id_including_procedure; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX procedures_perimetres_commune_id_including_procedure ON public.procedures_perimetres USING btree (commune_id) INCLUDE (procedure_id);


--
-- Name: procedures_pkey_secondary_null_not_archived; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX procedures_pkey_secondary_null_not_archived ON public.procedures USING btree (id) WHERE ((secondary_procedure_of IS NULL) AND (NOT archived));


--
-- Name: test_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX test_idx ON public.procedures_perimetres USING btree (procedure_id, collectivite_code);


--
-- Name: test_index; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX test_index ON public.doc_frise_events USING btree (procedure_id, date_iso);


--
-- Name: profiles Pipedrive Update; Type: TRIGGER; Schema: public; Owner: -
--
-- ⚠️ Désactivé car utilise une fonction Supabase
-- CREATE TRIGGER "Pipedrive Update" AFTER INSERT OR UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION supabase_functions.http_request('https://docurba.beta.gouv.fr/api/pipedrive/profiles', 'POST', '{"Content-type":"application/json"}', '{}', '1000');


--
-- Name: doc_frise_events handle_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER handle_updated_at BEFORE UPDATE ON public.doc_frise_events FOR EACH ROW EXECUTE FUNCTION moddatetime('updated_at');


--
-- Name: doc_frise_events trigger_event_procedure_status_handler; Type: TRIGGER; Schema: public; Owner: -
--
-- ⚠️ Désactive car la fonction appelée utilise des fonctions Supabase
-- ⚠️ Remplacée par un trigger jamais exécuté (WHEN (false)) pour pouvoir le désactiver
-- CREATE TRIGGER trigger_event_procedure_status_handler AFTER INSERT OR DELETE OR UPDATE ON public.doc_frise_events FOR EACH ROW EXECUTE FUNCTION public.event_procedure_status_handler();
CREATE TRIGGER trigger_event_procedure_status_handler AFTER INSERT OR DELETE OR UPDATE ON public.doc_frise_events FOR EACH ROW WHEN (false) EXECUTE FUNCTION moddatetime('updated_at');


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
-- Name: doc_frise_events public_doc_frise_events_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.doc_frise_events
    ADD CONSTRAINT public_doc_frise_events_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id) ON DELETE CASCADE;


--
-- Name: procedures public_procedures_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures
    ADD CONSTRAINT public_procedures_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.profiles(user_id) ON DELETE SET NULL;


--
-- Name: procedures_perimetres public_procedures_perimetres_procedure_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.procedures_perimetres
    ADD CONSTRAINT public_procedures_perimetres_procedure_id_fkey FOREIGN KEY (procedure_id) REFERENCES public.procedures(id) ON DELETE CASCADE;


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
-- PostgreSQL database dump complete
--
