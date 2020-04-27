import digitalocean
from paramiko import SSHClient, AutoAddPolicy
from tools.do_meili_tools import wait_for_droplet_creation, wait_for_ssh_availability
import os
import time
import socket
import CloudFlare
import json

def trigger_droplet_creation(subdomain_name, size_slug):
    print("Triggered droplet creation: {}".format(subdomain_name))
    create_droplet(subdomain_name, size_slug)
    print("DRPLOET CREATED: {}".format(subdomain_name))

def create_droplet(subdomain_name, size_slug):

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

    SIZE_SLUG=size_slug # https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
    DROPLET_NAME=subdomain_name
    DROPLET_TAGS=["SAAS", "AUTOBUILD"]
    SSH_KEYS_FINGERPRINTS=[
        "d4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc"
    ]
    ENABLE_BACKUPS=False

    # Meili starting config

    USE_API_KEY="true" # String ["true" / "false"]
    MEILISEARCH_API_KEY="123456" # String [Any]
    USE_SSL="true" # String ["true" / "false"]
    USE_CERTBOT="true" # String ["true" / "false"]
    DOMAIN_NAME="{}.{}".format(subdomain_name, CLOUDFLARE_ZONE) # String [Any]

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

    wait_for_droplet_creation(droplet)
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
        droplet.destroy()
    except Exception as e:
        exit('/zones.get - %s - api call failed' % (e))
        droplet.destroy()
    if len(zones) == 0:
        exit('No zones found')
        droplet.destroy()

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

    wait_for_ssh_availability(droplet)
    print("SSH Port is available")

    # Execute deploy script via SSH

    time.sleep(10)

    ssh_command = "ssh {user}@{host} -o StrictHostKeyChecking=no 'sh /var/opt/meilisearch/scripts/first-login/001-setup-prod.sh'".format(
            user='root',
            host=DOMAIN_NAME
        )
    print(ssh_command)
    os.system(ssh_command)

    # Make a callback to tell everything went ok and share KEY and URL

    response = "{'api_key':'{}','domain_name':'{}'}".format(MEILISEARCH_API_KEY, DOMAIN_NAME)
    return response

if __name__ == "__main__":
    subdomain_name="auto-img"
    size_slug="s-1vcpu-1gb"
    create_droplet(subdomain_name, size_slug)