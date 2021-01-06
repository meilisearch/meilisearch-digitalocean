curl https://raw.githubusercontent.com/meilisearch/meilisearch-cloud/main/scripts/deploy-meilisearch.sh | sh

# Clean up image using DigitalOcean scripts
curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/cleanup.sh | bash

# Reset os-release file
cat << EOF > /etc/os-release
PRETTY_NAME="Debian GNU/Linux 10 (buster)"
NAME="Debian GNU/Linux"
VERSION_ID="10"
VERSION="10 (buster)"
VERSION_CODENAME=buster
ID=debian
HOME_URL="https://www.debian.org/"
SUPPORT_URL="https://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
EOF

# Setup firewalls and Nginx
ufw allow 'Nginx Full'
ufw allow 'OpenSSH'
ufw --force enable

# Delete remaining logs

rm -rf /root/.ssh/authorized_keys
rm -rf /tmp/meili-tmp
rm -rf /var/log/*.log

curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/img_check.sh | bash
