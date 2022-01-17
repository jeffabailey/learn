#!/usr/bin/env bash
set -e
echo "Starting docker-entrypoint.sh"
export PG_VERSION="9.6"
export PG_CONF_PATH="/etc/postgresql/${PG_VERSION}/main"
export PG_HBA_CONF_FILE="${PG_CONF_PATH}/pg_hba.conf"
export PG_CONF_FILE="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"

# Update configurations
## Allow connections
echo "local all all trust" >> "${PG_HBA_CONF_FILE}"
echo "host all all all trust" >> "${PG_HBA_CONF_FILE}"

echo "listen_addresses = '*'" >> "${PG_CONF_FILE}"
echo "shared_preload_libraries = 'pg_stat_statements'" >> "${PG_CONF_FILE}"

# # Start it up
sudo service postgresql start && /var/lib/postgresql/tcp-port-wait.sh 127.0.0.1 5432

# Create the db and set it up
sudo su -c "psql -U postgres -tc \"SELECT 1 FROM pg_database WHERE datname = 'learnsignalfx'\" | grep -q 1 || psql -U postgres -c \"create database learnsignalfx\"" postgres &&
psql -f ~postgres/setup.sql

# The signalfx-agent needs a host entry
sudo su -c "echo '127.0.0.1 learn-signalfx' >> /etc/hosts" root

# Start the SFX agent
cd ~ && ./signalfx-agent/bin/signalfx-agent -config ./agent.yml &&

exec "$@"