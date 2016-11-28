# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import os

import time
from invoke import task

from pgbackups.client import PgAttachment, PgBackupClient, BackupStatus


@task
def pg_backup_archive(ctx, api_key=None, app_name=None, attachment=None):
    api_key = api_key or os.environ.get('HEROKU_API_KEY') or None
    app_name = app_name or os.environ.get('PGBACKUPS_APP') or None
    attachment_name = attachment or os.environ.get('PGBACKUPS_DATABASE') or 'DATABASE'

    if None in (api_key, app_name, attachment_name):
        raise Exception('Heroku API Key, App Name and Postgres Attachment name '
                        'must be set in environment variables')

    backup_url = create_backups(api_key, app_name, attachment)




def get_attachment(api_key, app_name, attachment):
    return PgAttachment.get(api_key, app_name, attachment)


def create_backups(api_key, app_name, pg_attachment):
    client = PgBackupClient(api_key, app_name, pg_attachment)
    backup = client.create_backup()
    status = client.get_backup_status(backup['uuid'])
    if status in (BackupStatus.RUNNING || BackupStatus.PENDING):
        time.sleep(2000)

    elif status == BackupStatus.FAILED:
        raise Exception("Unable to capture backup. Try again later")

    else:
        return client.get_backup_public_url(backup['uuisd'])

def download_backup_file():
    pass

