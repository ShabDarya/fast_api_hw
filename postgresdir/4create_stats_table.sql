-- Table: stats

-- DROP TABLE IF EXISTS stats;

\c links;
CREATE TABLE IF NOT EXISTS stats
(
    id integer NOT NULL,
    date_created timestamp without time zone NOT NULL,
    use_count integer NOT NULL,
    date_last timestamp without time zone,
    CONSTRAINT stats_pkey PRIMARY KEY (id),
    CONSTRAINT stats_id_fkey FOREIGN KEY (id)
        REFERENCES public.urls (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS stats
    OWNER to postgres;