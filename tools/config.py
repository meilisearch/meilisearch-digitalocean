import os
import requests

# Update with the MeiliSearch version TAG you want to build the image with

MEILI_CLOUD_SCRIPTS_VERSION_TAG = 'v0.19.0'

# Update with the fingerprint of your own SSH key after uploading it to DigitalOcean Settings => Security

SSH_KEYS_FINGERPRINTS = [
    'd4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc'
]

# Script settings

DIGITALOCEAN_ACCESS_TOKEN = os.getenv('DIGITALOCEAN_ACCESS_TOKEN')
DIGITALOCEAN_END_POINT = 'https://api.digitalocean.com/v2'
SNAPSHOT_NAME = 'MeiliSearch-{}-Debian-10.3'.format(
    MEILI_CLOUD_SCRIPTS_VERSION_TAG)
# https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
SIZE_SLUG = 's-1vcpu-1gb'
PROVIDER_NAME = 'digitalocean'
USER_DATA = requests.get(
    'https://raw.githubusercontent.com/meilisearch/cloud-scripts/{}/scripts/cloud-config.yaml'.format(MEILI_CLOUD_SCRIPTS_VERSION_TAG)).text.replace('unknown_provider', PROVIDER_NAME)


# Droplet settings

DROPLET_NAME = '{}-BUILD'.format(SNAPSHOT_NAME)
DROPLET_TAGS = ['MARKETPLACE', 'AUTOBUILD']
ENABLE_BACKUPS = False
