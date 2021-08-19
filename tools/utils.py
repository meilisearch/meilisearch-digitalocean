import datetime
import sys
import time
import socket
import requests

STATUS_OK = 0
STATUS_TIMEOUT = 1


def wait_for_droplet_creation(droplet):
    try:
        actions = droplet.get_actions()
        while True:
            for act in actions:
                if act.type == 'create':
                    act.load()
                    print('   Action {} is {}'.format(
                        act.type, act.status))
                    if act.status == 'completed':
                        return
            time.sleep(4)
    except Exception as err:
        print('   Exception: {}'.format(err))
        raise


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
    try:
        actions = droplet.get_actions()
        while True:
            for act in actions:
                if act.type == 'shutdown':
                    act.load()
                    print('   Action {} is {}'.format(
                        act.type, act.status))
                    if act.status == 'completed':
                        return
                    if act.status == 'errored':
                        power_off_droplet(droplet)
                        return
            time.sleep(4)
    except Exception as err:
        print('   Exception: {}'.format(err))
        raise

def wait_for_droplet_power_off(droplet):
    try:
        actions = droplet.get_actions()
        while True:
            for act in actions:
                if act.type == 'power_off':
                    act.load()
                    print('   Action {} is {}'.format(
                        act.type, act.status))
                    if act.status == 'completed':
                        return
                    if act.status == 'errored':
                        destroy_droplet_and_exit(droplet)
            time.sleep(4)
    except Exception as err:
        print('   Exception: {}'.format(err))
        raise

def power_off_droplet(droplet):
    print('Powering down droplet with power_off...')
    try:
        droplet.power_off(return_dict=True)
        wait_for_droplet_power_off(droplet)
    except Exception as err:
        print('   Exception: {}'.format(err))
        raise

def wait_for_snapshot_creation(droplet):
    try:
        actions = droplet.get_actions()
        while True:
            for act in actions:
                if act.type == 'snapshot':
                    act.load()
                    print('   Action {} is {}'.format(
                        act.type, act.status))
                    if act.status == 'completed':
                        return
            time.sleep(4)
    except Exception as err:
        print('   Exception: {}'.format(err))
        time.sleep(300)
        raise


def check_meilisearch_version(droplet, version):
    resp = requests.get(
        'http://{}/version'.format(droplet.ip_address), verify=False, timeout=10).json()
    if resp['pkgVersion'] in version:
        return
    raise Exception(
        '    The version of meilisearch ({}) does not match the droplet ({})'.format(version, resp['pkgVersion']))


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
