# This is a really simple API test developped for CI pipeline excercise
# This script will be used to test a built Docker application endpoints
import requests
import os

# Define the baseUrl of the service under testing
host = os.getenv('DOCKER_HOST_IP', '127.0.0.1')  # Default to '127.0.0.1' if the environment variable is not set
BASE_URL =  f"http://{host}:8197"

# Function for sending the PUT/state request with the state as payload
def set_state(state):
    """Set the system state using the PUT /state endpoint."""
    response = requests.put(f"{BASE_URL}/state", data=state)
    assert response.status_code == 200, f"Failed to set state to {state}: {response.text}"

# Function for sending a GET/state request to read the current state value
def get_state():
    """Get the current state using the GET /state endpoint."""
    response = requests.get(f"{BASE_URL}/state")
    if response.status_code == 404:
        return f"PAGE_NOT_FOUND {BASE_URL}/state"
    assert response.status_code == 200, f"Failed to get state from {BASE_URL}/state: {response.text}"
    return response.text.strip()

# Function for sending a GET/request to get information about the services
def get_request():
    """Trigger the request endpoint."""
    response = requests.get(f"{BASE_URL}/request")
    assert response.status_code == 200, f"Failed to send request: {response.text}"
    # Check if the Content-Type is 'text/plain'
    content_type = response.headers.get('Content-Type')
    assert 'text/plain' in content_type, f"Expected 'text/plain', but got {content_type}"
    return response.text.strip()

# function for sending a GET/run-log get log of the system states in text form
def get_run_log():
    """Retrieve the run log using the GET /run-log endpoint."""
    response = requests.get(f"{BASE_URL}/run-log")
    assert response.status_code == 200, f"Failed to get run log: {response.text}"
    return response.text.strip()

# The test for setting the state to INIT and seeing wheter the state has been changed correctly
def test_init_state():
    """Test the INIT state."""
    set_state("INIT")
    assert get_state() == "INIT", "State should be INIT after setting it"

# The test for setting the state to PAUSED and seeing wheter the state has been changed correctly
def test_paused_state():
    """Test the PAUSED state."""
    set_state("PAUSED")
    assert get_state() == "PAUSED", "State should be PAUSED after setting it"

# The test for setting the state to RUNNING and seeing wheter the state has been changed correctly
def test_running_state():
    """Test the RUNNING state."""
    set_state("RUNNING")
    assert get_state() == "RUNNING", "State should be RUNNING after setting it"

# The test for setting the state to SHUTDOWN and seeing wheter the state has been changed correctly
def test_shutdown_state():
    """Test the SHUTDOWN state."""
    set_state("SHUTDOWN")
    assert get_state() == "PAGE_NOT_FOUND", "system should be completely offline after shutting down"


def test_state_should_equal_to(expected):
    """Test retrieving the state from the REST API"""
    output = get_state()
    assert output == expected, f"System should return the {expected} state as original state Instead was {output}"
    print("State test passed")

def test_request_endpoint():
    """Test retrieving the information of services from the REST API"""
    output = get_request()
     # Check if the output contains both 'service1' and 'service2' in the plain text
    assert "service1" in output, f"System should return state including 'service1', instead got: {output}"
    assert "service2" in output, f"System should return state including 'service2', instead got: {output}"
    print("Request test passed")


#The main loop of this test program
if __name__ == "__main__":
    try:
        print(f"Running the tests now... the url is {BASE_URL}")
        test_state_should_equal_to("INIT")
        test_request_endpoint()
        print("All tests passed!")
    # If any of the tests asser an error, the test will fail and report the error    
    except AssertionError as err:
        print(f"Test failed: {err}")
        exit(1) # Exit with error code to make sure the pipeline triggers this as failed case