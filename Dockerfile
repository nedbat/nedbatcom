FROM python:3.9-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    pkg-config \
    build-essential python3-dev python3-cffi \
    git \
    default-libmysqlclient-dev \
 && rm -rf /var/lib/apt/lists/* \
 && adduser --system --group --home /usr/src/app --disabled-login stell

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements/server.txt server-requirements.txt
RUN python3 -m pip install --no-cache-dir -r server-requirements.txt
