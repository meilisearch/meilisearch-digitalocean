# This script will be installed in /var/lib/cloud/scripts/per-instance
# and will be run automatically by DO at the droplet creation

useradd -e "" -s /bin/bash samtest
usermod -aG sudo samtest