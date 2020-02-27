import subprocess
import json
import requests
import os
import platform
from utils import is_frozen, resource_dir


def open_browser():
    """
    Open browser with Uber login
    :return: None
    """
    if platform.system() == 'Darwin':
        print('Darwin here')
        if is_frozen:
            path = 'web.app/Contents/MacOS/web'
        else:
            path = 'browser/web.app/Contents/MacOS/web'
    else:
        if is_frozen:
            path = 'web'
        else:
            path = 'browser/web'

    app = os.path.join(resource_dir, path)
    print(app)

    p = subprocess.Popen([app])
    p.wait()

    print('Done')


def loading_cookies():
    """
    Loading cookies from browser to session
    :return:
    """
    session = requests.session()
    pre = os.path.expanduser('~')
    path = os.path.join(pre, 'UberLyftCookies')
    if os.path.exists(path):
        filename = os.path.join(path, 'data.json')

        with open(filename, 'r') as infile:
            cookie_dict = json.load(infile)

        session.cookies.update(cookie_dict)

        #print(json.dumps(session.cookies.get_dict(), indent=4, sort_keys=True))
        return session
    else:
        return None
