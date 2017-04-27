#!/usr/bin/env python
"""
Scans the type-script files and generates a reverse dependency
graph for import found in the given input files
for e.g. run the program like:

$ depends.py interface.ts
subscription/subscription.ts <- apisession/session.ts
config.ts <- apisession/session.ts
apisession/session.ts <- interface.ts
interface.ts <- util/historical-buffer-manager.ts
util/map.ts <- apisession/session.ts
blpapi-wrapper.ts <- interface.ts, apisession/session.ts, subscription/subscription.ts
util/historical-buffer-manager.ts <- subscription/subscription.ts
"""
import os
import re
import sys


def get_path(d, f):
    """
    Gets the physical path to a given directory and typescript file name, also
    appends the .ts extension to the filename
    for e.g. for 'dir1/dir2' and '../file1' returns dir1/file1.ts

    :param d: Directory where the file is located relatively
    :param f: path to file relative to the directory
    :return: returns a normalized path
    """
    return os.path.normpath(os.path.join(d, f + ".ts"))


def get_imports(input_file):
    """
    Scans the given file for imports

    :param input_file: file to be scanned and check for imports
    :return: returns list of import files that are found via regex processing
    """
    pattern = re.compile('(?:^|\n)\s*import.+require.*\(\s*[\'\"](\.+.*)[\'\"]\s*\);')

    with open(input_file) as f:
        return pattern.findall(f.read())


def main(input_files):
    """
    main driver for processing the files to find imports and generate reverse-
    dependency graph. The reverse dependency graph is a dictionary with key values
    as files, and dependencies referring to it

    :param input_files: files to be processed
    :return: dict type with files as keys and files depended on it as values
    """
    dependencies = {}
    for input_file in input_files:
        dir_name = os.path.dirname(input_file)
        try:
            import_files = get_imports(input_file)
            if import_files:
                rel_paths = set([get_path(dir_name, import_file)
                                 for import_file in import_files])
                input_files += rel_paths.difference(input_files)
                for rel_path in rel_paths:
                    dependencies.setdefault(rel_path, []).append(input_file)
        except IOError as e:
            print "I/O error({0}): {1} skipping {2}".format(e.errno, e.strerror, input_file)

    return dependencies

if __name__ == "__main__":
    if sys.argv[1:]:
        dependencies = main(sys.argv[1:])
        for k, v in dependencies.iteritems():
            print k, "<-", ", ".join(v)
    else:
        print "No arguments, expect file names for processing"
