FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

WORKDIR /
ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt

ADD ./app /app
RUN python app/load_fixture.py