#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import logging

logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)
from highlander_monitor import version
import socket
from highlander_monitor import config
import highlander_monitor.rpc as rpc
from oslo import messaging
import highlander_monitor.agent.default_agent as def_agent
import highlander_monitor.monitor.default_monitor as def_monitor
import time
import os

# If ../highlander_monitor/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'highlander_monitor', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)

from oslo.config import cfg
from oslo import messaging


def launch_monitor_listener(transport):
    notification_target = messaging.Target(
        topic=cfg.CONF.monitor.notifications
    )
    monitor_listener = messaging.get_notification_listener(transport, [notification_target],
                                                           [def_monitor.DefaultMonitorNotificationEndPoint(
                                                               'Test-Monitor')])

    monitor_listener.start()
    time.sleep(1)
    monitor_listener.wait()


def launch_monitor(transport):
    print "launching monitor"
    target = messaging.Target(
        topic=cfg.CONF.monitor.topic,
        server=cfg.CONF.monitor.host
    )

    notifier = messaging.Notifier(transport, cfg.CONF.agent.host, driver='messaging',
                                  topic=cfg.CONF.agent.notifications)

    monitor_engine = def_monitor.DefaultMonitor(rpc.get_agentclient(), notifier)

    monitor_endpoints = [rpc.MonitorServer(monitor_engine)]

    monitor_server = messaging.get_rpc_server(
        transport,
        target,
        monitor_endpoints,
        executor='eventlet'
    )

    try:
        monitor_server.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print ("Stopping server")
    monitor_server.stop()
    monitor_server.wait()


def launch_agent_listener(transport):
    notification_target = messaging.Target(
        topic=cfg.CONF.agent.notifications
    )
    agent_listener = messaging.get_notification_listener(transport, [notification_target],
                                                         [def_agent.DefaultAgentNotificationEndPoint()])
    agent_listener.start()
    time.sleep(0)
    agent_listener.wait()


def launch_agent(transport):
    print "launching agent"
    target = messaging.Target(
        topic=cfg.CONF.agent.topic,
        server=cfg.CONF.agent.host
    )

    notifier = messaging.Notifier(transport, cfg.CONF.monitor.host, driver='messaging',
                                  topic=cfg.CONF.monitor.notifications)

    agent_engine = def_agent.DefaultAgent(rpc.get_monitorclient(), notifier)
    agent_endpoints = [rpc.AgentServer(agent_engine)]

    agent_server = messaging.get_rpc_server(
        transport,
        target,
        agent_endpoints,
        executor='eventlet'
    )

    try:
        agent_server.start()
        while True:
            time.sleep(0)
    except KeyboardInterrupt:
        print ("Stopping server")
    agent_server.stop()

    agent_server.wait()


def launch_any(transport, options):
    # Launch the servers on different threads.
    threads = [eventlet.spawn(LAUNCH_OPTIONS[option], transport)
               for option in options]

    print('Server started.')
    [thread.wait() for thread in threads]


# Map cli options to appropriate functions. The cli options are
# registered in highlander monitor 's config.py.
LAUNCH_OPTIONS = {
    'monitor_listener': launch_monitor_listener,
    'agent_listener': launch_agent_listener,
    'monitor': launch_monitor,
    'agent': launch_agent

}
"""'register_agent':register_agent"""
HIGLANDER_MONITOR_TITLE = """
 _    _      _    _              _                          _ _
| |_ (_)__ _| |_ | |__ _ _ _  __| |___ _ _   _ __  ___ _ _ (_) |_ ___ _ _
| ' \| / _` | ' \| / _` | ' \/ _` / -_) '_| | '  \/ _ \ ' \| |  _/ _ \ '_|
|_||_|_\__, |_||_|_\__,_|_||_\__,_\___|_|   |_|_|_\___/_||_|_|\__\___/_|
       |___/

Highlander Monitor Service, version
"""


def print_server_info():
    print(HIGLANDER_MONITOR_TITLE)

    comp_str = ("[%s]" % ','.join(LAUNCH_OPTIONS)
                if cfg.CONF.server == ['all'] else cfg.CONF.server)

    print('Launching monitor components %s...' % comp_str)


def main():
    try:
        config.parse_args()

        print_server_info()
        print cfg.CONF

        # Please refer to the oslo.messaging documentation for transport
        # configuration. The default transport for oslo.messaging is
        # rabbitMQ. The available transport drivers are listed in the
        # setup.cfg file in oslo.messaging under the entry_points section for
        # oslo.messaging.drivers. The transport driver is specified using the
        # rpc_backend option in the default section of the oslo configuration
        # file. The expected value for the rpc_backend is one of the key
        # values available for the oslo.messaging.drivers (i.e. rabbit, fake).
        # There are additional options such as ssl and credential that can be
        # specified depending on the driver.  Please refer to the driver
        # implementation for those additional options. It's important to note

        transport = rpc.get_transport()

        if cfg.CONF.server == ['all']:
            # Launch all servers.
            launch_any(transport, LAUNCH_OPTIONS.keys())

        else:
            # Validate launch option.
            if set(cfg.CONF.server) - set(LAUNCH_OPTIONS.keys()):
                raise Exception('Valid options are all or any combination of '
                                'api, engine, and executor.')

            # Launch distinct set of monitor(s).
            launch_any(transport, set(cfg.CONF.server))


    except RuntimeError as excp:
        sys.stderr.write("ERROR: %s\n" % excp)
        sys.exit(1)


if __name__ == '__main__':
    main()
