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


"""Setup logging.
from valet.utils.logger import Logger
        Logger.get_logger('metric').info('bootstrap STUFF')
"""

import json
import logging
import socket
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Logger(object):
    logs = None

    def __init__(self, _config=None, console=False):
        if _config is None:
            Logger.logs = {"console": Console()}

        if Logger.logs is None:
            Logger.logs = {"audit": Audit(_config), "metric": Metric(_config), "debug": Debug(_config)}
            Logger.logs["error"] = Error(_config, Logger.logs["debug"])
            if console:
                Logger.logs["console"] = Console(Logger.logs["debug"])

    @classmethod
    def get_logger(cls, name):
        return cls.logs[name].adapter

    @classmethod
    def set_req_id(cls, uuid):
        EcompLogger._set_request_id(uuid)


class EcompLogger(object):
    """Parent class for all logs."""
    logging.getLogger().setLevel(logging.DEBUG)  # set root
    _lvl     = logging.INFO
    _size    = 10000000
    datefmt = '%d/%m/%Y %H:%M:%S'

    _requestID = None

    def __init__(self):
        self.fh = None
        self.logger = None

    def set_fh(self, name, fmt, _config, lvl=_lvl, size=_size):
        logfile = _config.get("path") + name + ".log"
        self.fh = RotatingFileHandler(logfile, mode='a', maxBytes=size, backupCount=2, encoding=None, delay=0)
        self.fh.setLevel(lvl)
        self.fh.setFormatter(fmt)

        self.logger = logging.getLogger(name)
        self.logger.addHandler(self.fh)
        self.fh.addFilter(LoggerFilter())

    def add_filter(self, fltr):
        self.fh.addFilter(fltr())

    @classmethod
    def get_request_id(cls): return EcompLogger._requestID

    @classmethod
    def _set_request_id(cls, uuid): EcompLogger._requestID = uuid
        
    @staticmethod
    def format_str(fmt, sep="|"):
        fmt = sep + sep.join(map(lambda x: '' if x.startswith('X') else '%(' + str(x) + ')s', fmt)) + sep
        return fmt.replace('%(asctime)s', '%(asctime)s.%(msecs)03d')


class LoggerFilter(logging.Filter):
    def filter(self, record):
        record.requestId = EcompLogger.get_request_id() or ''
        return True


class Audit(EcompLogger):
    """A summary view of the processing of a requests.
    It captures activity requests and includes time initiated, finished, and the API who invoked it
    """
    fmt = ['beginTimestamp', 'asctime', 'requestId', 'XserviceInstanceID', 'XthreadId', 'vmName', 'XserviceName', 'XpartnerName', 'statusCode', 'responseCode', 'responseDescription', 'XinstanceUUID', 'levelname', 'Xseverity', 'XserverIP', 'elapsedTime', 'server', 'XclientIP', 'XclassName', 'Xunused', 'XprocessKey', 'message', 'XcustomField2', 'XcustomField3', 'XcustomField4', 'XdetailMessage']

    def __init__(self, _config):
        EcompLogger.__init__(self)
        fmt = logging.Formatter(self.format_str(Audit.fmt), EcompLogger.datefmt)
        self.set_fh("audit", fmt, _config)
        self.add_filter(AuditFilter)

        # use value from kwargs in adapter process or the default given here
        instantiation = {
            'beginTimestamp'      : '',
            'statusCode'          : True,
            'responseCode'        : '900',
            'responseDescription' : '',
            'elapsedTime'         : '',
        }
        self.adapter = AuditAdapter(self.logger, instantiation)


# noinspection PyProtectedMember
class AuditFilter(logging.Filter):
    vmName = socket.gethostname()
    vmFqdn = socket.getfqdn()
    responseDecode = {
        'permission'  : 100,
        'availabilty' : 200,  # Availability/Timeouts
        'data'        : 300,
        'schema'      : 400,
        'process'     : 500  # Business process errors
    }                 # 900  # unknown

    def filter(self, record):
        record.beginTimestamp = AuditAdapter._beginTimestamp.strftime(EcompLogger.datefmt + ".%f")[:-3] if AuditAdapter._beginTimestamp else ""
        record.vmName = AuditFilter.vmName
        record.statusCode = "ERROR" if AuditAdapter._statusCode is False else "COMPLETE"
        record.responseCode = AuditFilter.responseDecode.get(AuditAdapter._responseCode, AuditAdapter._responseCode)
        record.responseDescription = AuditAdapter._responseDescription
        record.elapsedTime = AuditAdapter._elapsedTime
        record.server = AuditFilter.vmFqdn
        return True


class AuditAdapter(logging.LoggerAdapter):
    _beginTimestamp = None
    _elapsedTime = None
    _responseDescription = None
    _statusCode = None
    _responseCode = ''

    def process(self, msg, kwargs):
        AuditAdapter._beginTimestamp = kwargs.pop('beginTimestamp', self.extra['beginTimestamp'])
        AuditAdapter._elapsedTime = kwargs.pop('elapsedTime', self.extra['elapsedTime'])
        AuditAdapter._responseCode = kwargs.pop('responseCode', self.extra['responseCode'])
        AuditAdapter._responseDescription = kwargs.pop('responseDescription', self.extra['responseDescription'])
        AuditAdapter._statusCode = kwargs.pop('statusCode', self.extra['statusCode'])
        return msg, kwargs


class Metric(EcompLogger):
    """A detailed view into the processing of a transaction.
    It captures the start and end of calls/interactions with other entities
    """
    fmt = ['beginTimestamp', 'targetEntity', 'asctime', 'requestId', 'XserviceInstanceID', 'XthreadId', 'vmName', 'XserviceName', 'XpartnerName', 'statusCode', 'XresponseCode', 'XresponseDescription', 'XinstanceUUID', 'levelname', 'Xseverity', 'XserverIP', 'elapsedTime', 'server', 'XclientIP', 'XclassName', 'Xunused', 'XprocessKey', 'message', 'XcustomField2', 'XcustomField3', 'XcustomField4', 'XdetailMessage']

    def __init__(self, _config):
        EcompLogger.__init__(self)
        fmt = logging.Formatter(self.format_str(Metric.fmt), EcompLogger.datefmt)
        self.set_fh("metric", fmt, _config)
        self.add_filter(MetricFilter)

        # use value from kwargs in adapter process or the default given here
        instantiation = {
            'beginTimestamp'   : '',
            'targetEntity'     : '',
            'statusCode'       : True,
            'elapsedTime'      : '',
        }
        self.adapter = MetricAdapter(self.logger, instantiation)


# noinspection PyProtectedMember
class MetricFilter(logging.Filter):
    vmName = socket.gethostname()
    vmFqdn = socket.getfqdn()

    def filter(self, record):
        record.beginTimestamp = MetricAdapter._beginTimestamp.strftime(EcompLogger.datefmt + ".%f")[:-3] if MetricAdapter._beginTimestamp else ""
        record.targetEntity = MetricAdapter._targetEntity
        record.vmName = MetricFilter.vmName
        record.statusCode = "ERROR" if MetricAdapter._statusCode is False else "COMPLETE"
        record.elapsedTime = MetricAdapter._elapsedTime
        record.server = MetricFilter.vmFqdn
        return True


class MetricAdapter(logging.LoggerAdapter):
    _beginTimestamp = None
    _elapsedTime = None
    _targetEntity = None
    _statusCode = None

    def process(self, msg, kwargs):
        MetricAdapter._beginTimestamp = kwargs.pop('beginTimestamp', self.extra['beginTimestamp'])
        MetricAdapter._targetEntity = kwargs.pop('targetEntity', self.extra['targetEntity'])
        MetricAdapter._elapsedTime = kwargs.pop('elapsedTime', self.extra['elapsedTime'])
        MetricAdapter._statusCode = kwargs.pop('statusCode', self.extra['statusCode'])
        return msg, kwargs


class Error(EcompLogger):
    """capture info, warn, error and fatal conditions"""
    fmt = ['asctime', 'requestId', 'XthreadId', 'XserviceName', 'XpartnerName', 'targetEntity', 'targetServiceName', 'levelname', 'errorCode', 'errorDescription', 'filename)s:%(lineno)s - %(message']

    def __init__(self, _config, logdebug):
        EcompLogger.__init__(self)
        fmt = logging.Formatter(self.format_str(Error.fmt) + '^', EcompLogger.datefmt)
        self.set_fh("error", fmt, _config, lvl=logging.WARN)
        # add my handler to the debug logger
        logdebug.logger.addHandler(self.fh)
        self.add_filter(ErrorFilter)


# noinspection PyProtectedMember
class ErrorFilter(logging.Filter):
    errorDecode = {
        'permission'  : 100,
        'availabilty' : 200,  # Availability/Timeouts
        'data'        : 300,
        'schema'      : 400,
        'process'     : 500  # Business process errors
    }                 # 900  # unknown

    def filter(self, record):
        record.targetEntity = DebugAdapter._targetEntity
        record.targetServiceName = DebugAdapter._targetServiceName
        record.errorCode = ErrorFilter.errorDecode.get(DebugAdapter._errorCode, DebugAdapter._errorCode)
        record.errorDescription = DebugAdapter._errorDescription
        return True


class Debug(EcompLogger):
    """capture whatever data may be needed to debug and correct abnormal conditions"""
    fmt = ['asctime', 'requestId', 'levelname', 'filename)s:%(lineno)s - %(message']

    # use value from kwargs in adapter process or the default given here
    instantiation = {
        'targetEntity'      : '',
        'targetServiceName' : '',
        'errorCode'         : '900',
        'errorDescription'  : ''
    }

    def __init__(self, _config):
        EcompLogger.__init__(self)
        fmt = logging.Formatter(self.format_str(Debug.fmt) + '^', EcompLogger.datefmt)
        self.set_fh("debug", fmt, _config, lvl=logging.DEBUG)

        self.adapter = DebugAdapter(self.logger, Debug.instantiation)


class DebugAdapter(logging.LoggerAdapter):
    _targetEntity = ''
    _targetServiceName = ''
    _errorCode = ''
    _errorDescription = ''

    def process(self, msg, kwargs):
        DebugAdapter._targetEntity = kwargs.pop('targetEntity', self.extra['targetEntity'])
        DebugAdapter._targetServiceName = kwargs.pop('targetServiceName', self.extra['targetServiceName'])
        DebugAdapter._errorCode = kwargs.pop('errorCode', self.extra['errorCode'])
        DebugAdapter._errorDescription = kwargs.pop('errorDescription', self.extra['errorDescription'])
        return msg, kwargs


class Console(EcompLogger):
    """ set logger to point to stderr."""
    fmt = ['asctime', 'levelname', 'filename)s:%(lineno)s - %(message']

    def __init__(self, logdebug=None):
        EcompLogger.__init__(self)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        fmt = logging.Formatter(self.format_str(Console.fmt, sep="  "), EcompLogger.datefmt)
        ch.setFormatter(fmt)

        # console can be written to when Debug is, or...
        if logdebug is not None:
            logdebug.logger.addHandler(ch)
            return

        # ...console is written to as a stand alone (ex. for tools using valet libs)
        self.logger = logging.getLogger('console')
        self.adapter = DebugAdapter(self.logger, Debug.instantiation)
        self.logger.addHandler(ch)
        ch.addFilter(LoggerFilter())


def every_log(name):
    log = Logger.get_logger(name)
    log.info("so this happened")
    log.debug("check out what happened")
    log.warning("something bad happened")
    log.error("something bad happened to me")


""" MAIN """
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test Logging', add_help=False)  # <<<2
    parser.add_argument('-pc', action='store_true', help='where to write log files')
    parser.add_argument("-?", "--help", action="help", help="show this help message and exit")
    opts = parser.parse_args()

    path = "/opt/pc/" if opts.pc else "/tmp/"
    config = json.loads('{ "path": "' + path + '" }')

    now = datetime.now()
    then = now.replace(hour=now.hour + 1)
    differ = now - then

    # write to console
    logger = Logger().get_logger('console')
    logger.info('Log files are written to ' + path)
    Logger.logs = None  # this reset is only needed cuz of console test, never for prod

    # create all loggers and save an instance of debug logger
    logger = Logger(config, console=True).get_logger('debug')

    metric = Logger.get_logger('metric')
    metric.info('METRIC STUFF')
    metric = Logger.get_logger('metric')
    Logger.set_req_id('1235-123-1234-1234')
    metric.info(' -- METRIC NOW THEN  -- ', beginTimestamp=then, elapsedTime=differ, statusCode=False)
    every_log('metric')
    every_log('debug')
    Logger.get_logger('audit').info('AUDIT STUFF', responseCode=100, responseDescription="you shoulda seen it", elapsedTime=differ, statusCode=False, beginTimestamp=now)
    every_log('audit')
    logger.error("--------------------------------")
    logger.error('EC:100 TE:OS', errorCode='100', targetEntity='target entity')
    logger.error('EC:schema TSN:IDK', errorCode='schema', targetServiceName='target service name')
    logger.error('EC:393 ED:bt', errorCode='393', errorDescription='this is an error')
    logger.error("--------------------------------")
    try:
        assert False  # ("Now test logging an exception")
    except AssertionError:
        logger.exception('This is a log of an exception', errorDescription='EXMAN')
