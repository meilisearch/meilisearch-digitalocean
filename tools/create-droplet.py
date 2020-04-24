import digitalocean
from paramiko import SSHClient, AutoAddPolicy
import os
import time
import socket
import CloudFlare
import json

# Script settings

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"

CLOUDFLARE_API_KEY=os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_EMAIL=os.getenv("CLOUDFLARE_EMAIL")
CLOUDFLARE_ZONE='getmeili.com'

# Starting snapshot for Droplet

MEILI_VERSION="v0.10.0" # v0.10.0
MEILI_IMG_SLUG="meilisearch" # MeiliSearch

# Droplet settings

SIZE_SLUG="s-1vcpu-1gb" # https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
DROPLET_NAME="TestSam-AUTO"
DROPLET_TAGS=["SAAS", "AUTOBUILD"]
SSH_KEYS_FINGERPRINTS=[
    "d4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc"
]
ENABLE_BACKUPS=False

# Meili stating config

USE_API_KEY="true" # String ["true" / "false"]
MEILISEARCH_API_KEY="123456" # String [Any]
USE_SSL="true" # String ["true" / "false"]
USE_CERTBOT="true" # String ["true" / "false"]
DOMAIN_NAME="klklkl.getmeili.com" # String [Any]

manager = digitalocean.Manager(token=DIGITALOCEAN_ACCESS_TOKEN)
images = manager.get_images()
meili_img=None

for img in images:
    if MEILI_IMG_SLUG.lower() in img.name.lower() and MEILI_VERSION.lower() in img.name.lower():
        meili_img = img
        print("Found image: {} created at {}".format(img.name, img.created_at))
        break

if meili_img is None:
    raise Exception("Couldn't find the specified image: {} {}".format(MEILI_IMG_SLUG, MEILI_VERSION))

print("{name}: {id}. Regions: {reg}. Tags: {tags}. Size: {size}".format(
                name=meili_img.name,
                id=meili_img.id,
                reg=meili_img.regions,
                tags=meili_img.tags,
                size=SIZE_SLUG,
            ))

# Set initial MeiliSearch config

USER_DATA="""
export MEILI_SKIP_USER_INPUT=true
export USE_CERTBOT=true
export USE_API_KEY={USE_API_KEY}
export MEILISEARCH_API_KEY={MEILISEARCH_API_KEY}
export USE_SSL={USE_SSL}
export DOMAIN_NAME={DOMAIN_NAME}
""".format(USE_API_KEY=USE_API_KEY,MEILISEARCH_API_KEY=MEILISEARCH_API_KEY,USE_SSL=USE_SSL,DOMAIN_NAME=DOMAIN_NAME)

droplet = digitalocean.Droplet(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"),
                               name=DROPLET_NAME,
                               region='lon1', # London
                               image=meili_img.id, # Meilis Snapshot
                               size_slug='1gb',
                               tags=DROPLET_TAGS,
                               ssh_keys=SSH_KEYS_FINGERPRINTS,
                               user_data=USER_DATA,
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

# CREATE A RECORD CLOUDFLARE

cf = CloudFlare.CloudFlare(
        email=CLOUDFLARE_EMAIL,
        token=CLOUDFLARE_API_KEY,
        # debug=True,
    )
try:
    zones = cf.zones.get(params={'name':CLOUDFLARE_ZONE})
    zone_id = zones[0]['id']
    print("CLOUDFLARE: Found zone for {}. Id: {}".format(CLOUDFLARE_ZONE, zone_id))
except CloudFlare.exceptions.CloudFlareAPIError as e:
    exit('/zones.get %d %s - api call failed' % (e, e))
except Exception as e:
    exit('/zones.get - %s - api call failed' % (e))
if len(zones) == 0:
        exit('No zones found')

dns_record = {
            'name':DOMAIN_NAME,
            'type':'A',
            'content':droplet.ip_address,
            'proxied':False,
            'ttl':1,
            'zone_id': CLOUDFLARE_ZONE
        }

print("Creating CloudFlare A Record with params:")
print(str(dns_record))

zone_info = cf.zones.dns_records.post(zones[0]['id'], data=dns_record)

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
    "sh /var/opt/meilisearch/scripts/first-login/001-setup-prod.sh",
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