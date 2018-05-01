import subprocess


def call(title, info):
    """
    pop-up notification
    :param title: title of notification
    :param info: information of notification
    """
    subprocess.call(['notify-send', title, info])
