FROM python:3.13

ENV NEW_RELIC_APP_NAME="api-users"
ENV NEW_RELIC_LOG=stdout
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
ENV NEW_RELIC_LOG_LEVEL=info
ENV NEW_RELIC_CONFIG_FILE=newrelic.ini
ENV FLASK_APP=src.app:users_app
ENV PYTHONPATH=/src
ENV SECRET_KEY_SESSION=ids2g71c2025
ENV OAUTH_REDIRECT_URI=https://service-api-users.onrender.com/users/authorize
ENV GOOGLE_CLIENT_SECRET=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
ENV GOOGLE_CLIENT_ID=985128316026-v767el5qp9lanikh52up5m4ifs5usqdd.apps.googleusercontent.com
ENV FLASK_ENV=development

WORKDIR /

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install newrelic

COPY . .

CMD newrelic-admin run-program python -m flask run --host=0.0.0.0 --port=8080

EXPOSE 8080 
