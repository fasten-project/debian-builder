#! /bin/sh
psql -d wannadb -f /srv/wanna-build/schema/main-tables.sql
psql -d wannadb -f /srv/wanna-build/schema/roles.sql
psql -d wannadb -f /srv/wanna-build/schema/arches-tables.sql

