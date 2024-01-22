# Monitoring App

A simple Python script for monitoring system resources and port status.

## prerequisites

[Download Python](https://www.python.org/downloads/)

## installation

- clone the repository:

```bash
git clone https://github.com/uliaxe/monitoring.git
cd monitoring
```

- install dependencies :  

```bash
pip install psutil
```

## Usage

- Check System Resources

Execute the following command to generate a report on system resources:

```bash
python monit.py check
```

This command will create a report in the var/monit/ directory.

- List Reports

List all available reports:

```bash
python monit.py list
```

- Get Last Report

Retrieve and display the last generated report:

```bash
python monit.py get last
```

- Get Average Report

Retrieve and display the average report for the last X hours (replace X with the desired number of hours):

```bash
python monit.py get avg X
```

## Configuration

Edit the config.json file to specify the ports you want to monitor:

```json
{
  "ports_to_check": [80, 443, 22]
}

```
