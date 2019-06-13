/*
 * 3_seed.sql
 * Copyright (C) 2019 Stefanos Chaliasos <schaliasos@protonmail.com>
 *
 * Distributed under terms of the MIT license.
 */

\c wannadb
INSERT INTO distributions(distribution,build_dep_resolver) VALUES ('stretch','');
INSERT INTO architectures(architecture) VALUES ('amd64');
INSERT INTO distribution_architectures(distribution,architecture,archive) VALUES ('stretch','amd64','local');
INSERT INTO locks(distribution,architecture) VALUES ('stretch','amd64');
INSERT INTO distribution_aliases(distribution,alias) VALUES('stretch','stable')

-- vim:et
