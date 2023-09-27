FROM python:3.9-alpine
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8081
EXPOSE 8443
COPY . .

CMD ["python3", "app.py"]
