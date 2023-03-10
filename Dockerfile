FROM python:latest

WORKDIR /service/

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY entrypoint.sh entrypoint.sh
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]

COPY alembic.ini alembic.ini
COPY alembic/ alembic/

COPY users.ini users.ini
COPY app/ app/
