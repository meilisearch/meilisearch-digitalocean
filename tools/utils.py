import time
import socket
import requests


def wait_for_droplet_creation(droplet):
    while True:
        actions = droplet.get_actions()
        if actions[0].type == "create" and actions[0].status == "completed":
            break
        time.sleep(2)


def wait_for_ssh_availability(droplet):
    while True:
        time.sleep(2)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((droplet.ip_address, 22))
            sock.shutdown(2)
            sock.close()
            return
        except Exception:
            continue


def wait_for_health_check(droplet):
    while True:
        time.sleep(2)
        try:
            resp = requests.get("http://{}/health".format(droplet.ip_address))
            if resp.status_code >= 200 and resp.status_code < 300:
                return
        except Exception:
            continue


def wait_for_droplet_shutdown(droplet):
    while True:
        try:
            actions = droplet.get_actions()
            for act in actions:
                if act.type == "shutdown" and actions[0].status == "completed":
                    return
        except Exception as err:
            print("   Exception: {}".format(err))
            return


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
