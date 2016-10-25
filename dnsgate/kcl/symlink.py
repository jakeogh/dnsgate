#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common symlink functions
__version__ = "0.0.1"

from kcl.printops import LOG
from kcl.printops import eprint

def is_broken_symlink(path):
    if os.path.islink(path): # path is a symlink
        return not os.path.exists(path) # returns False for broken symlinks
    return False # path isnt a symlink

def is_unbroken_symlink(path):
    if os.path.islink(path): # path is a symlink
        return os.path.exists(path) # returns False for broken symlinks
    return False # path isnt a symlink

def get_symlink_abs_target(link): # assumes link is unbroken
    target = os.readlink(link)
    target_joined = os.path.join(os.path.dirname(link), target)
    target_file = os.path.realpath(target_joined)
    return target_file

def is_unbroken_symlink_to_target(target, link):    #bug, should not assume unicode paths
    if is_unbroken_symlink(link):
        link_target = get_symlink_abs_target(link)
        if link_target == target:
            return True
    return False

def create_relative_symlink(target, link_name):
    target = os.path.abspath(target)
    link_name = os.path.abspath(link_name)
    if not path_exists(target):
        eprint('target: %s does not exist. Refusing to make broken symlink. Exiting.',
            target, level=LOG['ERROR'])
        quit(1)

    if is_broken_symlink(link_name):
        eprint('ERROR: %s exists as a broken symlink. ' +
            'Remove it before trying to make a new symlink. Exiting.',
            link_name, level=LOG['ERROR'])
        quit(1)

    link_name_folder = '/'.join(link_name.split('/')[:-1])
    if not os.path.isdir(link_name_folder):
        eprint('link_name_folder: %s does not exist. Exiting.',
            link_name_folder, level=LOG['ERROR'])
        quit(1)

    relative_target = os.path.relpath(target, link_name_folder)
    os.symlink(relative_target, link_name)

if __name__ == '__main__':
    quit(0)
