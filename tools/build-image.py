import digitalocean
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient, SCPException
import os
import time
import socket

# Script settings

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"
MEILI_VERSION_TAG="v0.10.0"
SNAPSHOT_NAME="MeiliSearch-{}-Debian-10.3".format(MEILI_VERSION_TAG)

# Droplet settings

DROPLET_NAME="{}-BUILD".format(SNAPSHOT_NAME)
DROPLET_TAGS=["SAM", "TEST"]
SSH_KEYS_FINGERPRINTS=[
    "d4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc"
]
ENABLE_BACKUPS=False

# Create droplet

droplet = digitalocean.Droplet(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"),
                               name=DROPLET_NAME,
                               region='lon1', # London
                               image="debian-10-x64", # Debian 10.3
                               size_slug='1gb',
                               tags=["marketplace"],
                               ssh_keys=SSH_KEYS_FINGERPRINTS,
                               backups=ENABLE_BACKUPS)
droplet.create()

print("Creating droplet...")

# Wait for Droplet to be created

while True:
    d = droplet.get_actions()
    if d[0].type == "create" and d[0].status == "completed":
        droplet = droplet.load()
        print("IP:", droplet.ip_address, "id:", droplet.id)
        break
    time.sleep(1)

print("Droplet created")

# Wait for port 22 (SSH) to be available

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((droplet.ip_address, 22))
        s.shutdown(2)
        s.close()
        break
    except:
        continue
    time.sleep(1)

print("SSH Port is available")

# Execute deploy script via SSH

commands = [
    "apt update",
    "apt install curl -y",
    "curl https://raw.githubusercontent.com/meilisearch/meilisearch-digital-ocean/{}/scripts/deploy.sh | sh".format(MEILI_VERSION_TAG),
    # "rm -rf /var/log/*.log",
    # "history -c",
]

try:
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    
except Exception as e:
    print("ERROR:", e)

try:
    client.connect(
        droplet.ip_address,
        username='root',
        look_for_keys=True,
    )
    while len(commands) > 0:
        cmd = commands[0]
        print("EXECUTE COMMAND:", cmd)
        stdin, stdout, stderr = client.exec_command(cmd)
        status = stdout.channel.recv_exit_status()
        if int(status) == 0:
            commands.pop(0)
        print("Process return status", status)
        response = stdout.readlines()
        for line in response:
            print("\t\t", line)
        time.sleep(5)
except Exception as e:
    print("ERROR:", e)

# Power down droplet

droplet.take_snapshot(SNAPSHOT_NAME, return_dict=True, power_off=False)

while True:
    d = droplet.get_actions()
    if d[0].type == "snapshot" and d[0].status == "completed":
        print("Snapshot created")
        break

print("Destroying droplet")
droplet.destroy()
print("Droplet destroyed")
