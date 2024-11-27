# This is a really simple API test developped for CI pipeline excercise
# This script will be used to test a built Docker application endpoints
import requests

# Define the baseUrl of the service under testing
BASE_URL = "http://localhost:8197" # Base url which should be exposed locally by the docker application

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
        return "PAGE_NOT_FOUND"
    assert response.status_code == 200, f"Failed to get state: {response.text}"
    return response.text.strip()

# Function for sending a GET/request to get information about the services
def get_request():
    """Trigger the request endpoint."""
    response = requests.get(f"{BASE_URL}/request")
    assert response.status_code == 200, f"Failed to send request: {response.text}"
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

def test_initial_state_request():
    """Test retrieving the state from the REST API"""
    assert get_state() == "INIT", "System should return the INIT state as original state"


#The main loop of this test program
if __name__ == "__main__":
    try:
        print("Running the tests now...")
        test_initial_state_request()
        print("All tests passed!")
    # If any of the tests asser an error, the test will fail and report the error    
    except AssertionError as err:
        print(f"Test failed: {err}")
        exit(1) # Exit with error code to make sure the pipeline triggers this as failed case