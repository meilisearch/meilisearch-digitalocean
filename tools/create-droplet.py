import digitalocean
import os
import requests

# Script settings

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"

# Starting snapshot for Droplet

MEILI_VERSION="" # 0.10.0
MEILI_IMG_SLUG="TestSam" # MeiliSearch

# Droplet settings

DROPLET_NAME="TestSam-AUTO"
DROPLET_TAGS=["SAM", "TEST"]
SSH_KEYS_FINGERPRINTS=[
    "d4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc"
]
ENABLE_BACKUPS=False

# Meili stating config

USE_API_KEY="true" # String ["true" / "false"]
MEILISEARCH_API_KEY="123456" # String [Any]
USE_SSL="true" # String ["true" / "false"]
DOMAIN_NAME="sam.meilisearch.com" # String [Any]


manager = digitalocean.Manager(token=DIGITALOCEAN_ACCESS_TOKEN)
images = manager.get_images()
meili_img=None

for img in images:
    if MEILI_IMG_SLUG.lower() in img.name.lower() and MEILI_VERSION.lower() in img.name.lower():
        meili_img = img
        break

if meili_img is None:
    raise Exception("Couldn't find the specified image: {} {}".format(MEILI_IMG_SLUG, MEILI_VERSION))

print("{name}: {id}. Regions: {reg}. Tags: {tags}. Size: {size}".format(
                name=meili_img.name,
                id=meili_img.id,
                reg=meili_img.regions,
                tags=meili_img.tags,
                size=meili_img.size_gigabytes,
            ))

# Set initial MeiliSearch config
USER_DATA="""export USE_API_KEY={USE_API_KEY}
export MEILISEARCH_API_KEY={MEILISEARCH_API_KEY}
export USE_SSL={USE_SSL}
export DOMAIN_NAME={DOMAIN_NAME}
""".format(USE_API_KEY=USE_API_KEY,MEILISEARCH_API_KEY=MEILISEARCH_API_KEY,USE_SSL=USE_SSL,DOMAIN_NAME=DOMAIN_NAME)

droplet = digitalocean.Droplet(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"),
                               name=DROPLET_NAME,
                               region='lon1', # London
                               image=meili_img.id, # Meilis Snapshot
                               size_slug='2gb',
                               tags=DROPLET_TAGS,
                               ssh_keys=SSH_KEYS_FINGERPRINTS,
                               user_data=USER_DATA,
                               backups=ENABLE_BACKUPS)
droplet.create()