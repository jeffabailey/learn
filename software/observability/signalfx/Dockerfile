FROM debian:stretch

# Install packages
RUN apt-get update && apt install -y postgresql postgresql-client dos2unix curl openssh-server vim netcat sudo

# Copy Script
COPY scripts/docker-entrypoint.sh /var/lib/postgresql/docker-entrypoint.sh
COPY scripts/setup.sql /var/lib/postgresql/setup.sql
COPY scripts/tcp-port-wait.sh /var/lib/postgresql/tcp-port-wait.sh

# Copy Config Files
COPY config/agent.yml /var/lib/postgresql/agent.yml
COPY config/signalfx-ingest-url.txt /var/lib/postgresql/
COPY config/signalfx-api-url.txt /var/lib/postgresql/
COPY config/signalfx-access-token.txt /var/lib/postgresql/

# Get the signalfx-agent library
RUN curl -L https://github.com/signalfx/signalfx-agent/releases/download/v5.2.1/signalfx-agent-5.2.1.tar.gz --output /var/lib/postgresql/signalfx-agent-5.2.1.tar.gz

# Extract the signalfx-agent library
RUN cd /var/lib/postgresql && tar -xzvf /var/lib/postgresql/signalfx-agent-5.2.1.tar.gz

# Prep the docker entrypoint, if on windows fix up the file
RUN ["chmod", "+x", "/var/lib/postgresql/docker-entrypoint.sh"]
RUN ["dos2unix", "/var/lib/postgresql/docker-entrypoint.sh"]

RUN ["chmod", "+x", "/var/lib/postgresql/tcp-port-wait.sh"]
RUN ["dos2unix", "/var/lib/postgresql/tcp-port-wait.sh"]

RUN echo "postgres ALL=(ALL:ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/postgres
RUN usermod -a -G sudo postgres

# Expose postgres 
EXPOSE  5432

USER postgres
RUN cd ~postgres

# Args & environment
ARG signalfx_realm
ENV SIGNALFX_REALM=${signalfx_realm}

ARG signalfx_access_token
ENV SIGNALFX_ACCESS_TOKEN=${signalfx_access_token}

ENTRYPOINT ["/var/lib/postgresql/docker-entrypoint.sh"]