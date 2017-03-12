# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import datetime
import logging
import os
import time
from tempfile import NamedTemporaryFile

import progressbar
import requests
import sys

from pgbackups import storage
from pgbackups.client import PgAttachment, PgBackupClient, BackupStatus

logger = logging.getLogger('pgbackups')


def setup_logging(enable_stdout_logging, log_name, log_level):
    global logger
    logger = logging.getLogger(log_name)
    logger.setLevel(getattr(logging, log_level))
    if enable_stdout_logging:
        logger.addHandler(logging.StreamHandler(sys.stdout))
    else:
        logger.addHandler(logging.NullHandler())


def archive(api_key=None, app_name=None, attachment_name=None,
            delete_after_backup=True, **storage_kwargs):
    """
    Initiate a postgres database backup on heroku, wait for it to complete,
    download the db dump once its complete and then upload it to s3. Finally delete
    the backup from `Heroku PGBackups` if `delete_after_backup` is set to be `True`
    :param api_key: Heroku API Key. Default is `None`. If None must be inclued
    :param app_name: Heroku APP for which backup needs to be performed
    :param attachment_name: Heroku Database for which backup needs to be performed
    :param delete_after_backup:
    :param storage_kwargs:
    :return:
    """

    api_key = api_key or os.environ.get('HEROKU_API_KEY') or None
    app_name = app_name or os.environ.get('PGBACKUPS_APP') or None
    attachment_name = attachment_name or os.environ.get('PGBACKUPS_DATABASE') or 'DATABASE'

    if None in (api_key, app_name, attachment_name):
        raise Exception('Heroku API Key, App Name and Postgres Attachment name '
                        'must be set in environment variables')

    attachment = get_attachment(api_key, app_name, attachment_name)
    logger.debug("Found PG Attachment: {}".format(attachment.plan.name))
    backup_uuid, backup_url = create_backups(api_key, app_name, attachment)
    logger.debug("PG Backup Completed. Backup Available at {}".format(backup_url))
    archive_backup_file(backup_url, file_name=get_backup_file_name(), **storage_kwargs)
    if delete_after_backup or os.environ.get('PGBACKUPS_DELETE_AFTER_ARCHIVE', True):
        delete_backup_heroku(api_key, app_name, attachment, backup_uuid)
        logger.debug("Deleted PG Backup from heroku: {}".format(backup_uuid))


def get_backup_file_name():
    file_name = os.environ.get('PGBACKUPS_FILENAME_TEMPLATE') or 'pgbackups'
    date_format = os.environ.get('PGBACKIPS_DATE_FORMAT') or '%Y-%m-%d-%H%M%S'

    current_time = datetime.datetime.utcnow().strftime(date_format)
    return '{}-{}.dump'.format(file_name, current_time)


def get_attachment(api_key, app_name, attachment):
    return PgAttachment.get(api_key, app_name, attachment)


def create_backups(api_key, app_name, pg_attachment):
    client = PgBackupClient(api_key, app_name, pg_attachment)
    backup = client.create_backup()
    logger.debug("PG Backup initiated. "
                 "Waiting for backup to complete: {}".format(backup.uuid))
    while True:
        status = client.get_backup_status(backup['uuid'])
        if status in (BackupStatus.RUNNING, BackupStatus.PENDING):
            time.sleep(10)

        elif status == BackupStatus.FAILED:
            raise Exception("Unable to capture backup. Try again later")

        else:
            return backup['uuid'], client.get_backup_public_url(backup['uuid'])


def archive_backup_file(url, file_name, **storage_kwargs):
    st = storage.get_storage(**storage_kwargs)
    ft = NamedTemporaryFile(delete=False)
    resp = requests.get(url, stream=True)
    content_length = int(resp.headers['content-length'])

    logger.debug("Downloading db dump. "
                 "Total Size of the Db Dump: {} MB".format(content_length / (1024 * 1024)))

    with progressbar.ProgressBar(max_value=content_length) as bar:
        chunk_size = 1024 * 1024  # 1 MB Chunk Size
        downloaded_content = 0
        for chunk in resp.iter_content(chunk_size=chunk_size):
            ft.write(chunk)
            downloaded_content += chunk_size
            bar.update(downloaded_content)

    logger.info("Downloaded the db dump")
    logger.debug("Started uploading the db dump to s3")
    st.store(ft.name, file_name)
    logger.debug("Uploaded the db dump to s3")
    os.unlink(ft.name)


def delete_backup_heroku(api_key, app_name, pg_attachment, backup_uuid):
    client = PgBackupClient(api_key, app_name, pg_attachment)
    resp = client.delete_backup(backup_uuid)
    resp.raise_for_status()
