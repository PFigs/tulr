FROM python:3.9

WORKDIR /opt/tulr

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN pip install .


ENV PYTHONUNBUFFERED=1
