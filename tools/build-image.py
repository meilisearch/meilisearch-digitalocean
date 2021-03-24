import digitalocean
from paramiko import SSHClient, AutoAddPolicy
from do_meili_tools import wait_for_droplet_creation, wait_for_ssh_availability, \
    wait_for_health_check, wait_for_droplet_shutdown, wait_for_snapshot_creation
import os
import time
import requests

# Script settings

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"
MEILI_CLOUD_SCRIPTS_VERSION_TAG="v0.19.0"
SNAPSHOT_NAME="MeiliSearch-{}-Debian-10.3".format(MEILI_CLOUD_SCRIPTS_VERSION_TAG)
SIZE_SLUG="s-1vcpu-1gb" # https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
PROVIDER_NAME='digital_ocean'
USER_DATA =requests.get("https://raw.githubusercontent.com/meilisearch/cloud-scripts/{}/scripts/cloud-config.yaml".format(MEILI_CLOUD_SCRIPTS_VERSION_TAG)).text.replace("unknown_provider", PROVIDER_NAME)

# Droplet settings

DROPLET_NAME="{}-BUILD".format(SNAPSHOT_NAME)
DROPLET_TAGS=["MARKETPLACE", "AUTOBUILD"]
SSH_KEYS_FINGERPRINTS=[
    "d4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc"
]
ENABLE_BACKUPS=False

# Create droplet

droplet = digitalocean.Droplet(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"),
                               name=DROPLET_NAME,
                               region='lon1', # London
                               image="debian-10-x64", # Debian 10.3
                               size_slug=SIZE_SLUG,
                               tags=["marketplace"],
                               ssh_keys=SSH_KEYS_FINGERPRINTS,
                               backups=ENABLE_BACKUPS,
                               user_data=USER_DATA)
droplet.create()

print("Creating droplet...")

# Wait for Droplet to be created

wait_for_droplet_creation(droplet)
droplet = droplet.load()
print("   Droplet created. IP: {}, ID: {}".format(droplet.ip_address, droplet.id))

# Wait for port 22 (SSH) to be available

print("Waiting for SSH availability...")
wait_for_ssh_availability(droplet)
print("   SSH Port is available")

# Wait for Health check after configuration is finished

print("Waiting for Health check (may take a few minutes: config and reboot)")
wait_for_health_check(droplet)
print("   Instance is healthy")

# Execute deploy script via SSH

commands = [
    "rm -rf /var/log/*.log",
    "curl https://raw.githubusercontent.com/meilisearch/cloud-scripts/{0}/scripts/deploy-meilisearch.sh | bash -s {0}".format(MEILI_CLOUD_SCRIPTS_VERSION_TAG),
    "curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/img_check.sh | bash",
    "curl https://raw.githubusercontent.com/digitalocean/marketplace-partners/master/scripts/cleanup.sh | bash",
]

for cmd in commands:
    ssh_command = "ssh {user}@{host} -o StrictHostKeyChecking=no '{cmd}'".format(
        user='root',
        host=droplet.ip_address,
        cmd=cmd,
    )
    print("EXECUTE COMMAND:", ssh_command)
    os.system(ssh_command)
    time.sleep(5)

# Power down Droplet

print("Powering down droplet...")
shutdown = droplet.shutdown(return_dict=True)
wait_for_droplet_shutdown(droplet)
print("   Droplet is OFF")


# Create snapshot from Droplet

print("Creating a snapshot: {}".format(SNAPSHOT_NAME))
take_snapshot = droplet.take_snapshot(SNAPSHOT_NAME, return_dict=True, power_off=False)
wait_for_snapshot_creation(droplet)
print("   Snapshot created: {}".format(SNAPSHOT_NAME))

# Desroy Droplet

print("Destroying Droplet...")
droplet.destroy()
print("   Droplet destroyed")
