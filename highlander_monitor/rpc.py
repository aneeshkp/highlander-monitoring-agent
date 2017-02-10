from oslo.config import cfg
from oslo import messaging
from oslo_messaging.rpc import client
import oslo_messaging
from highlander_monitor.monitor import monitor as base_monitor
from highlander_monitor.agent import agent as base_agent
from highlander_monitor.monitor import default_monitor as def_monitor
from highlander_monitor.agent import default_agent as def_agent
import time
import random
import socket

_TRANSPORT = None
_NOTIFICATION_TRANSPORT = None

_MONITOR_CLIENT = None
_AGENT_CLIENT = None
_MONITOR_LISTENER = None
_AGENT_LISTENER = None


def cleanup():
    """Intended to be used by tests to recreate all RPC related objects."""

    global _TRANSPORT
    global _MONITOR_CLIENT
    global _AGENT_CLIENT
    global _MONITOR_LISTENER
    global _AGENT_LISTENER
    global _NOTIFICATION_TRANSPORT

    _TRANSPORT = None
    _MONITOR_CLIENT = None
    _AGENT_CLIENT = None
    _MONITOR_LISTENER = None
    _AGENT_LISTENER = None
    _NOTIFICATION_TRANSPORT = None


def get_transport():
    global _TRANSPORT

    if not _TRANSPORT:
        _TRANSPORT = messaging.get_transport(cfg.CONF)

    return _TRANSPORT


def get_monitorclient():
    global _MONITOR_CLIENT

    if not _MONITOR_CLIENT:
        _MONITOR_CLIENT = MonitorClient(get_transport())

    return _MONITOR_CLIENT


def get_monitorlistner():
    global _MONITOR_LISTENER

    if not _MONITOR_LISTENER:
        targets = [messaging.Target(topic=cfg.CONF.monitor.notifications)]
        endpoints = [def_monitor.DefaultMonitorNotificationEndPoint('defualt_monitor')]
        _MONITOR_LISTENER = messaging.get_notification_listener(get_transport(), targets, endpoints,
                                                                executor='eventlet')

    return _MONITOR_LISTENER


def get_agentlistner():
    global _AGENT_LISTENER

    if not _AGENT_LISTENER:
        targets = [messaging.Target(topic=cfg.CONF.agent.notifications)]
        endpoints = [def_agent.DefaultAgentNotificationEndPoint()]
        _AGENT_LISTENER = messaging.get_notification_listener(get_transport(), targets, endpoints, executor='eventlet')

    return _AGENT_LISTENER


def get_agentclient():
    global _AGENT_CLIENT

    if not _AGENT_CLIENT:
        _AGENT_CLIENT = AgentClient(get_transport())

    return _AGENT_CLIENT


class MonitorClient(base_monitor.Monitor):
    """RPC Monitor client."""

    def __init__(self, transport):
        self._ctx = {}
        self._topic = cfg.CONF.monitor.topic
        self._client = messaging.RPCClient(
            transport,
            messaging.Target(topic=self._topic)
        )

    def notify_down(self, **kwargs):
        ctx = {}
        self._client.call(ctx, 'notify_down', **kwargs)

    def add_agent_to_registry(self, **kwargs):
        print'monitor'
        call_ctx = self._client.prepare()
        rpc_client_method = call_ctx.cast
        rpc_client_method(self._ctx, 'add_agent_to_registry', **kwargs)

    def check_agent_status(self, **kwargs):
        ctx = {}
        self._client.cast(ctx, 'check_agent_status', **kwargs)

    def list_all_agents(self):
        raise NotImplementedError

    def list_all_agents_status(self):
        raise NotImplementedError


class MonitorServer(object):
    def __init__(self, defaultMonitorServer):
        self._defaultMonitorServer = defaultMonitorServer

    def notify_down(self, **kwargs):
        self._defaultMonitorServer.notify_down(**kwargs)

    def add_agent_to_registry(self, **kwargs):
        print 'coming here'
        self._defaultMonitorServer.add_agent_to_registry(**kwargs)

    def check_agent_status(self, **kwargs):
        return self._defaultMonitorServer.check_agent_status(**kwargs)


class AgentServer(object):
    def __init__(self, defaultagent):
        self._defaultagent = defaultagent

    def run_status_notification2(self, *args):
        self._defaultagent.run_status_notification()

    def report_heartbeat(self):
        self._defaultagent.report_heartbeat()

    def register_with_monitor2(self, *args):
        self._defaultagent.register_with_monitor()


class AgentClient(object):
    """RPC Monitor client."""

    def __init__(self, transport):
        self._topic = cfg.CONF.agent.topic
        self._client = messaging.RPCClient(
            transport,
            messaging.Target(topic=self._topic)
        )

    def run_status_notification(self, target=None):
        ctx = {}
        call_ctx = self._client.prepare(topic=self._topic, server=target)
        rpc_client_method = call_ctx.call
        """call_ctx.cast if async else call_ctx.call"""
        print'why here'
        rpc_client_method(ctx, 'run_status_notification2')

    def report_heartbeat(self, target=None):
        ctx = {}
        call_ctx = self._client.prepare(topic=self._topic, server=target)
        rpc_client_method = call_ctx.call
        return rpc_client_method(ctx, 'report_heartbeat')

    def register_with_monitor(self, target=None):
        ctx = {}
        call_ctx = self._client.prepare(topic=self._topic, server=target, fanout=True)
        rpc_client_method = call_ctx.cast
        """if async else call_ctx.call"""
        rpc_client_method(ctx, 'register_with_monitor2')
        rpc_client_method(ctx, 'run_status_notification2')

