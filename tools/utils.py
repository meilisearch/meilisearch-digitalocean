import datetime
import sys
import time
import socket
import requests

STATUS_OK = 0
STATUS_TIMEOUT = 1


def wait_for_droplet_creation(droplet):
    while True:
        actions = droplet.get_actions()
        if actions[0].type == "create" and actions[0].status == "completed":
            break
        time.sleep(2)


def wait_for_ssh_availability(droplet):
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((droplet.ip_address, 22))
            sock.shutdown(2)
            sock.close()
            return
        except Exception:
            continue
        time.sleep(2)


def wait_for_health_check(droplet, timeout_seconds=None):
    start_time = datetime.datetime.now()
    while timeout_seconds is None \
            or check_timeout(start_time, timeout_seconds) is not STATUS_TIMEOUT:
        try:
            resp = requests.get(
                'http://{}/health'.format(droplet.ip_address), verify=False, timeout=10)
            if resp.status_code >= 200 and resp.status_code < 300:
                return STATUS_OK
        except Exception:
            pass
        time.sleep(2)
    return STATUS_TIMEOUT


def wait_for_droplet_shutdown(droplet):
    time.sleep(10)
    while True:
        try:
            actions = droplet.get_actions()
            for act in actions:
                if act.type == "shutdown" and actions[0].status == "completed":
                    return
        except Exception as err:
            print("   Exception: {}".format(err))
            return
        time.sleep(2)


def wait_for_snapshot_creation(droplet):
    while True:
        time.sleep(2)
        actions = droplet.get_actions()
        if actions[0].type == "snapshot" and actions[0].status == "completed":
            return
        try:
            time.sleep(2)
            actions = droplet.get_actions()
            if actions[0].type == "snapshot" and actions[0].status == "completed":
                return
        except Exception as err:
            print("   Exception: {}".format(err))
            time.sleep(300)
            return


def check_meilisearch_version(droplet, version):
    resp = requests.get(
        "http://{}/version".format(droplet.ip_address), verify=False, timeout=10).json()
    if resp["pkgVersion"] in version:
        return
    raise Exception(
        "    The version of meilisearch ({}) does not match the droplet ({})".format(version, resp["pkgVersion"]))


def destroy_droplet_and_exit(droplet):
    print('   Destroying droplet {}'.format(droplet.id))
    droplet.destroy()
    print('ENDING PROCESS WITH EXIT CODE 1')
    sys.exit(1)

# GENERAL


def check_timeout(start_time, timeout_seconds):
    elapsed_time = datetime.datetime.now() - start_time
    if elapsed_time.total_seconds() > timeout_seconds:
        return STATUS_TIMEOUT
    return STATUS_OK
