import os
import signal
import psutil

def close_browser(app_name):
    """Close the specified browser."""
    for proc in psutil.process_iter():
        try:
            if proc.name() in ['chrome.exe', 'firefox.exe', 'msedge.exe']:  # Add other browsers if needed
                if app_name.lower() in proc.name().lower():
                    proc.terminate()  # Terminate the process
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def close_edge():
    """Close Microsoft Edge browser."""
    return close_browser('msedge')  # Reuse the close_browser function for Edge 