# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import os
from abc import ABCMeta, abstractmethod

import boto3
import six

env_get = os.environ.get


class BackupStorage(six.with_metaclass(ABCMeta)):
    @abstractmethod
    def store(self, backup_file, filename):
        pass


class AWSStorage(BackupStorage):
    def __init__(self, aws_access_key=None,
                 aws_secret_key=None, aws_bucket=None, **aws_storage_options):

        aws_access_key = aws_access_key or env_get(
            'PGBACKUPS_AWS_ACCESS_KEY_ID')
        aws_secret_key = aws_secret_key or env_get(
            'PGBACKUPS_AWS_SECRET_ACCESS_KEY')
        self.bucket = aws_bucket or env_get('PGBACKUPS_AWS_BUCKET')

        self.storage_options = aws_storage_options or env_get('PGBACKUPS_STORAGE_OPTIONS', {})

        if None in (aws_access_key, aws_secret_key, self.bucket):
                raise Exception('''AWS Credentials/ Bucket must be provided''')

        self.s3 = boto3.client('s3',
                               aws_access_key_id=aws_access_key,
                               aws_secret_access_key=aws_secret_key)

    def store(self, backup_file, filename):
        self.s3.put_object(Bucket=self.bucket,
                           Key=filename, Body=backup_file, **self.storage_options)


def get_storage(**kwargs):
    return AWSStorage(**kwargs)

