#!/usr/bin/env python3
# tab-width:4
# pylint: disable=missing-docstring

# MIT License
# https://github.com/jakeogh/dnsgate/blob/master/LICENSE
#
# common file functions
__version__ = "0.0.1"

import time
import os
import shutil
import pprint
from shutil import copyfileobj

def comment_out_line_in_file(file_path, line_to_match):
    '''
    add a # to the beginning of all instances of line_to_match
    iff there is not already a # preceding line_to_match and
        line_to_match is the only thing on the line
            except possibly a preceeding # and/or whitespace

    if line_to_match is found and all instances are commented return True
    if line_to_match is found and all instances already commented return True
    if line_to_match is not found return False
    '''
    with open(file_path, 'r') as rfh:
        lines = rfh.read().splitlines()
    newlines = []
    commented = False
    for line in lines:
        if line_to_match in line:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                newlines.append(line)
                commented = True
                continue
            else:
                if line_stripped == line:
                    newlines.append('#' + line)
                    commented = True
                    continue
                else:
                    newlines.append(line)
                    continue
        else:
            newlines.append(line)
    if lines != newlines:
        fh.write('\n'.join(newlines) + '\n')
        return True
    elif commented:
        return True
    return False

def uncomment_line_in_file(file_path, line_to_match):
    '''
    remove # from the beginning of all instances of line_to_match
    iff there is already a # preceding line_to_match and
        line_to_match is the only thing on the line
            except possibly a preceeding # and/or whitespace

    if line_to_match is found and all instances uncommented return True
    if line_to_match is found and all instances already uncommented return True
    if line_to_match is not found return False
    '''
    with open(file_path, 'r') as rfh:
        lines = rfh.read().splitlines()
    newlines = []
    uncommented = False
    for line in lines:
        if line_to_match in line:
            line_stripped = line.strip()
            if line_stripped.startswith('#'):
                newlines.append(line[1:])
                uncommented = True
                continue
            else:
                if line_stripped == line:
                    newlines.append(line)
                    uncommented = True
                    continue
                else:
                    newlines.append(line)
                    continue
        else:
            newlines.append(line)

    if lines != newlines:
        fh.write('\n'.join(newlines) + '\n')
        return True
    if uncommented:
        return True
    return False

def write_unique_line_to_file(line, file_to_write):
    '''
    Write line to file_to_write iff line not in file_to_write.
    '''
    try:
        with open(file_to_write, 'r+') as fh:
            if line not in fh:
                fh.write(line)
    except FileNotFoundError:
        with open(file_to_write, 'a') as fh:
            fh.write(line)

def backup_file_if_exists(file_to_backup):
    timestamp = str(time.time())
    dest_file = file_to_backup.name + '.bak.' + timestamp
    try:
        with open(file_to_backup.name, 'r') as sf:
            with open(dest_file, 'x') as df:
                copyfileobj(sf, df)
    except FileNotFoundError:
        pass    # skip backup if file does not exist

def read_file_bytes(path):
    with open(path, 'rb') as fh:
        file_bytes = fh.read()
    return file_bytes

def path_exists(path):
    return os.path.lexists(path) #returns True for broken symlinks

if __name__ == '__main__':
    quit(0)
