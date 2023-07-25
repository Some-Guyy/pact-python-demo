FROM --platform=linux/amd64 python:3.11-slim AS base

ARG SERVICE=frontend

ENV ENV_SERVICE=$SERVICE

WORKDIR /app

COPY ./requirements.txt .


FROM base AS test

ARG PROVIDER_VERSION=""

ENV ENV_PROVIDER_VERSION=$PROVIDER_VERSION

COPY ./requirements-dev.txt .

RUN pip install -r requirements-dev.txt

COPY . .

RUN chmod +x tests/contract/pact_test_$SERVICE.sh

CMD ./tests/contract/pact_test_$ENV_SERVICE.sh $ENV_PROVIDER_VERSION


FROM base AS prod

RUN pip install -r requirements.txt

COPY . .

CMD uvicorn src.$ENV_SERVICE:app --port 8080 --reload
