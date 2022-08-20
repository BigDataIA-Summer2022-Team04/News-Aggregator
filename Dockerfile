FROM python:3.9.11

RUN pip install --upgrade pip

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8090

CMD ["gunicorn" ,"-w", "4", "-k", "uvicorn.workers.UvicornWorker" , "--bind", "0.0.0.0:8090", "main:app"]