FROM python:3.13

WORKDIR /

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080 

RUN chmod +x /create_first_admin.py