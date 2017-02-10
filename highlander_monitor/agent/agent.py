import abc
import six


@six.add_metaclass(abc.ABCMeta)
class Agent(object):
    """ MOnitor Interface"""

    @abc.abstractmethod
    def run_status_notification(self):
        """
           :param target:
           :return:
           """
        raise NotImplementedError

    @abc.abstractmethod
    def report_heartbeat(self):
        """
           :param target:
           :return:
           """
        raise NotImplementedError

    @abc.abstractmethod
    def register_with_monitor(self):
        """
           :param target:
           :param async:
           :return:
           """
        raise NotImplementedError


class AgentNotificationEndPoint(object):
    @abc.abstractmethod
    def info(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError

    @abc.abstractmethod
    def warn(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError

    @abc.abstractmethod
    def critical(self, ctx, publisher_id, event_type, payload, metadata):
        raise NotImplementedError
