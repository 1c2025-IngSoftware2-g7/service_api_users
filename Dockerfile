FROM python:3.13

ENV NEW_RELIC_APP_NAME="api-users"
ENV NEW_RELIC_LOG=stdout
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
ENV NEW_RELIC_LOG_LEVEL=info
ENV NEW_RELIC_CONFIG_FILE=newrelic.ini
ENV FLASK_APP=src.app:users_app
ENV PYTHONPATH=/src
ENV FLASK_ENV=development

WORKDIR /

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install newrelic

COPY . .

CMD newrelic-admin run-program python -m flask run --host=0.0.0.0 --port=8080

EXPOSE 8080 
