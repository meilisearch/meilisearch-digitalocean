import digitalocean
import os
import requests

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"
MEILI_VERSION="" # 0.10.0
MEILI_IMG_SLUG="TestSam" # MeiliSearch

DROPLET_NAME="TestSam-AUTO"
DROPLET_TAGS=["SAM", "TEST"]
SSH_KEYS_FINGERPRINTS=[
    "d4:b1:a5:ce:10:01:27:14:44:aa:a9:8e:41:bd:39:bc"
]
USER_DATA="This is some data dynamically entered"
ENABLE_BACKUPS=False


manager = digitalocean.Manager(token=DIGITALOCEAN_ACCESS_TOKEN)
images = manager.get_images()
meili_img=None

for img in images:
    if MEILI_IMG_SLUG.lower() in img.name.lower() and MEILI_VERSION.lower() in img.name.lower():
        meili_img = img
        break

print("{name}: {id}. Regions: {reg}. Tags: {tags}. Size: {size}".format(
                name=meili_img.name,
                id=meili_img.id,
                reg=meili_img.regions,
                tags=meili_img.tags,
                size=meili_img.size_gigabytes,
            ))

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