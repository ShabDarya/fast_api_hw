-- Table: urls

-- DROP TABLE IF EXISTS urls;

\c links;
CREATE TABLE IF NOT EXISTS urls
(
    id integer NOT NULL,
    save_url text NOT NULL,
    short_url text NOT NULL,
    created_by_login boolean NOT NULL,
    exp_time timestamp without time zone,
    CONSTRAINT urls_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS urls
    OWNER to postgres;