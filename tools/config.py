import os

# Update with the MeiliSearch version TAG you want to build the image with

MEILI_CLOUD_SCRIPTS_VERSION_TAG = 'v0.19.0'

# Script settings

DIGITALOCEAN_ACCESS_TOKEN = os.getenv('DIGITALOCEAN_ACCESS_TOKEN')
DIGITALOCEAN_END_POINT = 'https://api.digitalocean.com/v2'
SNAPSHOT_NAME = 'MeiliSearch-{}-Debian-10.3'.format(
    MEILI_CLOUD_SCRIPTS_VERSION_TAG)
# https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
SIZE_SLUG = 's-1vcpu-1gb'
PROVIDER_NAME = 'digitalocean'

# Droplet settings

DROPLET_NAME = '{}-BUILD'.format(SNAPSHOT_NAME)
DROPLET_TAGS = ['MARKETPLACE', 'AUTOBUILD']
ENABLE_BACKUPS = False

# Cloud-init

USER_DATA = """
#cloud-config

package_update: true

package_upgrade: true

users:
  - default
  - name: meilisearch
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    ssh_import_id: root
    lock_passwd: True
    shell: /bin/bash
    groups: [sudo]
  - name: root
    shell: /bin/bash

packages:  
  - git
  - curl
  - ufw
  - gcc
  - make
  - nginx
  - certbot
  - python-certbot-nginx

write_files:
  - path: /etc/systemd/system/meilisearch.service
    content: |
      [Unit]
      Description=MeiliSearch
      After=systemd-user-sessions.service

      [Service]
      Type=simple
      ExecStart=/usr/bin/meilisearch --db-path /var/lib/meilisearch/data.ms --env development
      Environment='MEILI_SERVER_PROVIDER=digitalocean'

      [Install]
      WantedBy=default.target

  - path: /etc/nginx/sites-enabled/meilisearch
    content: |
      server {{
          listen 80 default_server;
          listen [::]:80 default_server;

          server_name _;

          location / {{
              proxy_pass  http://127.0.0.1:7700;
          }}

          client_max_body_size 100M;
      }}
  
  - path: /etc/nginx/sites-enabled/default
    content: |
      # Empty file

  - path: /etc/profile.d/00-aliases.sh
    content: |
      alias meilisearch-setup='sudo sh /var/opt/meilisearch/scripts/first-login/000-set-meili-env.sh'

  - path: /etc/profile.d/01-auto-run.sh
    content: |
      meilisearch-setup

runcmd:
  - wget --directory-prefix=/usr/bin/ -O /usr/bin/meilisearch https://github.com/meilisearch/MeiliSearch/releases/download/{0}/meilisearch-linux-amd64
  - chmod 755 /usr/bin/meilisearch
  - systemctl enable meilisearch.service
  - ufw --force enable
  - ufw allow 'Nginx Full'
  - ufw allow 'OpenSSH'
  - rm -rf /var/log/*.log
  - curl https://raw.githubusercontent.com/meilisearch/cloud-scripts/{0}/scripts/deploy-meilisearch.sh | bash -s {0}
  - curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/img_check.sh | bash
  - curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/cleanup.sh | bash

power_state:
  mode: reboot
  message: Bye Bye
  timeout: 10
  condition: True
""".format(MEILI_CLOUD_SCRIPTS_VERSION_TAG)
