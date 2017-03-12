#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import argparse

from pgbackups.api import setup_logging, archive


class StoreNameValuePair(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        n, v = values.split('=')
        setattr(namespace, n, v)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Perform Postgres Backup on heroku and store to s3')
    parser.add_argument('--app', dest='app',
                        help="Heroku App for which backup needs to be performed")

    parser.add_argument('--api-key', dest='api_key',
                        help='API key for heroku', )

    parser.add_argument('--db', dest='db_name', default='DATABASE',
                        help='Name of Heroku database', )

    parser.add_argument('--access-key', dest='access_key',
                        help='AWS Access Key')

    parser.add_argument('--secret-key', dest='secret_key',
                        help='AWS SECRET Key')

    parser.add_argument('--aws-bucket', dest='aws_bucket',
                        help='AWS S3 Bucket')

    parser.add_argument('--log-level', dest='log_level', default='DEBUG',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Log Level')

    parser.add_argument('--disable-logging', dest='disable_logging', action='store_true',
                        help='Disable default logging handler (stdout)',)

    parser.add_argument('--log-name', dest='log_name', default='pgbackups',
                        help='Log Name')

    parser.add_argument('--storage-opts', dest='storage_options',
                        action=StoreNameValuePair, nargs='*',
                        help='set additional storage options as key=value')

    parser.add_argument('--delete-after', dest='delete_after_backup',
                        action='store_true',
                        help='Delete backups from heroku after storing',
                        default=True)

    return parser.parse_args()


def parse_aws_options(opts):
    aws_opts = {}
    if opts.access_key:
        aws_opts['aws_access_key'] = opts.access_key

    if opts.secret_key:
        aws_opts['aws_secret_key'] = opts.secret_key

    if opts.access_key:
        aws_opts['aws_bucket'] = opts.aws_bucket

    if opts.storage_options:
        aws_opts['aws_storage_options'] = opts.storage_options

    return aws_opts


def main():
    args = parse_arguments()
    storage_kwargs = parse_aws_options(args)
    setup_logging(not args.disable_logging, args.log_name, args.log_level)
    archive(api_key=args.api_key, app_name=args.app,
            attachment_name=args.db_name,
            delete_after_backup=args.delete_after_backup,
            **storage_kwargs)

if __name__ == '__main__':
    main()

