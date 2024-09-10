# SQL client that makes GreptimeDB panic
See https://github.com/GreptimeTeam/greptimedb/issues/4696 for details.

# Running within container

```bash
podman build --tag make_it_fail .
podman run -it --rm make_it_fail --host <GreptimeDB-IP> --port 4002 --database public
````

# Running on host

Install python and mariadb or mysql headers:
- `apt install libpython3.11-dev libmariadb-dev` on Debian/Ubuntu;
- `dnf install python3.11-devel mariadb-devel` on Fedora;
- `zypper install python311-devel libmariadb-devel` on Tumbleweed.

Create virtual environment and install python dependencies:
```bash
python3 -m venv ./.venv
. ./.venv/bin/activate
pip install -r requirements.txt
```

Run
```bash
python3 make_it_fail.py
```
or
```bash
python3 make_it_fail.py --host 127.0.0.1 --port 4002 --database public
```

Run `python3 make_if_fail.py --help` for more info.

Script support two drivers:
- [mysql-connector-python](https://dev.mysql.com/doc/connector-python/en/);
- [MySQLdb](https://mysqlclient.readthedocs.io/user_guide.html);

Both drivers cause the DB to fail, but MySQLdb causes the DB to crash more often.

Errors are unstable. One time you may get parse error, second time - unicode error, third time no error at all.
You may have to re-run the script several times (up to 10) to get crash.

With small batch size `--batch-size 10` I was able to insert all this data with both drivers.
Default batch size is 1000 rows.
