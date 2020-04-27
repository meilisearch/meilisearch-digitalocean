from tools.create_droplet import create_droplet
from datetime import datetime
from flask import Flask, request, Response
from multiprocessing import Process

import jsonify
import digitalocean
import os

app = Flask(__name__)
domain = 'meilisearch.dev'

DIGITALOCEAN_ACCESS_TOKEN=os.getenv("DIGITALOCEAN_ACCESS_TOKEN")
DIGITALOCEAN_END_POINT="https://api.digitalocean.com/v2"

MEILI_SAAS_KEY=os.getenv("MEILI_SAAS_KEY")


@app.route('/', methods=['GET', 'POST'])
def home():
    return "OK", 200

@app.route('/create', methods=['POST'])
def create_meilisearch():

    if MEILI_SAAS_KEY is None or DIGITALOCEAN_ACCESS_TOKEN is None:
        raise Exception("Please define the following environment variables: DIGITALOCEAN_ACCESS_TOKEN, MEILI_SAAS_KEY")

    sas_key = request.headers.get('meili-saas-key')
    if sas_key != MEILI_SAAS_KEY:
        return "meili-saas-key header missing", 403
    meilisearch_api_key = ""
    try:
        meilisearch_api_key = request.json['meilisearch_api_key']
    except Exception:
        meilisearch_api_key = ""
    try:     
        subdomain_name = request.json['subdomain_name']
        size_slug = request.json['size_slug']
        if meilisearch_api_key == "":
            app.logger.info("{0: <15} | Meilisearch API KEY will be defined dynmically".format(
                subdomain_name,
            ))
        manager = digitalocean.Manager(token=DIGITALOCEAN_ACCESS_TOKEN)
        droplets = manager.get_all_droplets(tag_name="SAAS")
        for drop in droplets:
            if drop.name == subdomain_name:
                return "ERROR: {}".format("Droplet exists already"), 400
        creation_proc = Process(
            target=create_droplet,
            daemon=True,
            args=(subdomain_name, size_slug, meilisearch_api_key, domain, app.logger)
        )
        creation_proc.start()
        return Response(
            "Droplet {}.{} is being created".format(subdomain_name, domain),
            status=201,
            mimetype='application/json'
        )
    except Exception as e:       
        return "ERROR: {}".format(e), 400

if __name__ == '__main__':
      app.run(host='0.0.0.0')