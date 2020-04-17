export DEBIAN_FRONTEND=noninteractive

# Install build dependencies
echo "deb http://ftp.de.debian.org/debian sid main" >> /etc/apt/sources.list
apt update -y
apt install git curl ufw gcc make nginx certbot python-certbot-nginx -y
apt install gcc-10 -y

# Install MeiliSearch v0.10.0
wget --directory-prefix=/etc/meilisearch/ https://github.com/meilisearch/MeiliSearch/releases/download/v0.10.0/meilisearch.deb
apt install /etc/meilisearch/meilisearch.deb

# Prepare systemd service for MeiliSearch
cat << EOF >/etc/systemd/system/meilisearch.service
[Unit]
Description=MeiliSearch
After=systend-user-sessions.service

[Service]
Type=simple
ExecStart=/usr/bin/meilisearch

[Install]
WantedBy=default.target
EOF

# Start MeiliSearch service
systemctl enable meilisearch
systemctl start meilisearch

# Delete default Nginx config
rm /etc/nginx/sites-enabled/default

# Set Nginx to proxy MeiliSearch
cat << EOF > /etc/nginx/sites-enabled/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    location / {
        proxy_pass  http://127.0.0.1:7700;
    }
}
EOF
systemctl restart nginx

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

# Create SUDO user for MeiliSearch
useradd -e "" -s /bin/bash meilisearch
usermod -aG sudo meilisearch

# Delete remaining logs
rm -rf /var/log/*.log
rm -rf /root/.ssh/authorized_keys

curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/img_check.sh | bash
