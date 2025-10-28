import subprocess

def open_file(path):
    subprocess.Popen(["xdg-open", path])
