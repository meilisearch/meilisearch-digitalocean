import time
import socket
import requests

def wait_for_droplet_creation(droplet):
    while True:
        d = droplet.get_actions()
        if d[0].type == "create" and d[0].status == "completed":
            break
        time.sleep(2)

def wait_for_ssh_availability(droplet):
    while True:
        time.sleep(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((droplet.ip_address, 22))
            s.shutdown(2)
            s.close()
            return
        except Exception:
            continue

def wait_for_health_check(droplet):
    while True:
        time.sleep(2)
        try:
            resp = requests.get("http://{}/health".format(droplet.ip_address))
            if resp.status_code >=200 and resp.status_code < 300:
                return
        except Exception as e:
                continue

def wait_for_droplet_shutdown(droplet):
    while True:
        try:
            d = droplet.get_actions()
            for act in d:
                if act.type == "shutdown" and d[0].status == "completed":
                    return
        except Exception as e:
            print("   Exception: {}".format(e))
            return
