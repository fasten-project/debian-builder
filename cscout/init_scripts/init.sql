/*
 * 1_init.sql
 * Copyright (C) 2019 Stefanos Chaliasos <schaliasos@protonmail.com>
 *
 * Distributed under terms of the MIT license.
 */

CREATE DATABASE wannadb;
CREATE USER wbadm WITH PASSWORD 'wannapass';
GRANT ALL PRIVILEGES ON DATABASE wannadb to wbadm;
ALTER USER wbadm CREATEROLE;

-- vim:et
