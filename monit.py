#show RAM usage

import psutil

try:
    ram_info = psutil.virtual_memory()
    print(f"Total: {ram_info.total / 1024 / 1024 / 1024:.2f} GB")
    print(f"Available: {ram_info.available / 1024 / 1024 / 1024:.2f} GB")
    print(f"Used: {ram_info.used / 1024 / 1024 / 1024:.2f} GB")
    print(f"Percentage usage: {ram_info.percent}%")
except FileNotFoundError:
    print("Ram info not available on this system")

#show CPU usage
    
try:
    cpu_info = psutil.cpu_percent()
    print(f"CPU usage: {cpu_info}%")

    cpu_info = psutil.cpu_freq()
    print(f"CPU frequency: {cpu_info.current:.2f} Mhz")
    print(f"CPU max frequency: {cpu_info.max:.2f} Mhz")
    print(f"CPU min frequency: {cpu_info.min:.2f} Mhz")

except FileNotFoundError:
    print("CPU info not available on this system")

#show disk usage
    
try:
    disk_info = psutil.disk_usage('/')
    print(f"Total: {disk_info.total / 1024 / 1024 / 1024:.2f} GB")
    print(f"Used: {disk_info.used / 1024 / 1024 / 1024:.2f} GB")
    print(f"Free: {disk_info.free / 1024 / 1024 / 1024:.2f} GB")
    print(f"Percentage usage: {disk_info.percent}%")

except FileNotFoundError:
    print("Disk info not available on this system")
    