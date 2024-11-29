#!/bin/bash

# Function to get the current state from the /state endpoint
get_state() {
    local url="http://$DOCKER_HOST_IP:8197/state"
    echo "Getting state from: $url"

    # Execute the curl command to fetch the state
    state=$(curl -s -D- "$url" | tail -n 1)
    echo "Current state: $state"
    echo "$state"
}

# Fetch the initial state
DOCKER_HOST_IP=$(docker network inspect bridge --format '{{range .IPAM.Config}}{{.Gateway}}{{end}}')
echo "DOCKER_HOST_IP: $DOCKER_HOST_IP"

# Get the starting state
current_state=$(get_state)

# Check if the initial state is 'INIT'
if [[ "$current_state" == "INIT" ]]; then
    echo "Initial state is correctly 'INIT'."
else
    echo "Unexpected initial state: $current_state"
    exit 1
fi

echo "Test completed successfully!"