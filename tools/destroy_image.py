import sys
import digitalocean

import config as conf

if len(sys.argv) > 1:
    SNAPSHOT_NAME = sys.argv[1]
else:
    raise Exception('No snapshot name specified')

print(f'Destroying image named: {SNAPSHOT_NAME}...')

manager = digitalocean.Manager(token=conf.DIGITALOCEAN_ACCESS_TOKEN)
images = manager.get_images()

MEILI_IMG = None
for img in images:
    if img.name == SNAPSHOT_NAME:
        MEILI_IMG = img
        print(f'Found image: {img.name} created at {img.created_at}')
        break

if MEILI_IMG is None:
    raise Exception(f'Couldn\'t find the specified image: {SNAPSHOT_NAME}')

# Destroy Snapshot

print('Destroying Snapshot...')
MEILI_IMG.destroy()
print('   Snapshot destroyed')
