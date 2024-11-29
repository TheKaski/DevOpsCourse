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

# Function for sending a GET /state request to read the current state value
def get_state():
    """Get the current state using the GET /state endpoint."""
    try:
        # Execute curl command to get both headers and body
        result = subprocess.run(
            ["curl", "-s", "-D-", f"{BASE_URL}/state"],  # Include -D to separate headers
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Split the response into headers and body using a double newline as the separator
        headers, body = result.stdout.split("\r\n\r\n", 1)  # Headers and body are separated by "\r\n\r\n"

        # Get status code from headers (first line)
        status_code = headers.split()[1]  # Status code is the second element in the first header line
        
        if status_code == "404":
            return f"PAGE_NOT_FOUND {BASE_URL}/state"
        
        # Ensure status code is 200
        assert status_code == "200", f"Failed to get state from {BASE_URL}/state: {body}"

        # Optionally check the content type header if needed
        content_type = next((line.split(":")[1].strip() for line in headers.splitlines() if "Content-Type" in line), None)
        assert content_type == "text/plain", f"Expected 'text/plain' content type, but got {content_type}"

        return body.strip()
    
    except Exception as e:
        raise AssertionError(f"Error occurred while getting state: {e}")

def get_request():
    """Trigger the request endpoint and validate Content-Type and status with curl."""
    try:
        # Execute curl command with headers, capture both the headers and body
        result = subprocess.run(
            [
                "curl", "-s", "-w", "%{http_code}", "-D-", f"{BASE_URL}/request",
                "-H", "Content-Type: text/plain", "-H", "Accept: text/plain"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Check for errors in the subprocess call
        if result.returncode != 0:
            raise AssertionError(f"Curl command failed: {result.stderr.strip()}")

        # Separate headers and body + status code
        raw_output = result.stdout.split("\r\n\r\n", 1)
        headers = raw_output[0] if len(raw_output) > 1 else ""
        body_and_status = raw_output[1] if len(raw_output) > 1 else raw_output[0]
        
        # Print raw output for debugging
        print(f"Raw curl output: {result.stdout}")
        
        # Extract status code (last 3 characters of body_and_status)
        status_code = body_and_status[-3:]

        # Extract body (everything except the last 3 characters, which are the status code)
        body = body_and_status[:-3].strip()

        # Verify HTTP status code
        assert status_code == "200", f"Failed to send request: {body}"

        # Parse headers for Content-Type
        content_type = next(
            (line.split(":")[1].strip() for line in headers.splitlines() if "Content-Type" in line), None
        )
        
        # Ensure Content-Type is 'text/plain'
        assert content_type and "text/plain" in content_type, f"Expected 'text/plain', but got {content_type}"

        # Return the response body
        return body

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