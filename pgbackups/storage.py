# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import os
from abc import ABCMeta, abstractmethod

import boto3
import six


class BackupStorage(six.with_metaclass(ABCMeta)):
    @abstractmethod
    def store(self, backup_file, filename):
        pass


class AWSStorage(BackupStorage):
    def __init__(self):
        try:
            aws_access_key_id = os.environ['PGBACKUPS_AWS_ACCESS_KEY_ID']
            aws_secret_access_key = os.environ['PGBACKUPS_AWS_SECRET_ACCESS_KEY']
            self.bucket = os.environ['PGBACKUPS_AWS_BUCKET']
        except KeyError:
                raise Exception('''AWS Credentials/ Bucket must be set in
                                environment variables''')

        self.s3 = boto3.client('s3',
                               aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key)

    def store(self, backup_file, filename):
        storage_options = os.environ.get('PGBACKUPS_STORAGE_OPTIONS', None) or {}
        self.s3.put_object(Bucket=self.bucket,
                           Key=filename, Body=backup_file, **storage_options)


def get_storage():
    return AWSStorage()

