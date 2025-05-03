FROM python:3.13

WORKDIR /

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# install Datadog agent
RUN apt-get update && apt-get install -y curl
RUN curl -o /tmp/datadog-agent.deb https://github.com/DataDog/datadog-agent/releases/download/7.27.1/datadog-agent_7.27.1-1_amd64.deb && dpkg -i /tmp/datadog-agent.deb
RUN rm -f /tmp/datadog-agent.deb

ENV DD_API_KEY=414ee0768f4524374447e43f51ddabdc
ENV DD_SITE=datadoghq.com

CMD service datadog-agent start && python -m flask run --host=0.0.0.0 --port=8080

EXPOSE 8080 
