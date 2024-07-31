FROM docker.io/secoresearch/fuseki:4.5.0

USER root
RUN apt-get update; \
    apt-get install -y --no-install-recommends procps


# Create a non-root user and group
RUN groupadd -r fuseki && useradd -r -g fuseki fuseki

# Ensure the /fuseki-base and /fuseki-data directories exist and set permissions
RUN mkdir -p /fuseki-base /fuseki-data/databases /tmp && \
    chown -R fuseki:fuseki /fuseki-base /fuseki-data /tmp

# Switch to the non-root user
USER fuseki







