#!/usr/bin/env python

import sys
import collections
import json
import os
import tempfile
import subprocess

from argparse import ArgumentParser, Action


class ConsumerAction(Action):
    all_actions = []
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ConsumerAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        self.all_actions.append([self.dest, values])
        setattr(namespace, self.dest, values)


def build_argparser():
    arg_parser = ArgumentParser()

    arg_parser.add_argument('-a', '--add', action=ConsumerAction, help='Add a file from a source, possibly a url, into the container')
    arg_parser.add_argument('-c', '--copy', action=ConsumerAction, help='Copy a file into the container')
    arg_parser.add_argument('-e', '--env', action=ConsumerAction, help='Environment variable')
    arg_parser.add_argument('-k', '--healthcheck', action=ConsumerAction, help='Define a healthcheck command')
    arg_parser.add_argument('-l', '--label', action=ConsumerAction, help='Add a label to the metadata')
    arg_parser.add_argument('-m', '--cmd', action=ConsumerAction, help='Set the command')
    arg_parser.add_argument('-n', '--entrypoint', action=ConsumerAction, help='Set the entrypoint for the container')
    arg_parser.add_argument('-o', '--onbuild', action=ConsumerAction, help='Set a command to run when the image is used as a base')
    arg_parser.add_argument('-p', '--stopsignal', action=ConsumerAction, help='Set the signal that will stop the container')
    arg_parser.add_argument('-r', '--run', action=ConsumerAction, help='Set the run command')
    arg_parser.add_argument('-s', '--shell', action=ConsumerAction, help='Define the default shell used for shell-style commands')
    arg_parser.add_argument('-u', '--user', action=ConsumerAction, help='Change the active user')
    arg_parser.add_argument('-v', '--volume', action=ConsumerAction, help='Mark a directory as a volume')
    arg_parser.add_argument('-w', '--workdir', action=ConsumerAction, help='Change the working directory')
    arg_parser.add_argument('-x', '--expose', action=ConsumerAction, help='Expose a port')

    arg_parser.add_argument('-f', '--from', required=True, dest='from_container', help='Container to pull from')
    arg_parser.add_argument('-b', '--build-dir', default=os.getcwd(), help='The build folder')
    arg_parser.add_argument('-t', '--tag', help='The tag to create')
    arg_parser.add_argument('--pull', action='store_true', help='Try to pull a new copy of the FROM image')
    arg_parser.add_argument('--push', action='store_true', help='Push the resulting image')
    arg_parser.add_argument('--edit', action='store_true', help='Edit the dockerfile before building')

    return arg_parser


def build_dockerfile(from_container, actions):
    lines = []
    lines.append('FROM %s' % from_container)

    for action in actions:
        key = action[0]
        value = action[1]
        lines.append(' '.join([key.upper(), value]))

    return '\n'.join(lines) + '\n'


def write_tempfile(file_string):
    new_file, filename = tempfile.mkstemp()
    os.write(new_file, file_string)
    os.close(new_file)
    return filename


def edit_file(filename):
    args_list = ['nano', filename]
    process = subprocess.Popen(' '.join(args_list), stdout=sys.stdout, stderr=sys.stderr, shell=True)
    stdout, stderr = process.communicate()


def build_image(filename, tag_name, build_dir):
    args_list = [
        'docker',
        'build',
        '-f',
        filename,
    ]
    if tag_name != None:
        args_list.extend([
            '-t',
            tag_name
        ])
    args_list.append(build_dir)

    process = subprocess.Popen(' '.join(args_list), stdout=sys.stdout, stderr=sys.stderr, shell=True)
    stdout, stderr = process.communicate()


def push_image(tag_name):
    args_list = [
        'docker',
        'push',
        tag_name
    ]

    process = subprocess.Popen(' '.join(args_list), stdout=sys.stdout, stderr=sys.stderr, shell=True)
    stdout, stderr = process.communicate()


def pull_image(tag_name):
    args_list = [
        'docker',
        'pull',
        tag_name
    ]

    process = subprocess.Popen(' '.join(args_list), stdout=sys.stdout, stderr=sys.stderr, shell=True)
    stdout, stderr = process.communicate()


def print_summary(filename):
    # print('----------')
    # print('Summary:')
    print('Dockerfile located at: %s' % filename)


def main(args):
    parsed_args = build_argparser().parse_args()
    file_string = build_dockerfile(parsed_args.from_container, ConsumerAction.all_actions)
    filename = write_tempfile(file_string)
    if parsed_args.edit:
        edit_file(filename)
    if parsed_args.pull:
        pull_image(parsed_args.from_container)
    build_image(filename, parsed_args.tag, parsed_args.build_dir)
    if parsed_args.tag is not None and parsed_args.push:
        push_image(parsed_args.tag)
    print_summary(filename)


if __name__ == '__main__':
    main(sys.argv[1:])
