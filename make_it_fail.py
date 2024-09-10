import pathlib
import sys
import csv
import collections
import itertools

import click

UUID = "2e4b2c04-35a5-4aea-96b1-09b9d6b15c7e"


@click.command(help="Makes DB fail.")
@click.option(
    "-h",
    "--host",
    default="127.0.0.1",
    type=click.STRING,
    envvar="DB_HOST",
    show_default=True,
    help="Connect to host.",
)
@click.option(
    "-P",
    "--port",
    default=4002,
    type=click.INT,
    envvar="DB_PORT",
    show_default=True,
    help="Port number to use for connection.",
)
@click.option(
    "-D",
    "--database",
    default="public",
    type=click.STRING,
    envvar="DB_DATABASE",
    show_default=True,
    help="Database to use.",
)
@click.option(
    "-p",
    "--data-path",
    default="./data",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        path_type=pathlib.Path,
    ),
    envvar="DB_DATA_PATH",
    show_default=True,
    help="Sample data directory path.",
)
@click.option(
    "-b",
    "--batch-size",
    default=1_000,
    type=click.IntRange(1, 1_000_000),
    envvar="BATCH_SIZE",
    show_default=True,
    help="Number rows single insert.",
)
@click.option(
    "-m",
    "--mysql-driver",
    default="mysqldb",
    type=click.Choice(["mysqldb", "mysql-connector"]),
    envvar="MYSQL_DRIVER",
    show_choices=True,
    show_default=True,
    help="MySQL driver to use.",
)
def main(host, port, database, data_path, batch_size, mysql_driver):
    if mysql_driver == "mysqldb":
        import MySQLdb  # type: ignore

        conn = MySQLdb.connect(
            host=host,
            port=port,
            database=database,
        )
    elif mysql_driver == "mysql-connector":
        from mysql.connector import MySQLConnection

        conn = MySQLConnection(
            host=host,
            port=port,
            database=database,
            sql_mode="TRADITIONAL",
        )
    else:
        raise ValueError("Unknown mysql driver")

    with conn:
        make_it_fail(conn, data_path, batch_size)


PublicTrade = collections.namedtuple(
    "PublicTrade", ("market", "ts", "price", "amount", "side")
)


def data_generator(data_path):
    for csv_file in data_path.glob("*.csv"):
        with open(csv_file, "r", newline="") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for ts, price, amount, side in reader:
                yield PublicTrade(
                    UUID, int(ts) * 1_000, float(price), float(amount), side
                )


def make_it_fail(conn, data_path, batch_size):
    with conn.cursor() as cur:
        cur.execute(
            """
            drop table if exists public_trades;
            create table public_trades (
                market String,
                ts TimestampMillisecond,
                price Float64,
                amount Float32,
                side Char,
                primary key (market),
                time index (ts)
            ) engine=mito with('append_mode'='true');
            """
        )

    data_gen = data_generator(data_path)
    with conn.cursor() as cur:
        while batch := list(itertools.islice(data_gen, batch_size)):
            sys.stdout.write(".")
            sys.stdout.flush()
            cur.executemany(
                """
                insert into public_trades (market, ts, price, amount, side)
                values (%s, %s, %s, %s, %s);
                """,
                batch,
            )
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
