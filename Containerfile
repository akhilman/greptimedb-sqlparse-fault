from docker.io/python:3.11-bookworm

run apt update; apt install -y libmariadb-dev
run useradd -m -d /app bully
user bully
workdir /app
add data/*.csv data/
add make_it_fail.py requirements.txt ./
run python -m venv venv \
  && . venv/bin/activate \
  && pip install -r requirements.txt \
  && rm -r .cache
entrypoint ["/app/venv/bin/python3", "./make_it_fail.py"]

