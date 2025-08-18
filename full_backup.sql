--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: application; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.application (
    id integer NOT NULL,
    student_name character varying(100) NOT NULL,
    student_personnummer character varying(13) NOT NULL,
    parent_name character varying(100) NOT NULL,
    parent_email character varying(120) NOT NULL,
    parent_phone character varying(20) NOT NULL,
    address character varying(200) NOT NULL,
    postal_code character varying(10) NOT NULL,
    city character varying(50) NOT NULL,
    current_school character varying(100),
    musical_experience text,
    motivation text,
    grade_applying_for character varying(10) NOT NULL,
    has_transportation boolean,
    additional_info text,
    application_year character varying(9) NOT NULL,
    status character varying(30),
    email_confirmed boolean,
    email_confirmed_at timestamp without time zone,
    admin_notes text,
    created_at timestamp without time zone
);


ALTER TABLE public.application OWNER TO neondb_owner;

--
-- Name: application_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.application_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.application_id_seq OWNER TO neondb_owner;

--
-- Name: application_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.application_id_seq OWNED BY public.application.id;


--
-- Name: confirmation_codes; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.confirmation_codes (
    id integer NOT NULL,
    code character varying(64) NOT NULL,
    email character varying(120) NOT NULL,
    purpose character varying(50) NOT NULL,
    used boolean,
    used_at timestamp without time zone,
    created_at timestamp without time zone,
    expires_at timestamp without time zone NOT NULL
);


ALTER TABLE public.confirmation_codes OWNER TO neondb_owner;

--
-- Name: confirmation_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.confirmation_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.confirmation_codes_id_seq OWNER TO neondb_owner;

--
-- Name: confirmation_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.confirmation_codes_id_seq OWNED BY public.confirmation_codes.id;


--
-- Name: contact; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.contact (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(120) NOT NULL,
    phone character varying(20),
    subject character varying(200) NOT NULL,
    message text NOT NULL,
    created_at timestamp without time zone,
    is_read boolean
);


ALTER TABLE public.contact OWNER TO neondb_owner;

--
-- Name: contact_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.contact_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.contact_id_seq OWNER TO neondb_owner;

--
-- Name: contact_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.contact_id_seq OWNED BY public.contact.id;


--
-- Name: event; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.event (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    event_date timestamp without time zone NOT NULL,
    location character varying(200),
    ticket_url character varying(500),
    is_active boolean,
    created_at timestamp without time zone,
    info_to_parents text,
    coordinator_id integer
);


ALTER TABLE public.event OWNER TO neondb_owner;

--
-- Name: event_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.event_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_id_seq OWNER TO neondb_owner;

--
-- Name: event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.event_id_seq OWNED BY public.event.id;


--
-- Name: event_tasks; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.event_tasks (
    id integer NOT NULL,
    event_id integer NOT NULL,
    title character varying(200) NOT NULL,
    description text,
    assigned_to_user_id integer,
    completed boolean,
    completed_at timestamp without time zone,
    completed_by_user_id integer,
    created_at timestamp without time zone,
    due_offset_days integer,
    due_offset_hours integer
);


ALTER TABLE public.event_tasks OWNER TO neondb_owner;

--
-- Name: event_tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.event_tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.event_tasks_id_seq OWNER TO neondb_owner;

--
-- Name: event_tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.event_tasks_id_seq OWNED BY public.event_tasks.id;


--
-- Name: groups; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.groups (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    description character varying(200),
    created_at timestamp without time zone
);


ALTER TABLE public.groups OWNER TO neondb_owner;

--
-- Name: groups_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.groups_id_seq OWNER TO neondb_owner;

--
-- Name: groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.groups_id_seq OWNED BY public.groups.id;


--
-- Name: news_post; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.news_post (
    id integer NOT NULL,
    title character varying(200) NOT NULL,
    content text NOT NULL,
    author character varying(100),
    published_date timestamp without time zone,
    is_published boolean,
    featured boolean
);


ALTER TABLE public.news_post OWNER TO neondb_owner;

--
-- Name: news_post_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.news_post_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.news_post_id_seq OWNER TO neondb_owner;

--
-- Name: news_post_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.news_post_id_seq OWNED BY public.news_post.id;


--
-- Name: swish_payment; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.swish_payment (
    id character varying(32) NOT NULL,
    payee_payment_reference character varying(35) NOT NULL,
    payer_alias character varying(15),
    payee_alias character varying(15) NOT NULL,
    amount numeric(12,2) NOT NULL,
    currency character varying(3) NOT NULL,
    message character varying(50),
    callback_url character varying(500) NOT NULL,
    callback_identifier character varying(36) NOT NULL,
    status character varying(20),
    payment_reference character varying(32),
    error_code character varying(10),
    error_message character varying(1000),
    date_created timestamp without time zone,
    date_paid timestamp without time zone,
    date_cancelled timestamp without time zone,
    user_id integer,
    application_id integer,
    event_id integer
);


ALTER TABLE public.swish_payment OWNER TO neondb_owner;

--
-- Name: user_groups; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.user_groups (
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.user_groups OWNER TO neondb_owner;

--
-- Name: users; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.users (
    id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(256) NOT NULL,
    active boolean,
    created_at timestamp without time zone,
    last_login timestamp without time zone
);


ALTER TABLE public.users OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: neondb_owner
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO neondb_owner;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: neondb_owner
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: application id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.application ALTER COLUMN id SET DEFAULT nextval('public.application_id_seq'::regclass);


--
-- Name: confirmation_codes id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.confirmation_codes ALTER COLUMN id SET DEFAULT nextval('public.confirmation_codes_id_seq'::regclass);


--
-- Name: contact id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.contact ALTER COLUMN id SET DEFAULT nextval('public.contact_id_seq'::regclass);


--
-- Name: event id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event ALTER COLUMN id SET DEFAULT nextval('public.event_id_seq'::regclass);


--
-- Name: event_tasks id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_tasks ALTER COLUMN id SET DEFAULT nextval('public.event_tasks_id_seq'::regclass);


--
-- Name: groups id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.groups ALTER COLUMN id SET DEFAULT nextval('public.groups_id_seq'::regclass);


--
-- Name: news_post id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.news_post ALTER COLUMN id SET DEFAULT nextval('public.news_post_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: application; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.application (id, student_name, student_personnummer, parent_name, parent_email, parent_phone, address, postal_code, city, current_school, musical_experience, motivation, grade_applying_for, has_transportation, additional_info, application_year, status, email_confirmed, email_confirmed_at, admin_notes, created_at) FROM stdin;
\.


--
-- Data for Name: confirmation_codes; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.confirmation_codes (id, code, email, purpose, used, used_at, created_at, expires_at) FROM stdin;
\.


--
-- Data for Name: contact; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.contact (id, name, email, phone, subject, message, created_at, is_read) FROM stdin;
\.


--
-- Data for Name: event; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.event (id, title, description, event_date, location, ticket_url, is_active, created_at, info_to_parents, coordinator_id) FROM stdin;
\.


--
-- Data for Name: event_tasks; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.event_tasks (id, event_id, title, description, assigned_to_user_id, completed, completed_at, completed_by_user_id, created_at, due_offset_days, due_offset_hours) FROM stdin;
\.


--
-- Data for Name: groups; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.groups (id, name, description, created_at) FROM stdin;
1	admin	Fullständig tillgång till alla administrativa funktioner och användarhantering	\N
2	applications_manager	Kan hantera och granska studentansökningar samt godkänna nya elever	\N
3	event_manager	Kan skapa, redigera och hantera evenemang samt tilldela uppgifter	\N
4	parent	Förälder med tillgång till barnspecifik information och uppgifter	\N
\.


--
-- Data for Name: news_post; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.news_post (id, title, content, author, published_date, is_published, featured) FROM stdin;
\.


--
-- Data for Name: swish_payment; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.swish_payment (id, payee_payment_reference, payer_alias, payee_alias, amount, currency, message, callback_url, callback_identifier, status, payment_reference, error_code, error_message, date_created, date_paid, date_cancelled, user_id, application_id, event_id) FROM stdin;
\.


--
-- Data for Name: user_groups; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.user_groups (user_id, group_id) FROM stdin;
3	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.users (id, first_name, last_name, email, password_hash, active, created_at, last_login) FROM stdin;
3	Admin	User	admin@brunnsbomusikklasser.nu	scrypt:32768:8:1$NQCdBRMOPqX8HTao$44a62c44592bafe30d2d49e4aa9894ae2570d0a23b6bc7b286a3411b4c1597d7514a8f906f7cdec37536c7f362c09d87ed3938500d14a5cb81ddb214c4f201f2	t	2025-08-18 12:22:45.540379	\N
\.


--
-- Name: application_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.application_id_seq', 1, false);


--
-- Name: confirmation_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.confirmation_codes_id_seq', 1, false);


--
-- Name: contact_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.contact_id_seq', 1, false);


--
-- Name: event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.event_id_seq', 1, false);


--
-- Name: event_tasks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.event_tasks_id_seq', 1, false);


--
-- Name: groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.groups_id_seq', 4, true);


--
-- Name: news_post_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.news_post_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: neondb_owner
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: application application_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.application
    ADD CONSTRAINT application_pkey PRIMARY KEY (id);


--
-- Name: confirmation_codes confirmation_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.confirmation_codes
    ADD CONSTRAINT confirmation_codes_pkey PRIMARY KEY (id);


--
-- Name: contact contact_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.contact
    ADD CONSTRAINT contact_pkey PRIMARY KEY (id);


--
-- Name: event event_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_pkey PRIMARY KEY (id);


--
-- Name: event_tasks event_tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_tasks
    ADD CONSTRAINT event_tasks_pkey PRIMARY KEY (id);


--
-- Name: groups groups_name_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_name_key UNIQUE (name);


--
-- Name: groups groups_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.groups
    ADD CONSTRAINT groups_pkey PRIMARY KEY (id);


--
-- Name: news_post news_post_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.news_post
    ADD CONSTRAINT news_post_pkey PRIMARY KEY (id);


--
-- Name: swish_payment swish_payment_payee_payment_reference_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.swish_payment
    ADD CONSTRAINT swish_payment_payee_payment_reference_key UNIQUE (payee_payment_reference);


--
-- Name: swish_payment swish_payment_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.swish_payment
    ADD CONSTRAINT swish_payment_pkey PRIMARY KEY (id);


--
-- Name: user_groups user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_pkey PRIMARY KEY (user_id, group_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_confirmation_codes_code; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ix_confirmation_codes_code ON public.confirmation_codes USING btree (code);


--
-- Name: event event_coordinator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event
    ADD CONSTRAINT event_coordinator_id_fkey FOREIGN KEY (coordinator_id) REFERENCES public.users(id);


--
-- Name: event_tasks event_tasks_assigned_to_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_tasks
    ADD CONSTRAINT event_tasks_assigned_to_user_id_fkey FOREIGN KEY (assigned_to_user_id) REFERENCES public.users(id);


--
-- Name: event_tasks event_tasks_completed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_tasks
    ADD CONSTRAINT event_tasks_completed_by_user_id_fkey FOREIGN KEY (completed_by_user_id) REFERENCES public.users(id);


--
-- Name: event_tasks event_tasks_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.event_tasks
    ADD CONSTRAINT event_tasks_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id);


--
-- Name: swish_payment swish_payment_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.swish_payment
    ADD CONSTRAINT swish_payment_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.application(id);


--
-- Name: swish_payment swish_payment_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.swish_payment
    ADD CONSTRAINT swish_payment_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.event(id);


--
-- Name: swish_payment swish_payment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.swish_payment
    ADD CONSTRAINT swish_payment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_groups user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES public.groups(id);


--
-- Name: user_groups user_groups_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT SELECT,INSERT,REFERENCES,DELETE,TRIGGER,TRUNCATE,UPDATE ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

