import os
import time
import digitalocean
from utils import wait_for_droplet_creation, wait_for_ssh_availability, \
    wait_for_health_check, wait_for_droplet_shutdown, wait_for_snapshot_creation

import config as conf
# Create droplet

droplet = digitalocean.Droplet(token=conf.DIGITALOCEAN_ACCESS_TOKEN,
                               name=conf.DROPLET_NAME,
                               region='lon1',  # London
                               image='debian-10-x64',  # Debian 10.3
                               size_slug=conf.SIZE_SLUG,
                               tags=['marketplace'],
                               ssh_keys=conf.SSH_KEYS_FINGERPRINTS,
                               backups=conf.ENABLE_BACKUPS,
                               user_data=conf.USER_DATA)
droplet.create()

print('Creating droplet...')

# Wait for Droplet to be created

wait_for_droplet_creation(droplet)
droplet = droplet.load()
print('   Droplet created. IP: {}, ID: {}'.format(
    droplet.ip_address, droplet.id))

# Wait for port 22 (SSH) to be available

print('Waiting for SSH availability...')
wait_for_ssh_availability(droplet)
print('   SSH Port is available')

# Wait for Health check after configuration is finished

print('Waiting for Health check (may take a few minutes: config and reboot)')
wait_for_health_check(droplet)
print('   Instance is healthy')

# Execute deploy script via SSH

commands = [
    'rm -rf /var/log/*.log',
    'curl https://raw.githubusercontent.com/meilisearch/cloud-scripts/{0}/scripts/deploy-meilisearch.sh | bash -s {0}'.format(
        conf.MEILI_CLOUD_SCRIPTS_VERSION_TAG),
    'curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/img_check.sh | bash',
    'curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/cleanup.sh | bash',
]

for cmd in commands:
    SSH_COMMAND = 'ssh {user}@{host} -o StrictHostKeyChecking=no "{cmd}"'.format(
        user='root',
        host=droplet.ip_address,
        cmd=cmd,
    )
    print('EXECUTE COMMAND:', SSH_COMMAND)
    os.system(SSH_COMMAND)
    time.sleep(5)

# Power down Droplet

print('Powering down droplet...')
shutdown = droplet.shutdown(return_dict=True)
wait_for_droplet_shutdown(droplet)
print('   Droplet is OFF')


# Create snapshot from Droplet

print('Creating a snapshot: {}'.format(conf.SNAPSHOT_NAME))
take_snapshot = droplet.take_snapshot(
    conf.SNAPSHOT_NAME, return_dict=True, power_off=False)
wait_for_snapshot_creation(droplet)
print('   Snapshot created: {}'.format(conf.SNAPSHOT_NAME))

# Desroy Droplet

print('Destroying Droplet...')
droplet.destroy()
print('   Droplet destroyed')
