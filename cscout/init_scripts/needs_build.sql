/*
 * 3_seed.sql
 * Copyright (C) 2019 Stefanos Chaliasos <schaliasos@protonmail.com>
 *
 * Distributed under terms of the MIT license.
 */

\c wannadb
UPDATE packages
    SET state = 'Needs-Build';
UPDATE packages
    SET state = 'failed'
    WHERE package = 'rootskel';

-- vim:et
