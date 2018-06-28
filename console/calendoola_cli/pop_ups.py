import subprocess


def call(title, info):
    """
    Pop-up notification
    Args:
        title(str): title of notification
        info(str): information of notification
    """
    subprocess.check_call(['notify-send', title, info])

