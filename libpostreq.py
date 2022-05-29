"""Lib Post-requirements"""

from os.path import expanduser, exists

PATH = ['/usr/local/lib/python3.9', '/usr/local/lib/python3.9/site-packages',
        expanduser("~/.local/lib/python3.9/site-packages")]


def _finder(module, type='module'):
    for path in PATH:
        a = '.py' if type == 'module' else ''
        if exists(path+f'/{module}{a}'):
            return True
    return False


yaml_installed = _finder('yaml') or _finder('yaml', 'package')
pygame_installed = _finder('pygame') or _finder('pygame', 'package')
