from oslo.config import cfg

from highlander_monitor import version

launch_opt = cfg.ListOpt(
    'server',
    default=['all'],
    help='Specifies which highlander monitor server to start by the launch script. '
         'Valid options are all or any combination of '
         'monitor and  agent'
)


monitor_opts = [
    cfg.StrOpt('monitor', default='default',
               help='highlander monitor engine'),
    cfg.StrOpt('host', default='0.0.0.0',
               help='Name of the monitor engine node. This can be an opaque '
                    'identifier. It is not necessarily a hostname, '
                    'FQDN, or IP address.'),
    cfg.StrOpt('topic', default='highlander_monitor',
               help='The message topic that the monitor engine listens on.'),
    cfg.StrOpt('version', default='1.0',
               help='The version of the engine.'),
    cfg.StrOpt('notifications', default='highlander_notifications',
               help='The message topic that the monitor engine listens on.')
]

agent_opts = [
    cfg.StrOpt('host', default='0.0.0.0',
               help='Name of the agent node. This can be an opaque '
                    'identifier. It is not necessarily a hostname, '
                    'FQDN, or IP address.'),
    cfg.StrOpt('topic', default='highlander_agent',
               help='The message topic that the agent listens on.'),
    cfg.StrOpt('version', default='1.0',
               help='The version of the agent.'),
    cfg.StrOpt('notifications', default='highlander_notifications',
               help='The message topic that the monitor engine listens on.'),
    cfg.StrOpt('status_report_interval', default='1',
               help='seconds between running periodic tasks.')

]
highlander_notifications_opts=[
    cfg.StrOpt('highlander_notification_topic', default='highlander_notifications', help='higlander notifications ')
]


CONF = cfg.CONF

CONF.register_opts(monitor_opts, group='monitor')

CONF.register_opts(agent_opts, group='agent')

CONF.register_opts(highlander_notifications_opts, group='notifications')

CONF.register_cli_opt(launch_opt)


def parse_args(args=None, usage=None, default_config_files=None):
    CONF(
        args=args,
        project='higlander-mointoring-agent',
        version=version,
        usage=usage,
        default_config_files=default_config_files
    )
