FROM python:3.13

WORKDIR /

RUN apt-get update && apt-get install -y postgresql-client

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER password=$DB_PASSWORD" -f initialize_users_db.sql && python -m flask run --host=0.0.0.0 --port=8080

EXPOSE 8080 

RUN chmod +x /create_first_admin.py