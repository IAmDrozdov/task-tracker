import subprocess


def call(title, info):
    subprocess.call(['notify-send', title, info])
