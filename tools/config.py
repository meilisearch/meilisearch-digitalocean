import os
import requests

# Update with the MeiliSearch version TAG you want to build the image with

MEILI_CLOUD_SCRIPTS_VERSION_TAG = 'v0.22.0'

# Script settings

DIGITALOCEAN_ACCESS_TOKEN = os.getenv('DIGITALOCEAN_ACCESS_TOKEN')
DIGITALOCEAN_END_POINT = 'https://api.digitalocean.com/v2'
SNAPSHOT_NAME = 'MeiliSearch-{}-Debian-10.3-TEST-DUMP'.format(
    MEILI_CLOUD_SCRIPTS_VERSION_TAG)
# https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
SIZE_SLUG = 's-1vcpu-1gb'
USER_DATA = requests.get(
    'https://raw.githubusercontent.com/meilisearch/cloud-scripts/dump-dir/scripts/providers/digitalocean/cloud-config.yaml'
).text

# Droplet settings

DROPLET_NAME = '{}-BUILD'.format(SNAPSHOT_NAME)
DROPLET_TEST_NAME = '{}-TEST'.format(SNAPSHOT_NAME)
DROPLET_TAGS = ['MARKETPLACE', 'AUTOBUILD']
ENABLE_BACKUPS = False
