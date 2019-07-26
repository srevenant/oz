#!/usr/bin/env python3
# vim:set expandtab ts=4 sw=4 ai ft=python:
# vim modeline (put ":set modeline" into your ~/.vimrc)
# License by GNU Affrero - Derived from Protos Library code and online examples
"""

aws/boto3 wrapper for simplified use beyond the existing simple use of boto

cause I can

phonetic aws == oz

-B

"""
# http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#service-resource

import sys
import datetime
import time
import boto3
import botocore.exceptions
import json
import os
import configparser
import re

DEBUG = False

################################################################################
# from https://stackoverflow.com/questions/2319019/using-regex-to-remove-comments-from-source-files
def remove_comments(string):
    pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$|#[^\r\n]*$)"
    # first group captures quoted strings (double or single)
    # second group captures comments (//single-line or /* multi-line */)
    regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
    def _replacer(match):
        # if the 2nd group (capturing comments) is not None,
        # it means we have captured a non-quoted (real) comment string.
        if match.group(2) is not None:
            return "" # so we will return empty to remove the comment
        else: # otherwise, we will return the 1st group
            return match.group(1) # captured quoted-string
    return regex.sub(_replacer, string)

def load_hjson(path):
    with open(path) as infile:
        rawdata = []
        for line in infile:
            rawdata.append(remove_comments(line))
        try:
            return json.loads(''.join(rawdata))
        except ValueError as err:
            sys.exit("Cannot load {}: {}".format(path, err))

def load_data_file(path, abort=sys.exit):
    """
    Figure out which file to load from, and read in the data file, handling errors
    """
    try:
        if not os.path.exists(path):
            abort("Cannot find template-file: " + path)
        with open(path) as infile:
            spec = yaml.load(infile)
            spec['_file_'] = path
            return spec
    except Exception as err: # pylint: disable=broad-except
        abort(str(err))

################################################################################
def ignore_boto(errs, func, *args, **kwargs):
    """
    Catch boto errors and abort with a friendlier message
    """
    try:
        return func(*args, **kwargs)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] in errs:
            return False
        log("boto error = {}", err.response['Error'])
        traceback.format_exc()
        sys.exit(1)

################################################################################
def ignore(func, *args, **kwargs):
    """
    Just ignore it all
    """
    try:
        func(*args, **kwargs)
    except: # pylint: disable=bare-except
        pass

################################################################################
def good(condition, msg, *args, **kwargs):
    """Similar to assert, but always inline (not compiled out) and with more
       formatting functionality"""

    if not condition:
        msg = msg.format(*args, **kwargs)
        if kwargs.get('abort'):
            kwargs.get('abort')(msg)
        else:
            sys.exit(msg)

################################################################################
def missing(obj, key, abort=None, pre=None):
    """
    Recursively pull from a dictionary, using dot notation. Fail if not found.
    >>> missing({"a":{"b":{"c":1}}}, "a.b.c")
    1
    >>> missing({"a":{"b":{"c":1}}}, "a.d.c")
    Traceback (most recent call last):
    ...
    SystemExit: a.d is missing
    """
    return _missing(obj, [], key.split("."), abort=abort, pre=pre)

################################################################################
# pylint: disable=too-many-instance-attributes


class OzCore(object):
    """
    """
    args = None
    cfg = None
    aws = None
    start = None

    ############################################################################
    # pylint: disable=too-many-arguments
    def __init__(self, args):
        self.start = time.time()

        self.cfg = load_hjson(args.profile)

        print("Loading ~/.aws/credentials...")
        credsfile = os.path.expanduser("~/.aws/credentials")
        if not os.path.exists(credsfile):
            sys.exit("Missing ~/.aws/credentials?")
        creds = configparser.ConfigParser()
        creds.read(credsfile)
        aws_profile = 'default'
        if os.environ.get("AWS_PROFILE"):
            aws_profile = os.environ["AWS_PROFILE"]
        elif self.cfg.get("AWS_PROFILE"):
            aws_profile = self.cfg.get("AWS_PROFILE")
        if aws_profile not in creds.sections():
            sys.exit("AWS PROFILE `{}` is missing from ~/.aws/credentials".format(aws_profile))

        self.cfg['aws'].update(creds[aws_profile])

        # setup
        start = time.time()
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

        # connect to aws
        self.aws = boto3.session.Session(**self.cfg['aws'])
        self.args = args
