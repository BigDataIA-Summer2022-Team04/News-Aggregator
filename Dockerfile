FROM python:3.9.11

RUN pip install --upgrade pip

WORKDIR /app

ADD . /app

RUN pip install -r requirements.txt

EXPOSE 8095

CMD ["streamlit", "run", "main.py", "--server.port", "8095"]