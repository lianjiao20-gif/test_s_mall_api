FROM node:24-bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends make python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

WORKDIR /app
ARG NPM_REGISTRY=https://mirrors.tencent.com/npm/
RUN --mount=type=cache,target=/root/.npm \
    npm install --global --registry="$NPM_REGISTRY" allure@3

COPY requirements.txt ./
ARG PIP_INDEX_URL=https://mirrors.tencent.com/pypi/simple/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --index-url "$PIP_INDEX_URL" -r requirements.txt

COPY . .

ARG VCS_URL
LABEL org.opencontainers.image.source="${VCS_URL}"

CMD ["make", "test"]
