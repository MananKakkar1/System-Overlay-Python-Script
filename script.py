import psutil
import time
import clr
import os
import sys
import ctypes
import tkinter as tk
from tkinter import ttk
import subprocess


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


if not is_admin():
    params = ' '.join([sys.executable] + sys.argv)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

ohm_path = r'C:\OpenHardwareMonitor\OpenHardwareMonitor.exe'


def is_ohm_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'OpenHardwareMonitor.exe':
            return True
    return False


if not is_ohm_running():
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", ohm_path, None, None, 0)
    except Exception as e:
        print(f"Error starting OpenHardwareMonitor: {e}")
    time.sleep(5)

clr.AddReference(r'C:\OpenHardwareMonitor\OpenHardwareMonitorLib.dll')
from OpenHardwareMonitor.Hardware import Computer, HardwareType, SensorType


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    memory = psutil.swap_memory()
    return memory.percent, memory.total, memory.used


def get_disk_usage():
    disk = psutil.disk_usage('/')
    total_gb = disk.total / (1024 ** 3)
    used_gb = disk.used / (1024 ** 3)
    return disk.percent, total_gb, used_gb


def get_network_usage():
    network = psutil.net_io_counters()
    return network.bytes_sent, network.bytes_recv


def get_components_type():
    computer = Computer()
    computer.MainboardEnabled = True
    computer.CPUEnabled = True
    computer.RAMEnabled = True
    computer.GPUEnabled = True
    computer.SSDEnabled = True
    computer.Open()

    components = {}
    for hardware in computer.Hardware:
        hardware.Update()
        components[hardware.Name] = str(hardware.HardwareType)
    return components


def close_ohm():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'OpenHardwareMonitor.exe':
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except psutil.AccessDenied:
                pass
            except psutil.TimeoutExpired:
                pass


def update_info():
    cpu_usage.set(f"CPU Usage: {get_cpu_usage()} %")
    mem = get_memory_usage()
    memory_usage.set(
        f"Memory Usage: {mem[0]} % (Used: {mem[2] / (1024 ** 3):.2f} GB, Total: {mem[1] / (1024 ** 3):.2f} GB)")
    disk = get_disk_usage()
    disk_usage.set(f"Disk Usage: {disk[0]} % (Used: {disk[2]:.2f} GB, Total: {disk[1]:.2f} GB)")
    network = get_network_usage()
    network_usage.set(f"Network Sent: {network[0] / (1024 ** 2):.2f} MB, Received: {network[1] / (1024 ** 2):.2f} MB")
    components = get_components_type()
    components_info.set("\n".join([f"{key}: {value}" for key, value in components.items()]))
    root.after(1000, update_info)


root = tk.Tk()
root.title("System Overlay")

cpu_usage = tk.StringVar()
memory_usage = tk.StringVar()
disk_usage = tk.StringVar()
network_usage = tk.StringVar()
components_info = tk.StringVar()

ttk.Label(root, textvariable=cpu_usage).pack()
ttk.Label(root, textvariable=memory_usage).pack()
ttk.Label(root, textvariable=disk_usage).pack()
ttk.Label(root, textvariable=network_usage).pack()
ttk.Label(root, text="Components:").pack()
ttk.Label(root, textvariable=components_info).pack()

update_info()
root.mainloop()
