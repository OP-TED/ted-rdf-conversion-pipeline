#!/bin/bash
set -e # exit immediately if a command exits with a non-zero status.

POSTGRES="psql --username postgres"

# create database for superset
echo "Creating database: metabase"
$POSTGRES <<EOSQL
CREATE DATABASE $ENV_MB_DB_DBNAME OWNER $ENV_MB_DB_USER;
EOSQL
