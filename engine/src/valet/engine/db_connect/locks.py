#
# -------------------------------------------------------------------------
#   Copyright (c) 2019 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#
import re
import time

from valet.utils.logger import Logger


def now():
    return int(round(time.time() * 1000))


def later(minutes=0, seconds=0):
    # Consider 20 sec as a lead time.
    seconds -= 20
    return int(round(time.time() * 1000)) + (minutes * 60 + seconds) * 1000


class Locks(object):
    """Manage locking as a semaphore.

    A region lock that manages locks and the region table to
    lock the entire time while working on a region.
    """

    Lockspace = "engine"

    def __init__(self, dbh, timeout=None):
        self.dbh = dbh
        self.db = dbh.db
        self.timeout = timeout

        self.locked_regions = []
        self.expired = 0
        self.locked = False
        self.region = None
        self.key = None

    def set_regions(self):
        """Set locked regions."""

        lr = self.dbh.clean_expired_regions()
        if lr is None:
            return False

        self.locked_regions = lr

        return True

    def _add_region(self, region):
        """Set when to expire and update/add to region table."""

        self.expired = later(seconds=self.timeout)
        self.region = region

        if not self.dbh.add_region(self.region, self.expired):
            return None

        return "yes"

    def is_my_turn(self, region):
        """Try for a lock, unless you know its already locked.

        If you already have the lock, just update the expire time."""

        if self.expired < now():
            self.locked = False

        if self.locked:
            if not self.region == region:
                return "no"

            return self._add_region(region)

        if region in self.locked_regions:
            return "no"

        self.db.logger.debug("try lock region: " + region)

        if self._add_region(region) is None:
            return None

        status = self.got_lock(region)
        if status is None:
            return None

        if status == "fail":
            self.locked = False
            return "no"

        self.locked = True

        return "yes"

    def got_lock(self, key):
        """I got lock if I get the first (0) lock"""

        self.key = '%s.%s.%s' % (self.dbh.keyspace, Locks.Lockspace, key)

        try:
            lock_id = self.db.create_lock(self.key)
        except Exception as e:
            Logger.get_logger('debug').error("DB: while creating lock: " + str(e))
            return None

        if 0 == int(re.search('-(\d+)$', lock_id).group(1)):
            return "ok"
        else:
            return "fail"

    def done_with_my_turn(self):
        """Release lock and clear from region table."""

        if not self.locked:
            return "ok"

        try:
            self.db.delete_lock(self.key)
        except Exception as e:
            Logger.get_logger('debug').error("DB: while deleting lock: " + str(e))
            return None

        if not self.dbh.delete_region(self.region):
            return None

        self.locked = False
        self.region = None

        return "ok"

    @staticmethod
    def unlock(dbh, key):
        """Removes the lock for a key."""

        key = '%s.%s.%s' % (dbh.keyspace, Locks.Lockspace, key)
        dbh.db.delete_lock(key)
