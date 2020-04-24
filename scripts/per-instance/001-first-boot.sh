#!/bin/bash


# This script will be installed in /var/lib/cloud/scripts/per-instance
# and will be run automatically by DO at the droplet creation

# set user_data as env vars
user_vars=$(curl "http://169.254.169.254/metadata/v1/user-data")
echo $user_vars > /var/opt/meilisearch/env
. /var/opt/meilisearch/env

if [ $MEILI_SKIP_USER_INPUT = true ]; then
    # remove the auto-launch config at first login
    cp -f /etc/skel/.bashrc /root/.bashrc
fi 