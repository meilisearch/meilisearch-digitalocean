import time
import socket

def wait_for_droplet_creation(droplet):
    while True:
        d = droplet.get_actions()
        if d[0].type == "create" and d[0].status == "completed":
            droplet = droplet.load()
            print("IP:", droplet.ip_address, "id:", droplet.id)
            break
        time.sleep(2)

def wait_for_ssh_availability(droplet):
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((droplet.ip_address, 22))
            s.shutdown(2)
            s.close()
            break
        except Exception:
            continue
        time.sleep(2)
