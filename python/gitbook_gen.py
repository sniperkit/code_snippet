# -*- coding: utf-8 -*-
"""
This script will generate a gitbook projects based on the given dir.
The generated dir contains the same structure and the corresponding markdown
files.

To update the structure, please keep a copy of your README.md and SUMMARY.md.
This tool should never overwrite other files.

Usage: python gitbook_gen [src_dir1] [src_dir2] ...

The generated books will have names like `src_dir1_gitbook`, 'src_dir2_gitbook'

Author: yeasy@github.com
"""

import __future__  # noqa
import os
import sys
from fnmatch import fnmatch

ROOT_PATH = os.getcwd()
PROJECT = ""
README = "README.md"
SUMMARY = "SUMMARY.md"
IGNORES=['*readme.md', '*build*', '*_test.go']  # path with these patterns will be ignored

generator_info = \
    "The book structure is generated by [gitbook_gen]" \
    "(https://github.com/yeasy/code_snippet/#gitbook_gen)."


def init_gitbook_dir(dir_path, title):
    """ Initialized a gitbook dir.

     Init a README.md and a SUMMARY.md

    :param dir_path: whole dir path
    :param title: project title
    :return:
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    create_file(README,
                "# {}\n\n{}".format(title, generator_info), forced=False)
    create_file(SUMMARY, "# Summary\n\n* [Introduction](README.md)",
                forced=True)


def refine_dirname(name):
    """ Refine a dir name to make sure it's validate for processing.

    e.g., ./yeasy_book/ --> yeasy_book

    :param name: directory name to refine
    :return: refined result
    """
    name = name.replace('.' + os.sep, '')  # remove './'
    if name.endswith('/') or name.endswith('\\'):
        name = name[:-1]
    return name


def has_pattern(path_name, patterns=IGNORES):
    """ Test whether path_name has a given pattern

    :param path_name:
    :param patterns:
    :return:
    """

    def test_pattern(pattern):
        return fnmatch(path_name, pattern)
    result = filter(test_pattern, patterns)
    # print(path_name)
    # print(result)
    return len(result) > 0


def process_dir(root_dir, level=1):
    """ Process the directory, checking sub dirs and files recursively.

    :param root_dir: current root dir
    :param level: current depth of the dir from the root
    :return:
    """
    if level > 4:  # do not process very deep dir
        return
    valid_dirs = filter(lambda x: not x.startswith('.'), os.listdir(root_dir))
    list_dir = filter(lambda x: os.path.isdir(os.path.join(root_dir, x)),
                      valid_dirs)
    list_file = filter(lambda x: os.path.isfile(os.path.join(root_dir, x)) and
                                 not x.startswith('_'), valid_dirs)
    for e in list_dir:  # dirs
        if has_pattern(e):
            continue
        path = os.path.join(root_dir, e).replace('.' + os.sep, '')
        if level == 4:
            create_file(PROJECT + os.sep + path + '.md', '#' * level + ' ' + e)
            line = '* [%s](%s.md)' % (e, path.replace('\\', '/'))
        else:
            if not os.path.exists(PROJECT+os.sep+path):
                os.makedirs(PROJECT + os.sep + path)
            create_file(PROJECT + os.sep + path + os.sep + 'README.md',
                        '#' * level + ' ' + e, forced=False)
            line = '* [%s](%s/README.md)' % (e, path.replace('\\', '/'))
        update_file(SUMMARY, ' ' * 4 * (level - 1) + line)
        process_dir(path, level+1)
    for e in list_file:  # files
        if has_pattern(e):
            continue
        name, suffix = os.path.splitext(e)  # test .py
        path = os.path.join(root_dir, name).replace('.' + os.sep, '') \
               + suffix.replace('.', '_')  # test\test_py
        create_file(PROJECT + os.sep + path + '.md', '#' * level + ' ' + e)
        line = '* [%s](%s.md)' % (e, path.replace('\\', '/'))
        update_file(SUMMARY, ' ' * 4 * (level - 1) + line)


def create_file(file_path, content, forced=False):
    """ Create a file at the path, and write the content.
    If not forced, when file already exists, then do nothing.

    :param file_path: The whole path of the file
    :param content: Content to write into the file
    :param forced: Whether to force to overwrite file content, default to False
    :return: None
    """
    if os.path.isfile(file_path) and not forced:
        print("Warn: {} already exists, stop writing content={}".format(
            file_path, content))
        return
    with open(file_path, 'w') as f:
        f.write(content+'\n')


def update_file(file_path, content, append=True, debug=False):
    """ Update the content into the file_path

    Potentially this can be merged with create_file, but maybe too heavy

    :param file_path: The whole path of the file
    :param content: content to append to SUMMARY file
    :param debug: Whether to output the result
    :param append: Whether to append the content
    :return: None
    """
    if append:
        with open(file_path, 'a') as f:
            f.write(content + '\n')
    else:
        with open(file_path, 'w') as f:
            f.write(content + '\n')
    if debug:
        print(content)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        for d in sys.argv[1:]:
            if not os.path.exists(d):
                print("WARN: dir name {} does not exist".format(d))
                continue
            d = refine_dirname(d)
            PROJECT = ROOT_PATH + os.sep \
                      + d.replace('/', '_').replace('\\', '_') \
                      + '_gitbook'
            README = PROJECT + os.sep + 'README.md'
            SUMMARY = PROJECT + os.sep + 'SUMMARY.md'
            print("Will init the output dir={}".format(PROJECT))
            init_gitbook_dir(PROJECT, d)
            os.chdir(d)
            process_dir('.')
    else:
        print("Put the input dir name(s) as parameters")
        print("Usage: python gitbook_gen [source_dir1] [source_dir2] ... ")
