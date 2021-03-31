import time
import sys
import digitalocean
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from utils import wait_for_droplet_creation, wait_for_health_check, \
    wait_for_droplet_shutdown, wait_for_snapshot_creation, \
    destroy_droplet_and_exit, check_meilisearch_version, STATUS_OK
import config as conf

# Configure requests on digitalocean
manager = digitalocean.Manager(token=conf.DIGITALOCEAN_ACCESS_TOKEN)
retry = Retry(connect=3)
adapter = HTTPAdapter(max_retries=retry)
manager._session.mount('https://', adapter)

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


# def wait_own(event, dropl, status="completed"):
#     state = 'in-progress'
#     actions = dropl.get_actions()
#     while state != 'completed':
#         for action in actions:
#             time.sleep(2)
#             action.load()
#             if action.id == event['action']['id']:
#                 state = action.status

# Wait for Droplet to be created

try:
    state = 'in-progress'
    actions = droplet.get_actions()
    while state != 'completed':
        for action in actions:
            time.sleep(2)
            if action.type == 'create':
                action.load()
                print("Droplet type {} | Droplet status {}". format(
                    action.type, action.status))
                state = action.status
except Exception as err:
    print("   Exception at action.type == 'create': {}".format(err))
    raise

# wait_for_droplet_creation(droplet)
# droplet = droplet.load()

try:
    while not droplet.ip_address:
        print('droplet has no ip assigned yet')
        time.sleep(2)
        droplet.load()
except Exception as err:
    print("   Exception at droplet.ip_address: {}".format(err))
    raise

print('   Droplet created. IP: {}, ID: {}'.format(
    droplet.ip_address, droplet.id))

# Wait for Health check after configuration is finished
try:
    while not droplet.status == 'active':
        droplet.get_actions()
        droplet.load()
        print('Current status... ' + droplet.status)
        time.sleep(2)
except Exception as err:
    print("   Exception at droplet.status == 'active': {}".format(err))
    raise

print('Waiting for Health check (may take a few minutes: config and reboot)')
try:
    HEALTH = wait_for_health_check(droplet, timeout_seconds=600)
    if HEALTH == STATUS_OK:
        print('   Instance is healthy')
    else:
        print('   Timeout waiting for health check')
        destroy_droplet_and_exit(droplet)
except Exception as err:
    print("   Exception at wait_for_health_check: {}".format(err))
    raise

# Check version

print('Waiting for Version check')
try:
    check_meilisearch_version(
        droplet, conf.MEILI_CLOUD_SCRIPTS_VERSION_TAG)
except Exception as err:
    print("   Exception at check_meilisearch_version: {}".format(err))
    raise
print('   Version of meilisearch match!')

# Power down Droplet
try:
    print('Powering down droplet...')
    shutdown = droplet.shutdown(return_dict=False)
    print('trigger shutdown droplet...')
    shutdown.wait()
except Exception as err:
    print("  Exception  shutdown.wait(): {}".format(err))
    raise
print('   Droplet is OFF')

time.sleep(15)

# Create snapshot from Droplet

if len(sys.argv) > 1:
    SNAPSHOT_NAME = sys.argv[1]
else:
    SNAPSHOT_NAME = conf.SNAPSHOT_NAME
try:
    print('Creating a snapshot: {}'.format(SNAPSHOT_NAME))
    take_snapshot = droplet.take_snapshot(
        SNAPSHOT_NAME, return_dict=False, power_off=True)
    print('trigger take_snapshot...')
    take_snapshot.wait()
except Exception as err:
    print("  Exception at take_snapshot: {}".format(err))
    raise
print('   Snapshot created: {}'.format(SNAPSHOT_NAME))

# Desroy Droplet

print('Destroying Droplet...')
try:
    droplet.destroy()
except Exception as err:
    print("  Exception at destroy: {}".format(err))
    raise
print('   Droplet destroyed')
