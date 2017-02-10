# Copyright 2015 - Aputtur, Inc.
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


import time
import json
import random
from oslo import messaging
from highlander_monitor.monitor import monitor
import logging

logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)


class DefaultMonitor(monitor.Monitor):
    def __init__(self, agent_client, agent_notifier, name=None):
        self._agent_client = agent_client
        self._registered_agents = {}

        if name is None:
            self._name = "Monitor_" + str(random.seed(long(time.time() * 256)))
        else:
            self._name = name
        self._agent_notifier = agent_notifier.prepare(publisher_id=self._name)

    def add_agent_to_registry(self, **kwargs):
        print '************Registering agent in default monitoring *************'
        """
        Calls to start monitoring and report back
        :param hostname:
        :param hostaddress:
        :return:
        """
        ctx = {}
        if kwargs['hostname'] in self._registered_agents:
            logging.info('[Monitor : %s ]  Agent %s is already registered', self._name, kwargs['hostname'])
            return self._agent_notifier.info(ctx, 'Agent_registry_with_monitor', {'Status:Previously registered'})
        else:
            logging.info('[Monitor : %s ]  Agent %s is registered  with hosaddress',
                         self._name, kwargs['hostname'], kwargs['hostaddress'])
            self._registered_agents[kwargs['hostname']] = kwargs['hostaddress']
            print self._registered_agents
            print '************Registering agent in default monitoring *************'
            return self._agent_notifier.info(ctx, 'Agent_registry_with_monitor', {'Status:Newly registered.'})
            """ once registered successfully start monitoring"""
            """self._agent_client.start_mointoring(kwargs['hostaddr'])"""

    def check_agent_status(self, target=None):
        return self.agent_client.report_heartbeat(target)

    def list_all_agents(self):
        raise NotImplementedError

    def list_all_agents_status(self):
        raise NotImplementedError


class DefaultMonitorNotificationEndPoint(object):
    def __init__(self, monitorname):
        self._monitorname = monitorname

    def info(self, ctx, publisher_id, event_type, payload, metadata):
        print('*********MONITOR received Notification=Start********')
        print ('Monitor[ %s ]receiving notification ' % self._monitorname)
        print('event_type %s'% event_type)
        logging.info('publisher_id %s', publisher_id)
        logging.info('payload')
        logging.info(json.dumps(payload, indent=4))
        logging.info('metadata')
        print(json.dumps(metadata, indent=4))
        print('*********MONITOR received Notification=End********')

        return messaging.NotificationResult.HANDLED

    def warn(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError

    def critical(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError
