import psutil, os

def print_memory_usage(tag=""):
    print(f"[MEMORY {tag}] Used: {psutil.Process(os.getpid()).memory_info().rss / 1024**2:.2f} MB")
