export DEBIAN_FRONTEND=noninteractive

# Install build dependencies
echo "deb http://ftp.de.debian.org/debian sid main" >> /etc/apt/sources.list
apt update -y
apt upgrade -y
apt install git curl ufw gcc make nginx certbot python-certbot-nginx qemu-utils gcc-10 -y

# Install MeiliSearch v0.10.1
wget --directory-prefix=/etc/meilisearch/ https://github.com/meilisearch/MeiliSearch/releases/download/v0.10.1/meilisearch.deb
apt install /etc/meilisearch/meilisearch.deb

# Prepare systemd service for MeiliSearch
cat << EOF >/etc/systemd/system/meilisearch.service
[Unit]
Description=MeiliSearch
After=systemd-user-sessions.service

[Service]
Type=simple
ExecStart=/usr/bin/meilisearch --db-path /var/lib/meilisearch

[Install]
WantedBy=default.target
EOF

# Start MeiliSearch service
systemctl enable meilisearch
systemctl start meilisearch

# Delete default Nginx config
rm /etc/nginx/sites-enabled/default

# Set Nginx to proxy MeiliSearch
cat << EOF > /etc/nginx/sites-enabled/meilisearch
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

# Copy MeiliSearch configuration scripts
mkdir -p /var/log/meilisearch
mkdir -p /var/lib/meilisearch
mkdir -p /var/opt/meilisearch/scripts/first-login
git clone https://github.com/meilisearch/meilisearch-digital-ocean.git /tmp/meili-tmp
cd /tmp/meili-tmp
git checkout v0.10.1
chmod 755 /tmp/meili-tmp/scripts/per-instance/*
chmod 755 /tmp/meili-tmp/scripts/first-login/*
chmod 755 /tmp/meili-tmp/scripts/MOTD/*
cp -r /tmp/meili-tmp/scripts/per-instance/* /var/lib/cloud/scripts/per-instance/.
cp -r /tmp/meili-tmp/scripts/first-login/* /var/opt/meilisearch/scripts/first-login/.
cp -r /tmp/meili-tmp/scripts/MOTD/* /etc/update-motd.d/.

# Set launch MeiliSearch first login script
touch /var/opt/meilisearch/env
echo "source /var/opt/meilisearch/env" >> /root/.bashrc
echo "source /var/opt/meilisearch/env" >> /etc/skel/.bashrc
echo "sh /var/opt/meilisearch/scripts/first-login/000-set-meili-env.sh" >> /root/.bashrc

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
