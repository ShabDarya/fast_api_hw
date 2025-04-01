#!/bin/bash
set -e

psql -c CREATE USER weeeeeee WITH PASSWORD 'user';
psql -c GRANT ALL PRIVILEGES ON DATABASE links TO user;
