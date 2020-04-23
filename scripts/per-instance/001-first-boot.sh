#!/bin/bash


# This script will be installed in /var/lib/cloud/scripts/per-instance
# and will be run automatically by DO at the droplet creation

if [ MEILI_SKIP_USER_INPUT = true ]; then
    # remove the auto-launch config at first login
    cp -f /etc/skel/.bashrc /root/.bashrc

    user_vars=$("curl http://169.254.169.254/metadata/v1/user-data 2>/dev/null")
    echo user_vars > /var/opt/meilisearch/env
fi 