import datetime
import os
import psutil
import json
import socket
import sys

#chemin dossier stockage rapport 
REPORT_DIR= "var/monit"

def create_report_dir():
    """Create the report directory if it does not exist"""
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def generate_report():
    report = {
        "timestamp": get_timestamp(),
        "id": hash(get_timestamp()),
        "ram_usage": psutil.virtual_memory().percent,
        "cpu_usage":psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage("/").percent,
        "port_status": check_ports()
    }
    return report

def check_ports():
    # Charger les ports depuis le fichier de configuration
    config_filename = 'config.json'

    if not os.path.exists(config_filename):
        print(f"Error: Configuration file '{config_filename}' not found.")
        sys.exit(1)

    try:
        with open(config_filename, 'r') as config_file:
            config = json.load(config_file)
            ports_to_check = config.get('ports_to_check', [])
    except json.JSONDecodeError as e:
        print(f"Error decoding the configuration file '{config_filename}': {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"Error: Missing key '{e}' in the configuration file '{config_filename}'.")
        sys.exit(1)

    # Vérifier l'état de chaque port
    ports_status = {}
    for port in ports_to_check:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('127.0.0.1', port))
        s.close()
        ports_status[port] = result == 0  # 0 indique une connexion réussie

    return ports_status

    

def save_report(report):
    create_report_dir()
    report_filename = REPORT_DIR + f'report_{report["id"]}.json'
    with open(report_filename, 'w') as report_file:
        json.dump(report, report_file, indent=4)

def list_reports():
    reports = [f for f in os.listdir(REPORT_DIR) if f.startswith("report_") and f.endswith(".json")]
    return reports

def get_last_report():
    reports = list_reports()
    if reports:
        last_report_filename = REPORT_DIR + sorted(reports)[-1] 
        with open(last_report_filename, 'r') as last_report_file:
            last_report= json.load(last_report_file)
            return last_report
    else:
        return None
    
def get_avg_report(last_hours):
    reports = list_reports()
    if reports:
        recent_reports = sorted(reports)[-last_hours:]
        avg_report = {
            'timestamp': get_timestamp(),
            'average_values': {}
        }
        for metric in ['ram_usage', 'cpu_usage', 'disk_usage']:
            avg_metric_values = [json.load(open(REPORT_DIR + report))[metric] for report in recent_reports]
            avg_report['average_values'][metric] = sum(avg_metric_values) / len(avg_metric_values)

        return avg_report
    else:
        return None

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: monit.py [check | list | get last |get avg x]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check":
        reports = generate_report()
        save_report(reports)
        print(f"Check executed and report saved : {REPORT_DIR}report_{reports['id']}.json")

    elif command == "list":
        reports = list_reports()
        print("List of reports :")
        for report in reports:
            print(report)

    elif command == "get":
        if len(sys.argv) < 3:
            print("Usage: monit.py get [last | avg]")
            sys.exit(1)

        subcommand = sys.argv[2]

        if subcommand == "last":
            last_report = get_last_report()
            if last_report:
                print("Last report :")
                print(json.dumps(last_report, indent=4))
            else:
                print("No report available")

        elif subcommand == "avg":
            if len(sys.argv) < 4:
                print("Usage: monit.py get avg x")
                sys.exit(1)

            try:
                last_hours = int(sys.argv[3])
                avg_report = get_avg_report(last_hours)
                if avg_report:
                    print(f"Average report for the last {last_hours} hours :")
                    print(json.dumps(avg_report, indent=4))
                else:
                    print("No report available")
            except ValueError:
                print("Invalid value for X. Please provide a valid integer")
                sys.exit(1)

        else:
            print(f"Unknown subcommand : {subcommand}")
            sys.exit(1)

    else:
        print(f"Unknown command : {command}")
        sys.exit(1)

