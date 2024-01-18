import os
import json
import psutil
import socket
import datetime

MONIT_DIR = '/var/monit/'
REPORT_FILE_PREFIX = 'report_'
CONFIG_FILE = 'config.json'


def create_monit_dir():
    if not os.path.exists(MONIT_DIR):
        os.makedirs(MONIT_DIR)


def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_unique_id():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")


def check_resources():
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    cpu_usage = psutil.cpu_percent()
    open_ports = check_open_ports()

    report_data = {
        'time': get_current_time(),
        'id': get_unique_id(),
        'RAM_usage': ram_usage,
        'disk_usage': disk_usage,
        'CPU_usage': cpu_usage,
        'open_ports': open_ports
    }

    report_file_path = os.path.join(MONIT_DIR, f"{REPORT_FILE_PREFIX}{report_data['id']}.json")

    with open(report_file_path, 'w') as report_file:
        json.dump(report_data, report_file, indent=2)

    print(f"Check completed and report saved to: {report_file_path}")


def check_open_ports():
    with open(CONFIG_FILE) as config_file:
        config = json.load(config_file)
        ports_to_check = config.get('ports_to_check', [])

    open_ports = []
    for port in ports_to_check:
        try:
            sock = socket.create_connection(('127.0.0.1', port), timeout=1)
            sock.close()
            open_ports.append(port)
        except (socket.timeout, ConnectionRefusedError):
            pass

    return open_ports


def list_reports():
    reports = [f for f in os.listdir(MONIT_DIR) if f.startswith(REPORT_FILE_PREFIX) and f.endswith('.json')]
    print("List of available reports:")
    for report in reports:
        print(report)


def get_last_report():
    reports = [f for f in os.listdir(MONIT_DIR) if f.startswith(REPORT_FILE_PREFIX) and f.endswith('.json')]
    if reports:
        latest_report = max(reports, key=lambda x: os.path.getctime(os.path.join(MONIT_DIR, x)))
        print(f"Last report: {latest_report}")
        with open(os.path.join(MONIT_DIR, latest_report)) as report_file:
            print(json.dumps(json.load(report_file), indent=2))
    else:
        print("No reports available.")


def get_avg_last_x_hours(x):
    reports = [f for f in os.listdir(MONIT_DIR) if f.startswith(REPORT_FILE_PREFIX) and f.endswith('.json')]
    if reports:
        recent_reports = sorted(reports, key=lambda x: os.path.getctime(os.path.join(MONIT_DIR, x)), reverse=True)[:x]
        avg_data = {}
        for report_file in recent_reports:
            with open(os.path.join(MONIT_DIR, report_file)) as report:
                data = json.load(report)
                for key, value in data.items():
                    if key not in avg_data:
                        avg_data[key] = value
                    elif isinstance(value, (int, float)):
                        avg_data[key] = (avg_data[key] + value) / 2

        print(f"Average data for the last {x} hours:")
        print(json.dumps(avg_data, indent=2))
    else:
        print("No reports available.")


if __name__ == "__main__":
    create_monit_dir()

    import argparse

    parser = argparse.ArgumentParser(description="Monitor system resources and generate JSON reports.")
    parser.add_argument("command", choices=['check', 'list', 'get'], help="Command to execute")
    parser.add_argument("--avg", type=int, help="Number of hours for 'get avg X' command")

    args = parser.parse_args()

    if args.command == 'check':
        check_resources()
    elif args.command == 'list':
        list_reports()
    elif args.command == 'get':
        if args.avg:
            get_avg_last_x_hours(args.avg)
        else:
            get_last_report()
