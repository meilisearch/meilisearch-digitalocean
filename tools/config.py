import os
import requests

# Update with the Meilisearch version TAG you want to build the image with

MEILI_CLOUD_SCRIPTS_VERSION_TAG = 'v0.28.0'

# Script settings

DIGITALOCEAN_ACCESS_TOKEN = os.getenv('DIGITALOCEAN_ACCESS_TOKEN')
DIGITALOCEAN_END_POINT = 'https://api.digitalocean.com/v2'
SNAPSHOT_NAME = f'MeiliSearch-{MEILI_CLOUD_SCRIPTS_VERSION_TAG}-Debian-10.3'
# https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
SIZE_SLUG = 's-1vcpu-1gb'
USER_DATA = requests.get(
    f'https://raw.githubusercontent.com/meilisearch/cloud-scripts/{MEILI_CLOUD_SCRIPTS_VERSION_TAG}/scripts/providers/digitalocean/cloud-config.yaml'
).text

# Droplet settings

DROPLET_NAME = f'{SNAPSHOT_NAME}-BUILD'
DROPLET_TEST_NAME = f'{SNAPSHOT_NAME}-TEST'
DROPLET_TAGS = ['MARKETPLACE', 'AUTOBUILD']
ENABLE_BACKUPS = False
