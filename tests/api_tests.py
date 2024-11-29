# This is a really simple API test developped for CI pipeline excercise
# This script will be used to test a built Docker application endpoints
import os
import subprocess

# Define the baseUrl of the service under testing
host = os.getenv('DOCKER_HOST_IP', '127.0.0.1')  # Default to '127.0.0.1' if the environment variable is not set
BASE_URL =  f"http://{host}:8197"

# Define a simple inline class for stroing the test results of this DIY test script
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failures = []

    def add_pass(self):
        self.passed += 1

    def add_fail(self, test_name, error_message):
        self.failed += 1
        self.failures.append((test_name, error_message))

    # Function for printing the summary after tests have been completed
    def summary(self):
        print("\nTest Summary:")
        print(f"Total tests run: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.failed > 0:
            print("\nFailed Tests:")
            for test_name, error_message in self.failures:
                print(f"- {test_name}: {error_message}")

# Function for sending the PUT/state request with the state as payload
def set_state(state):
    """Set the system state using the PUT /state endpoint."""
    try:
         # Use curl to make the PUT request
         result = subprocess.run(
             [
                 "curl",
                 "-X", "PUT",  # Specify the HTTP method
                 f"{BASE_URL}/state",  # Target URL
                 "-d", state  # Data payload
             ],
             capture_output=True,  # Capture the output
             text=True,  # Get the output as text
         )

         # Check if the HTTP request was successful
         if result.returncode != 0:
             raise RuntimeError(f"Curl command failed: {result.stderr}")

         if "200 OK" not in result.stdout:
             raise AssertionError(f"Failed to set state to {state}: {result.stdout}")

         print(f"State set successfully: {state}")

    except Exception as e:
         raise RuntimeError(f"Error setting state: {str(e)}")

# Makes a Get request to the /state endpoint and returns the output
def get_state():
    """Get the current state using the GET /state endpoint."""
    try:
        # Execute curl command to get both headers and body
        result = subprocess.run(
            ["curl", "-s", f"{BASE_URL}/state"],  # -s for silent mode, -D- for headers
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check for errors in the subprocess call
        if result.returncode != 0:
            raise AssertionError(f"Curl command failed: {result.stderr.strip()}")

        return result.stdout

    except Exception as e:
        raise AssertionError(f"Error occurred while getting state: {e}")

def get_request():
    """Trigger the request endpoint and validate Content-Type and status with curl."""
    try:
        # Execute curl command with headers, capture both the headers and body
        result = subprocess.run(
            [
                "curl", "-s", f"{BASE_URL}/request",
                "-H", "Content-Type: text/plain", "-H", "Accept: text/plain"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Check for errors in the subprocess call
        if result.returncode != 0:
            raise AssertionError(f"Curl command failed: {result.stderr.strip()}")
        # Return the response body
        return result.stdout

    except Exception as e:
        raise AssertionError(f"Error occurred while sending request: {e}")
# DEFINE THE TEST CASES HERE THAT CAN USE THE ENDPOINT FUNCTIONS DECRIBED ABOVE

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
    results = TestResult()

    # Define the tests here
    tests = [
        ("test_state_should_equal_to_INIT", lambda: test_state_should_equal_to("INIT")),
        ("test_request_endpoint", test_request_endpoint),
    ]

    print(f"Running the tests now... the URL is {BASE_URL}")

    # Run each test so that you print the test clause and then run the function, and then add a pass or fail based on errors thrown
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"{test_name} passed.")
            results.add_pass()
        except AssertionError as err:
            print(f"{test_name} failed: {err}")
            results.add_fail(test_name, str(err))
        except Exception as ex:
            print(f"{test_name} encountered an unexpected error: {ex}")
            results.add_fail(test_name, f"Unexpected error: {ex}")

    # Print summary
    results.summary()

    # Exit with error code if any test failed
    if results.failed > 0:
        exit(1)