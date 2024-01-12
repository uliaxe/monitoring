import os
import datetime
import psutil
import json
import socket

MONIT_DIR = '/var/monit'

def create_monit_dir():
    if not os.path.exists(MONIT_DIR):
        os.makedirs(MONIT_DIR)


def get_unique_id():
    return str(datetime.datetime.utcnow().timestamp())

def get_timestamp():
    return str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))

def check_resources():
    data = {
        'timestamp': get_timestamp(),
        'id': get_unique_id(),
        'ram_usage': psutil.virtual_memory().percent,
        'disk_usahge': psutil.disk_usage('/').percent,
        'cpu_usage': psutil.cpu_percent(),
        'open_ports' : check_open_ports()
    }
    return data

def check_open_ports():
    with open ('config.json') as f:
        config = json.load(f)
        ports_to_check = config.get('ports', [])

    open_ports = []
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('10.0.64.12', port))
        if result == 0:
            open_ports.append(port)
        sock.close()

    return open_ports

def save_report(data):
    create_monit_dir()
    filename = f"{MONIT_DIR}monit-report_{data['id']}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    return filename
    
if __name__ == '__main__':
    report_data = check_resources()
    save_path = save_report(report_data)
    print(f"Check completed. Report saved to {save_path}")
