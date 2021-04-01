import time
import sys
import digitalocean
from utils import wait_for_droplet_creation, wait_for_health_check, \
    wait_for_droplet_shutdown, wait_for_snapshot_creation, \
    destroy_droplet_and_exit, check_meilisearch_version, STATUS_OK
import config as conf

# Create droplet

print('Creating droplet...')

droplet = digitalocean.Droplet(token=conf.DIGITALOCEAN_ACCESS_TOKEN,
                               name=conf.DROPLET_NAME,
                               region='lon1',  # London
                               image='debian-10-x64',  # Debian 10.3
                               size_slug=conf.SIZE_SLUG,
                               tags=['marketplace'],
                               backups=conf.ENABLE_BACKUPS,
                               user_data=conf.USER_DATA)
droplet.create()

# Wait for Droplet to be created

try:
    wait_for_droplet_creation(droplet)
    droplet = droplet.load()
except Exception as err:
    print("   Exception: {}".format(err))
    destroy_droplet_and_exit(droplet)

print('   Droplet created. IP: {}, ID: {}'.format(
    droplet.ip_address, droplet.id))

# Wait for Health check after configuration is finished

print('Waiting for Health check (may take a few minutes: config and reboot)')
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
    print("   Exception: {}".format(err))
    destroy_droplet_and_exit(droplet)

print('   Version of meilisearch match!')

# Power down Droplet

print('Powering down droplet...')
try:
    shutdown = droplet.shutdown(return_dict=True)
    wait_for_droplet_shutdown(droplet)
except Exception as err:
    print("   Exception: {}".format(err))
    destroy_droplet_and_exit(droplet)

print('   Droplet is OFF')

# Create snapshot from Droplet

if len(sys.argv) > 1:
    SNAPSHOT_NAME = sys.argv[1]
else:
    SNAPSHOT_NAME = conf.SNAPSHOT_NAME

print('Creating a snapshot: {}'.format(SNAPSHOT_NAME))

try:
    take_snapshot = droplet.take_snapshot(
        SNAPSHOT_NAME, return_dict=False, power_off=True)
    wait_for_snapshot_creation(droplet)
except Exception as err:
    print("  Exception: {}".format(err))
    destroy_droplet_and_exit(droplet)

print('   Snapshot created: {}'.format(SNAPSHOT_NAME))

# Destroy Droplet

print('Destroying Droplet...')
droplet.destroy()
print('   Droplet destroyed')
