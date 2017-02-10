# Copyright 2015 - aputtur, Inc.
#
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import sys
import eventlet
eventlet.monkey_patch(
    os=True,
    select=True,
    socket=True,
    thread=False if '--use-debugger' in sys.argv else True,
    time=True)

import copy
import traceback
import time, threading
import socket
import json
from oslo import messaging
from highlander_monitor.agent import agent
import threading
import logging

logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)

class DefaultAgent(agent.Agent):
    def __init__(self, monitor_client, monitor_notifier):
        self._monitor_client = monitor_client
        self._MONITORING_STATE = None
        self._hostname = socket.gethostname()
        self._hostaddress = socket.getfqdn()
        self._monitor_notifier = monitor_notifier
        """.prepare(publisher_id=self._hostaddress)"""

    def run_status_notification(self):
        logging.info("Logging")
        threading.Thread(target=self._run_status_notification())

    def _run_status_notification(self):
        while True:
            logging.info('running notification status by agent')
            kwargs = {'hostname': self._hostname, 'hostaddress': self._hostaddress, 'status': 'up'}
            ctx = {}
            self._monitor_notifier.info(ctx, 'status_update', kwargs)
            logging.info('sleep one sec')
            time.sleep(0.001)

    def report_heartbeat(self):
        return 'up'

    def register_with_monitor(self):
        logging.info('calling registering')
        kwargs = {'hostname': self._hostname,
                  'hostaddress': self._hostaddress}
        self._monitor_client.add_agent_to_registry(**kwargs)
        self.run_status_notification()


class DefaultAgentNotificationEndPoint(object):
    """filter_rule=NotificationFilter()"""
    def info(self, ctx, publisher_id, event_type, payload, metadata):
        logging.info("Inside info notification endpoint -AGENT")
        print('*********Agent received Notification=Start********')
        print json.dumps(payload, indent=4)
        print(json.dumps(metadata, indent=4))
        print('*********Agent received Notification=End********')
        return messaging.NotificationResult.HANDLED

    def warn(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError

    def critical(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError
