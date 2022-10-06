import sys
import digitalocean
from utils import wait_for_droplet_creation, wait_for_health_check, \
    wait_for_droplet_shutdown, check_meilisearch_version, \
    destroy_droplet_and_exit, STATUS_OK, wait_for_droplet_ip

import config as conf

if len(sys.argv) > 1:
    SNAPSHOT_NAME = sys.argv[1]
else:
    raise Exception('No snapshot name specified')

print(f'Running test for image named: {SNAPSHOT_NAME}...')

# Get the snapshot for the test

manager = digitalocean.Manager(token=conf.DIGITALOCEAN_ACCESS_TOKEN)
images = manager.get_images()

MEILI_IMG = None
for img in images:
    if img.name == SNAPSHOT_NAME:
        MEILI_IMG = img
        print(f'Found image: {img.name} created at {img.created_at}')
        break

if MEILI_IMG is None:
    raise Exception(f'Couldn\'t find the specified image: {SNAPSHOT_NAME}')

# Create droplet from the retreived snapshot

droplet = digitalocean.Droplet(token=conf.DIGITALOCEAN_ACCESS_TOKEN,
                               name=conf.DROPLET_TEST_NAME,
                               region='lon1', # London
                               image=MEILI_IMG.id,
                               size_slug=conf.SIZE_SLUG,
                               tags=['meisearch-digitalocean-ci'],
                               backups=conf.ENABLE_BACKUPS)
droplet.create()

print('Creating droplet...')

# Wait for Droplet to be created

try:
    wait_for_droplet_creation(droplet)
    droplet = droplet.load()
except Exception as err:
    print(f'   Exception: {err}')
    destroy_droplet_and_exit(droplet)

print('Waiting until the droplet has an IP address')
IP_AVAILABLE = wait_for_droplet_ip(droplet, timeout_seconds=600)
if IP_AVAILABLE == STATUS_OK:
    print(f'   Droplet IP: {droplet.ip_address}')
else:
    print('   Timeout waiting for the IP address of the droplet')
    destroy_droplet_and_exit(droplet)

print(f'   Droplet created. IP: {droplet.ip_address}, ID: {droplet.id}')

# Wait for Health check after configuration is finished

print('Waiting for Health check (may take a few minutes)')
HEALTH = wait_for_health_check(droplet, timeout_seconds=1000)
if HEALTH == STATUS_OK:
    print('   Instance is healthy')
else:
    print('   Timeout waiting for health check')
    destroy_droplet_and_exit(droplet)

# Check version

print('Waiting for Version check')
try:
    check_meilisearch_version(
        droplet, conf.MEILI_CLOUD_SCRIPTS_VERSION_TAG)
except Exception as err:
    print(f'   Exception: {err}')
    destroy_droplet_and_exit(droplet)

print('   Version of meilisearch match!')

# Power down Droplet

print('Powering down droplet...')
try:
    shutdown = droplet.shutdown(return_dict=True)
    wait_for_droplet_shutdown(droplet)
except Exception as err:
    print(f'   Exception: {err}')
    destroy_droplet_and_exit(droplet)

print('   Droplet is OFF')

# Destroy Droplet

print('Destroying Droplet...')
droplet.destroy()
print('   Droplet destroyed')
