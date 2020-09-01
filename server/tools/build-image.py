import digitalocean
from paramiko import SSHClient, AutoAddPolicy
from do_meili_tools import wait_for_droplet_creation, wait_for_ssh_availability
import os
import time
import socket

# Script settings

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"
MEILI_VERSION_TAG="v0.14.0"
SNAPSHOT_NAME="MeiliSearch-{}-Debian-10.3".format(MEILI_VERSION_TAG)
SIZE_SLUG="s-1vcpu-1gb" # https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/

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
                               backups=ENABLE_BACKUPS)
droplet.create()

print("Creating droplet...")

# Wait for Droplet to be created

wait_for_droplet_creation(droplet)
print("Droplet created")

# Wait for port 22 (SSH) to be available

wait_for_ssh_availability(droplet)
print("SSH Port is available")

# Execute deploy script via SSH

commands = [
    "apt update",
    "apt update", # Needed ?
    "apt install curl -y",
    "curl https://raw.githubusercontent.com/meilisearch/meilisearch-digital-ocean/{}/scripts/deploy.sh | sh".format(MEILI_VERSION_TAG),
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


# TODO: Add a check by HTTP request to IP. If fail no build.

# Power down droplet

print("Powering down droplet and creating a snapshot: {}".format(SNAPSHOT_NAME))

droplet.take_snapshot(SNAPSHOT_NAME, return_dict=True, power_off=False)

while True:
    d = droplet.get_actions()
    if d[0].type == "snapshot" and d[0].status == "completed":
        print("Snapshot created: {}".format(SNAPSHOT_NAME))
        break

print("Destroying droplet")
droplet.destroy()
print("Droplet destroyed")
