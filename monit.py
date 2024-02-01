"""Monitoring script for system resources and port status."""

import datetime
import os
import json
import socket
import sys
import psutil

# chemin dossier stockage rapport
REPORT_DIR = "var/monit/"


def create_report_dir():
    """Create the report directory if it does not exist."""
    if not os.path.exists(REPORT_DIR):
        os.makedirs(REPORT_DIR)


def get_timestamp():
    """Get the current timestamp."""
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def generate_report():
    """Generate a system resource usage report."""
    ram_percent = psutil.virtual_memory().percent
    cpu_percent = psutil.cpu_percent()
    disk_percent = psutil.disk_usage("/").percent

    the_report = {
        "timestamp": get_timestamp(),
        "id": hash(get_timestamp()),
        "ram usage": f"{ram_percent:.2f}% are used for RAM",
        "cpu usage": f"{cpu_percent:.2f}% are used for CPU",
        "disk usage": f"{disk_percent:.2f}% are used for Disk",
        "port status": check_ports(),
    }
    return the_report


def check_ports():
    """Check the status of configured ports."""
    # Charger les ports depuis le fichier de configuration
    config_filename = "config.json"

    if not os.path.exists(config_filename):
        print(f"Error: Configuration file '{config_filename}' not found.")
        sys.exit(1)

    try:
        with open(config_filename, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
            ports_to_check = config.get("ports_to_check", [])
    except json.JSONDecodeError as e:
        print(f"Error decoding the configuration file '{config_filename}': {e}")
        sys.exit(1)
    except KeyError as e:
        print(
            f"Error: Missing key '{e}' in the configuration file '{config_filename}'."
        )
        sys.exit(1)

    # Vérifier l'état de chaque port
    ports_status = {}
    for port in ports_to_check:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(("15.0.64.12", port))
        s.close()
        ports_status[port] = result == 0  # 0 indique une connexion réussie

    return ports_status


def save_report(reporter):
    """Save the generated report to a file."""
    create_report_dir()
    report_filename = REPORT_DIR + f'report_{reporter["id"]}.json'
    with open(report_filename, "w", encoding="utf-8") as report_file:
        json.dump(reporter, report_file, indent=4)


def list_reports():
    """List all available reports."""
    reportes = [
        f
        for f in os.listdir(REPORT_DIR)
        if f.startswith("report_") and f.endswith(".json")
    ]
    return reportes


def get_last_report():
    """Get the most recent report."""
    reporters = list_reports()
    if reporters:
        last_report_filename = REPORT_DIR + max(
            reporters, key=lambda x: os.path.getctime(os.path.join(REPORT_DIR, x))
        )
        with open(last_report_filename, "r", encoding="utf-8") as last_report_file:
            last_reporter = json.load(last_report_file)
            return last_reporter
    else:
        return None


def get_avg_report(lastest_hours):
    """Get the average report for the last specified hours."""
    reportse = list_reports()
    if reportse:
        recent_reports = sorted(reportse)[-lastest_hours:]
        avge_report = {"timestamp": get_timestamp(), "average_values": {}}
        for metric in ["ram_usage", "cpu_usage", "disk_usage"]:
            avg_metric_values = []

            for repaurt in recent_reports:
                try:
                    # Charger le rapport JSON
                    with open(
                        os.path.join(REPORT_DIR, repaurt), "r", encoding="utf-8"
                    ) as report_file:
                        report_data = json.load(report_file)

                    # Vérifier si la clé 'metric' existe dans le rapport
                    if metric in report_data:
                        avg_metric_values.append(report_data[metric])
                    else:
                        print(f"KeyError: '{metric}' not found in report '{repaurt}'")

                except json.JSONDecodeError as e:
                    print(f"Error decoding the report file '{repaurt}': {e}")
                except KeyError:
                    print(f"KeyError: '{metric}' not found in report '{repaurt}'")

            # Calculer la moyenne uniquement si des valeurs ont été trouvées
            if avg_metric_values:
                avge_report["average_values"][metric] = sum(avg_metric_values) / len(
                    avg_metric_values
                )

        return avge_report

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
        print(
            f"Check executed and report saved : {REPORT_DIR}report_{reports['id']}.json"
        )

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
