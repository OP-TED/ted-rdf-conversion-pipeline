FROM docker.io/secoresearch/fuseki:5.3.0

USER root
RUN apk update && \
    apk add --no-cache procps


# Create a non-root user and group
RUN addgroup -S fuseki && adduser -S fuseki -G fuseki

# Ensure the /fuseki-base and /fuseki-data directories exist and set permissions
RUN mkdir -p /fuseki-base /fuseki-data/databases /tmp && \
    chown -R fuseki:fuseki /fuseki-base /fuseki-data /tmp

# Switch to the non-root user
USER fuseki







