# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import base64
import re

import requests
from attrdict import AttrDict
from enum import Enum
from six.moves.urllib.parse import urljoin


class BackupStatus(Enum):
    COMPLETED = 'completed'
    RUNNING = 'running'
    PENDING = 'pending'
    FAILED = 'error'


class PgAttachment(AttrDict):

    BASIC_PLAN_RE = re.compile(r'(dev|basic)')

    def __init__(self, attachment_dict):
        super(PgAttachment, self).__init__(attachment_dict)

    def is_basic_plan(self):
        return self.BASIC_PLAN_RE.search(self.plan.name) is not None

    @classmethod
    def get(cls, api_key, app_name, attachment_name):
        headers = {
            'Authorization': 'Bearer %s'.format(api_key),
            'Accept': 'application/vnd.heroku+json; version=3'
        }
        url = 'https://api.heroku.com/apps/{}/addons/{}'.format(app_name,
                                                                attachment_name)
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        attachment = resp.json()
        return PgAttachment(attachment)


class PgBackupClient(object):

    BASE_URL = 'https://{}/client/v11/databases'

    def __init__(self, heroku_api_key, app_name, pg_attachment):

        self._api_key = base64.b64encode(heroku_api_key)
        self._app_name = app_name
        self._pg_attachment = pg_attachment
        self._db_name = self._pg_attachment.name

        if self._pg_attachment.is_basic_plan():
            host = 'https://postgres-starter-api.heroku.com'
        else:
            host = 'https://postgres-api.heroku.com'

        self._db_base_url = urljoin(host,
                                    'client/v11/databases/{}/'.format(self._db_name))

        self._app_base_url = urljoin(host,
                                     'client/v11/apps/{}/'.format(self._app_name))

        self._urls = {
            'capture_backup': '/{db_name}/backups'.format(
                db_name=self._db_name),
            'get_backup': '/{db_name}/transfers/%%s'.format(
                db_name=self._db_name)
        }

    def _get_headers(self):
        return {
            'Authorization': 'Basic {}'.format(self._api_key)
        }

    def create_backup(self):
        url = urljoin(self._db_base_url, 'backups')
        headers = self._get_headers()
        resp = requests.post(url, headers=headers)
        resp.raise_for_status()
        return AttrDict(resp.json())

    def get_backup(self, backup_uuid):
        url = urljoin(self._db_base_url,
                      'transfers/{}'.format(backup_uuid))

        headers = self._get_headers()

        resp = requests.get(url, headers=headers)

        resp.raise_for_status()

        return AttrDict(resp.json())

    def get_backup_status(self, backup_uuid):
        resp = self.get_backup(backup_uuid=backup_uuid)
        if resp.finished_at:
            return BackupStatus.COMPLETED if resp.succeeded else BackupStatus.FAILED

        return BackupStatus.RUNNING if resp.started_at else BackupStatus.PENDING

    def get_backup_public_url(self, backup_uuid):
        url = urljoin(self._app_base_url,
                      'transfers/{}/actions/public-url'.format(backup_uuid))
        headers = self._get_headers()

        resp = requests.post(url, headers=headers)

        resp.raise_for_status()

        return resp.json()['url']

    def delete_backup(self, backup_uuid):
        url = urljoin(self._db_base_url, 'backups/{}'.format(backup_uuid))
        headers = self._get_headers()
        return requests.delete(url, headers=headers)
