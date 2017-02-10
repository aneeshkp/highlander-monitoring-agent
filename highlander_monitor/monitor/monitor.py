

import abc
import jsonschema
import six


@six.add_metaclass(abc.ABCMeta)
class Monitor(object):
       """ MOnitor Interface"""


       @abc.abstractmethod
       def add_agent_to_registry(self, **kwargs):
           """agent notifies when compute node is down
           :param hostname: computenode hostname"""
           raise NotImplementedError

       @abc.abstractmethod
       def check_agent_status(self, target=None):
            raise NotImplementedError

       @abc.abstractmethod
       def list_all_agents(self):
           raise NotImplementedError

       @abc.abstractmethod
       def list_all_agents_status(self):
           raise NotImplementedError


class MonitorNotificationEndPoint(object):

    @abc.abstractmethod
    def info(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError

    @abc.abstractmethod
    def warn(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError

    @abc.abstractmethod
    def critical(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError






