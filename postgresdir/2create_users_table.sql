-- Table: links.users

-- DROP TABLE IF EXISTS public.users;
\c links;
CREATE TABLE IF NOT EXISTS users
(
    login text NOT NULL,
    password text NOT NULL,
    CONSTRAINT users_pkey PRIMARY KEY (login)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS users
    OWNER to postgres;