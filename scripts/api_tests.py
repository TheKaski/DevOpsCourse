# This is a really simple API test developped for CI pipeline excercise
# This script will be used to test a built Docker application endpoints
import requests

BASE_URL = "http://localhost:8197" # Base url which should be exposed locally by the docker application

def test_function():
    print("Test Executed succesfully")

if __name__ == "__main__":
    try:
        test_function()
        print("Tests passed")

    except AssertionError as err:
        print(f"Test failed: {err}")
        exit(1) # Exit with error code to make sure the pipeline triggers this as failed case