import sys
from oslo.config import cfg
from highlander_monitor import config
import highlander_monitor.rpc as rpc
import logging
import os

logging.basicConfig(format='%(asctime)s:%(message)s', level=logging.DEBUG)

# If ../highlander_monitor/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
POSSIBLE_TOPDIR = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
if os.path.exists(os.path.join(POSSIBLE_TOPDIR, 'highlander_monitor', '__init__.py')):
    sys.path.insert(0, POSSIBLE_TOPDIR)


def register_agent():
    rpc.get_agentclient().register_with_monitor(cfg.CONF.agent.host)


def main():
    try:
        config.parse_args()
        print cfg.CONF
        register_agent()

    except RuntimeError as excp:
        sys.stderr.write("ERROR: %s\n" % excp)
        sys.exit(1)


if __name__ == '__main__':
    main()

