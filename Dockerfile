FROM python:3.11-bullseye

ARG GITHUB_SHA_ARG

ENV REDIS_HOST="localhost" \
    REDIS_PORT=6379        \
    REDIS_PASS=""          \
    WEATHER_GOV_API_URL="https://api.weather.gov"

WORKDIR /opt

COPY src/weathergov /opt/weathergov
COPY poetry.lock pyproject.toml .

RUN pip install poetry==1.4.0 \
 && poetry config virtualenvs.create false \
 && poetry install

#
# Entry point for the web app. Entry point for the loaders will be different
ENTRYPOINT ["gunicorn", "-b=0.0.0.0:80", "--log-level=debug", "--timeout=90", "--workers=2", "--threads=2"]

CMD ["weathergov.run_app:server"]
