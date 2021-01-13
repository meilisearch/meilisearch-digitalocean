import digitalocean
from paramiko import SSHClient, AutoAddPolicy
from do_meili_tools import wait_for_droplet_creation, wait_for_ssh_availability
import os
import time
import requests

# Script settings

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"
MEILI_VERSION_TAG="v0.17.0"
SNAPSHOT_NAME="MeiliSearch-{}-Debian-10.3".format(MEILI_VERSION_TAG)
SIZE_SLUG="s-1vcpu-1gb" # https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
USER_DATA =requests.get("https://raw.githubusercontent.com/meilisearch/meilisearch-cloud/main/scripts/cloud-config.yaml").text

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
print("Droplet created")

# Wait for port 22 (SSH) to be available

wait_for_ssh_availability(droplet)
print("SSH Port is available")

# Execute deploy script via SSH

time.sleep(120)

commands = [
    "rm -rf /var/log/*.log",
    "curl https://raw.githubusercontent.com/meilisearch/meilisearch-cloud/main/scripts/deploy-meilisearch.sh | bash",
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



# Power down droplet

print("Powering down droplet")

shutdown = droplet.shutdown(return_dict=True)

while True:
    d = droplet.get_actions()
    if d[0].type == "shutdown" and d[0].status == "completed":
        print("Droplet is OFF")
        break

print("Creating a snapshot: {}".format(SNAPSHOT_NAME))

take_snapshot = droplet.take_snapshot(SNAPSHOT_NAME, return_dict=True, power_off=False)

while True:
    d = droplet.get_actions()
    if d[0].type == "snapshot" and d[0].status == "completed":
        print("Snapshot created: {}".format(SNAPSHOT_NAME))
        break

print("Destroying droplet")
droplet.destroy()
print("Droplet destroyed")
