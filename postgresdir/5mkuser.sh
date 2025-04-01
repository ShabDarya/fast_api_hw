#!/bin/bash
set -e

psql -v --username "postgres" --dbname "links" <<-EOSQL
	CREATE USER docker WITH PASSWORD 'user';
	GRANT ALL PRIVILEGES ON DATABASE links TO docker;
	GRANT ALL PRIVILEGES ON TABLE users TO docker;
	GRANT ALL PRIVILEGES ON TABLE urls TO docker;
	GRANT ALL PRIVILEGES ON TABLE stats TO docker;
EOSQL
