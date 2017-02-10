# 70-highlander-monitoring-agent.sh - DevStack extras script to install highlander-monitoring-agent

if is_service_enabled highlander-monitoring-agent; then
    if [[ "$1" == "source" ]]; then
        # Initial source
        source $TOP_DIR/lib/highlander-monitoring-agent
    elif [[ "$1" == "stack" && "$2" == "install" ]]; then
        echo_summary "Installing highlander-monitoring-agent"
        install_highlander-monitoring-agent
    elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
        echo_summary "Configuring highlander-monitoring-agent"
        configure_highlander-monitoring-agent
    elif [[ "$1" == "stack" && "$2" == "extra" ]]; then
        echo_summary "Initializing highlander-monitoring-agent"
        init_highlander-monitoring-agent
        start_highlander-monitoring-agent
    fi

    if [[ "$1" == "unstack" ]]; then
        stop_highlander-monitoring-agent
    fi
fi
