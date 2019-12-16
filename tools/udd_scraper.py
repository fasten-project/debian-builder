#!/usr/bin/env python3
import argparse
import psycopg2


HOST = "udd-mirror.debian.net"
USER = "udd-mirror"
DBNAME = "udd"
PASSWORD = "udd-mirror"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def query_udd(release, limit):
    conn = psycopg2.connect(
        host=HOST, user=USER, password=PASSWORD, dbname=DBNAME
    )
    cur = conn.cursor()
    query = ("SELECT DISTINCT all_packages.source, popcon.vote "
             "FROM all_packages "
             "INNER JOIN sources ON all_packages.source = sources.source "
             "INNER JOIN popcon ON all_packages.package = popcon.package WHERE "
             "all_packages.release = '{}' AND "
             "tag LIKE '%implemented-in::c%' "
             "ORDER BY popcon.vote DESC LIMIT {}"
            ).format(release, limit)
    print(query)
    cur.execute(query)
    res = cur.fetchall()
    res = set([x[0] for x in res])  # Remove duplicates
    return '\n'.join(res)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', type=int, default=100,
                        help='Number of packages to find'
                       )
    parser.add_argument('-r', '--release', default='buster',
                        help='Debian release'
                       )
    args = parser.parse_args()
    res = query_udd(args.release, args.number)
    print(res)


if __name__ == "__main__":
    main()
