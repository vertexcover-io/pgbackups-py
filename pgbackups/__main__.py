# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division

import logging

import sys

from pgbackups import archive


if __name__ == '__main__':
    logger = logging.getLogger('pgbackups')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    archive()
