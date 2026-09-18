FROM ghcr.io/astral-sh/uv:python3.13-alpine

# Copy the project into the image
COPY . /usr/src

# Disable development dependencies
ENV UV_NO_DEV=1

# Sync the project into a new environment, asserting the lockfile is up to date.
WORKDIR /usr/src
RUN uv sync --locked

# Copy entrypoint scripts and update permissions to make them executable.
RUN ["chmod", "+x", "./docker/docker-entrypoint.sh"]
RUN ["chmod", "+x", "./docker/docker-entrypoint.prod.sh"]

ENTRYPOINT ["uv", "run", "./docker/docker-entrypoint.sh"]
