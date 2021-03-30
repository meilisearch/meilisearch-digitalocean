import sys
import digitalocean
from utils import wait_for_droplet_creation, wait_for_health_check, \
    wait_for_droplet_shutdown, check_meilisearch_version, destroy_droplet_and_exit, STATUS_OK

import config as conf

if len(sys.argv) > 1:
    SNAPSHOT_NAME = sys.argv[1]
else:
    raise Exception("No snapshot name specified")

print("Running test for image named: {name}...".format(
    name=SNAPSHOT_NAME))

# Get the snapshot for the test

manager = digitalocean.Manager(token=conf.DIGITALOCEAN_ACCESS_TOKEN)
images = manager.get_images()

MEILI_IMG = None
for img in images:
    if img.name == SNAPSHOT_NAME:
        MEILI_IMG = img
        print("Found image: {name} created at {created_at}".format(
            name=img.name,
            created_at=img.created_at
        ))
        break

if MEILI_IMG is None:
    raise Exception("Couldn't find the specified image: {}".format(
        SNAPSHOT_NAME))

# Create droplet from the retreived snapshot

droplet = digitalocean.Droplet(token=conf.DIGITALOCEAN_ACCESS_TOKEN,
                               name=conf.DROPLET_TEST_NAME,
                               region='lon1',  # London
                               image=MEILI_IMG.id,
                               size_slug=conf.SIZE_SLUG,
                               tags=['meisearch-digitalocean-ci'],
                               backups=conf.ENABLE_BACKUPS)
droplet.create()

print('Creating droplet...')

# Wait for Droplet to be created

wait_for_droplet_creation(droplet)
droplet = droplet.load()
print('   Droplet created. IP: {}, ID: {}'.format(
    droplet.ip_address, droplet.id))

# Wait for Health check after configuration is finished

print('Waiting for Health check (may take a few minutes)')
HEALTH = wait_for_health_check(droplet, timeout_seconds=600)
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
    destroy_droplet_and_exit(droplet)
print('   Version of meilisearch match!')

# Power down Droplet

print('Powering down droplet...')
shutdown = droplet.shutdown(return_dict=True)
wait_for_droplet_shutdown(droplet)
print('   Droplet is OFF')

# Destroy Droplet

print('Destroying Droplet...')
droplet.destroy()
print('   Droplet destroyed')
