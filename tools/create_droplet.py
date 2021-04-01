import random
import hashlib
import os
import time
import datetime
import CloudFlare
import requests
import digitalocean
from utils import wait_for_droplet_creation, wait_for_ssh_availability


 # -----------------------------------------
# MeiliSearch DigitalOcean Droplet Config
# -----------------------------------------

# Script settings

DIGITALOCEAN_ACCESS_TOKEN = os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_EMAIL = os.getenv("CLOUDFLARE_EMAIL")

# Droplet settings

# https://developers.digitalocean.com/documentation/changelog/api-v2/new-size-slugs-for-droplet-plan-changes/
DROPLET_TAGS = ["SAAS", "AUTOBUILD"]
SSH_KEYS_FINGERPRINTS = [
    "d4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc",
    "0b:9b:00:21:60:17:6f:e4:d6:f3:d0:8a:e0:cc:a6:97",
]
ENABLE_BACKUPS = False

MEILI_VERSION = "v0.10.0"  # v0.10.0
MEILI_IMG_SLUG = "meilisearch"  # MeiliSearch

USE_API_KEY = "true"  # String ["true" / "false"]
USE_SSL = "true"  # String ["true" / "false"]
USE_CERTBOT = "true"  # String ["true" / "false"]

def trigger_create_droplet(subdomain_name, size_slug, callback_url, meilisearch_api_key, domain, logger):
    try:
        response = create_droplet(
            subdomain_name, size_slug, meilisearch_api_key, domain, logger)
    except Exception as err:
        requests.post(
            callback_url,
            json={
                'status': 'fail',
                'message': str(err),
                'domain_name': subdomain_name,
                'api_key': None
            },
        )
        logger.error("{0: <15} | ERROR CREATING DROPLET: {error}".format(
            subdomain_name, error=err))
    else:
        requests.post(
            callback_url,
            json={
                'status': 'ok',
                'message': 'Droplet created successfuly',
                'domain_name': "https://{url}".format(url=response['domain_name']),
                'api_key': response['api_key']
            },
        )
        logger.info("{0: <15} | DROPLET CREATED".format(subdomain_name))


def create_droplet(subdomain_name, size_slug, meilisearch_api_key, domain, logger):

    cloudflare_zone = domain
    logger.info(
        "{0: <15} | TRIGGERED DROPLET CREATION: {0}".format(subdomain_name)
    )
    if meilisearch_api_key == "":
        seed = datetime.datetime.now().microsecond + random.randint(100000, 1000000)
        key = hashlib.md5()
        key.update(str(seed).encode('utf-8'))
        meilisearch_api_key = key.hexdigest()

    domain_name = "{}.{}".format(subdomain_name, cloudflare_zone)

    # -------------------------------------------
    # MeiliSearch DigitalOcean Droplet Creation
    # -------------------------------------------

    manager = digitalocean.Manager(token=DIGITALOCEAN_ACCESS_TOKEN)
    images = manager.get_images()
    meili_img = None

    for img in images:
        if MEILI_IMG_SLUG.lower() in img.name.lower() and MEILI_VERSION.lower() in img.name.lower():
            meili_img = img
            logger.info("{0: <15} | Found image: {name} created at {created_at}".format(
                subdomain_name,
                name=img.name,
                created_at=img.created_at
            ))
            break

    if meili_img is None:
        raise Exception("Couldn't find the specified image: {} {}".format(
            MEILI_IMG_SLUG, MEILI_VERSION))

    logger.info("{0: <15} | id: {id}. Regions: {reg}. Tags: {tags}. Size: {size}".format(
        subdomain_name,
        id=meili_img.id,
        reg=meili_img.regions,
        tags=meili_img.tags,
        size=size_slug,
    ))

    # Set initial MeiliSearch config

    user_data = """
    export MEILI_SKIP_USER_INPUT=true
    export USE_CERTBOT={0}
    export USE_API_KEY={1}
    export MEILISEARCH_API_KEY={2}
    export USE_SSL={3}
    export DOMAIN_NAME={4}
    """.format(USE_CERTBOT, USE_API_KEY, meilisearch_api_key, USE_SSL, domain_name)

    droplet = digitalocean.Droplet(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"),
                                   name=subdomain_name,
                                   region='lon1',  # London
                                   image=meili_img.id,  # Meilis Snapshot
                                   size_slug=size_slug,
                                   tags=DROPLET_TAGS,
                                   ssh_keys=SSH_KEYS_FINGERPRINTS,
                                   user_data=user_data,
                                   backups=ENABLE_BACKUPS)
    droplet.create()

    logger.info("{0: <15} | Creating droplet...".format(subdomain_name))

    # Wait for Droplet to be created

    wait_for_droplet_creation(droplet)
    logger.info("{0: <15} | Droplet created".format(subdomain_name))

    # CREATE A RECORD CLOUDFLARE

    cloudflare = CloudFlare.CloudFlare(
        email=CLOUDFLARE_EMAIL,
        token=CLOUDFLARE_API_KEY,
        # debug=True,
    )
    try:
        zones = cloudflare.zones.get(params={'name': cloudflare_zone})
        zone_id = zones[0]['id']
        logger.info("{0: <15} | CLOUDFLARE: Found zone for {zone}. Id: {zone_id}".format(
            subdomain_name,
            zone=cloudflare_zone,
            zone_id=zone_id,
        ))
    except CloudFlare.exceptions.CloudFlareAPIError as err:
        droplet.destroy()
        raise Exception('/zones.get - %s - api call failed' % (err)) from err
    except Exception as err:
        droplet.destroy()
        raise Exception('/zones.get - %s - api call failed' % (err)) from err
    if len(zones) == 0:
        droplet.destroy()
        raise Exception('No zones found')

    dns_record = {
        'name': domain_name,
        'type': 'A',
        'content': droplet.ip_address,
        'proxied': False,
        'ttl': 1,
        'zone_id': cloudflare_zone
    }

    logger.info(
        "{0: <15} | Creating CloudFlare A Record with params:".format(subdomain_name))
    logger.info("{0: <15} | {dns}".format(
        subdomain_name,
        dns=str(dns_record),
    ))

    # Wait for port 22 (SSH) to be available

    wait_for_ssh_availability(droplet)
    logger.info("{0: <15} | SSH Port is available".format(subdomain_name))

    # Execute deploy script via SSH

    time.sleep(10)

    ssh_command = "ssh {user}@{host} -o StrictHostKeyChecking=no 'sh /var/opt/meilisearch/scripts/first-login/001-setup-prod.sh'".format(
        user='root',
        host=domain_name
    )
    logger.info("{0: <15} | {command}".format(
        subdomain_name,
        command=ssh_command,
    ))
    os.system(ssh_command)

    response = {
        'api_key': meilisearch_api_key,
        'domain_name': domain_name,
    }
    return response