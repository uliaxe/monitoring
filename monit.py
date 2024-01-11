import psutil

def check_ram():
    return psutil.virtual_memory().percent

def check_cpu():
    return psutil.cpu_percent(interval=1)

def check_disk():
    return psutil.disk_usage('/').percent
