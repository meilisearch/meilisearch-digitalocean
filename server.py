from tools.create_droplet import trigger_droplet_creation
from datetime import datetime
from flask import Flask, request, Response
from multiprocessing import Process

import jsonify
import digitalocean
import os
app = Flask(__name__)

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"

MEILI_SAAS_KEY=os.getenv("MEILI_SAAS_KEY")

if MEILI_SAAS_KEY is None or DIGITALOCEAN_ACCESS_TOKEN is None:
    raise Exception("Please define the following environment variables: DIGITALOCEAN_ACCESS_TOKEN, MEILI_SAAS_KEY")

@app.route('/create', methods=['POST'])
def create_meilisearch():

    # date = datetime.now()
    # date_str = date.strftime("%d%m%Y%H%M%S%f")
    # subdomain_name="droplet{}".format(date_str)
    error = None

    try:
        if request.method == 'POST':
            domain_name = request.json['domain_name']
            size_slug = request.json['size_slug']
            manager = digitalocean.Manager(token=DIGITALOCEAN_ACCESS_TOKEN)
            droplets = manager.get_all_droplets(tag_name="SAAS")
            for drop in droplets:
                if drop.name == domain_name:
                    return "ERROR: {}".format("Droplet exists already"), 400
            creation_proc = Process(
                target=trigger_droplet_creation,
                daemon=True,
                args=(domain_name, size_slug,)
            )
            creation_proc.start()
            # trigger_droplet_creation(domain_name, size_slug)
            return Response("Droplet is being created", status=201, mimetype='application/json')
    except Exception as e:       
        return "ERROR: {}".format(e), 400

if __name__=='__main__':
    app.run(threaded=True, port=80)