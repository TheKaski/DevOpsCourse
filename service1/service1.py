# This file contains implementation for basic http API using Python
import json
import docker
import logging
import socket
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import os
from datetime import datetime
# Set up logging
logging.basicConfig(level=logging.INFO)


# Share the state with other service 1 replicas
SYNCSTATEFILE = "/sync/state.txt"
SYNCLOGFILE = "/sync/log.txt"

requireReLoginForStateChange = False

# Define basic HTTPRequestHandler:
class HTTPRequestHandler(BaseHTTPRequestHandler):
    # Create endpoint for GET request:
    def do_GET(self):
        if self.path == "/shutdown":
            current_state = readSyncState()
            timestamp = datetime.now()
            writeSyncLog(f"${timestamp}: {current_state} -> {'SHUTDOWN'}")
            self.send_response(200)
            self.end_headers()
            self.shutdown_all_containers()
            return
        # Additional endpoint for retrieving "real time" data stream
        if self.path == "/realtime":
            # Send the response
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()
            while True:
                # Extract information about local system
                informationDump = self.get_system_info()
                # Retrieve service2 information
                service2Information = self.get_Service_Information()
                response = [informationDump, service2Information]
                self.wfile.write(f"data: {json.dumps(response)}\n\n".encode())
                self.wfile.flush()  # Ensure the data is sent immediately
                time.sleep(2)  # Adjust the interval as needed
                
        # Main endpoint for the excercise data retrieval: 
        if self.path == "/":
            # Send the response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            # Extract information about local system
            informationDump = self.get_system_info()
            # Retrieve service2 information
            service2Information = self.get_Service_Information()
            response = [informationDump, service2Information]
            self.wfile.write(json.dumps(response).encode())
            return

        # Experimental GUI consuming the realtime data stream:
        if self.path =="/gui":
             # Serve the HTML file
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            with open("testi.html", "r") as f:
                self.wfile.write(f.read().encode())
            return
        
        # NEW Feature of returning the STATE variable when asked:
        if self.path =="/state":
            logging.info("I RECEIVED A API REQUEST FOR CURRENT STATE")
            # Serve the HTML file
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()

            current_state = readSyncState()
            # Write the state data as plain text to the response body
            self.wfile.write(current_state.encode())  # Encode to bytes as required by `wfile`

            return
        
        # Main endpoint for the excercise data retrieval: 
        if self.path == "/request":
            logging.info("I RECEIVED A API REQUEST FOR CURRENT SERVICE INFO")
            # Do not respond when PAUSED state is ative state
            if readSyncState() == 'PAUSED':
                 return
            # Send the response
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")  # Set content type to plain text
            self.end_headers()

            # Extract information about the local system
            informationDump = self.get_system_info()
            # Retrieve service2 information
            service2Information = self.get_Service_Information()

            # Prepare the response to be in plain text format (string)
            # Convert both information dumps to a human-readable string
            response_str = f"service1 Information:\n{informationDump}\n\nservice2 Information:\n{service2Information}"

            # Encode the string into bytes before sending
            self.wfile.write(response_str.encode())
            self.wfile.flush() 
            return
        
        # NEW Feature of returning the STATE variable when asked:
        if self.path =="/run-log":
            logging.info("I RECEIVED A API REQUEST FOR RUNLOG STATE")
            # Serve the HTML file
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()

            current_log = readSyncLog()
            # Write the state data as plain text to the response body
            self.wfile.write(current_log.encode())  # Encode to bytes as required by `wfile`
            return

        # Anything else will result in 404     
        self.send_response(404)
        self.end_headers()


    # Create endpoint for PUT requests mainyl just PUT/state
    def do_PUT(self):

         # Main endpoint for the excercise data retrieval: 
        if self.path == "/state":
            try:
                content_length = int(self.headers.get('Content-Length', 0))  # Get the length of the payload
                payload = self.rfile.read(content_length).decode('utf-8')  # Read and decode the payload

                # Log the payload for debugging purposes
                logging.info(f"Received payload: {payload}")
                auth_header = self.headers.get('Authorization')

                # Get the current timestamp
                timestamp = datetime.now()
                current_state = readSyncState()
                
                logging.info(f"Authorization header: {auth_header}")

                # Check if transitioning to INIT state
                if payload == "INIT":
                    writeSyncState("INIT")  # Update state to INIT
                    writeSyncLog(f"${timestamp}: {current_state} -> {payload}")
                    logging.info("System state changed to INIT.")

                    # Respond with a custom header to trigger re-authentication
                    self.send_response(401)  # Or 200 with a custom header
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("X-Reauthenticate", "true")  # Custom header for Nginx
                    self.end_headers()
                    self.wfile.write(f"{payload}".encode())
                    self.wfile.write("State changed to INIT. Reauthentication required.".encode())
                    return

                # Check if the current state is INIT and no Authorization header is provided
                if current_state == "INIT" and not auth_header:
                    logging.info("Unauthorized attempt to modify state while in INIT.")
                    self.send_response(403)  # Forbidden
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write("Forbidden: Authorization required to modify state from INIT.".encode())
                    return

                # When the payload is received the program will change the state and log the state change in the run-log
                writeSyncLog(f"${timestamp}: {current_state} -> {payload}")
                writeSyncState(payload)
 
                # Respond to the request
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")  # Set content type to plain text
                self.end_headers()
                self.wfile.write(f"{payload}".encode())  # Echo back the payload for testing
            except Exception as e:
                logging.error(f"Error processing PUT request: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write("Internal Server Error".encode())
            return
        # Anything else will result in 404     
        self.send_response(404)
        self.end_headers()

    def get_Service_Information(self):
        logging.info("Asking service 2 information")
        response = requests.get('http://service2:1234/info') # Ask for service 2 status

        logging.info(f"Got a response: {response.text} ")

        return {
            "service2": response.json()
        }
    
    def get_system_info(self):
        # Get host name
        hostname = socket.gethostname()
       
        # Retrieve IP of this host:
        ip_address = socket.gethostbyname(hostname)

        # Get running processes
        processes = subprocess.run('ps -ax', shell=True, text=True, capture_output=True)

        # Get available disk space
        disk_usage = subprocess.run('df -h', shell=True, text=True, capture_output=True)
        #available_space = disk_usage.split()[3]  # Get available space from output

        # Get time since last boot
        uptime = subprocess.run('uptime -p', shell=True, text=True, capture_output=True)

        # Compile the information
        info = {
            "service1": {
                "ip_address": ip_address,
                "running_processes": processes.stdout,
                "available_disk_space": disk_usage.stdout,
                "uptime": uptime.stdout
            }
        }
        
        return info    
    
    def shutdown_all_containers(self):
        client = docker.from_env()
        currentContainer = client.containers.get(os.getenv('HOSTNAME'))
        currentID = currentContainer.id
        logging.info("I am" , currentID)
        try:
            for container in client.containers.list():
                logging.info("Shutting down service" , container.id)
                if container.id != currentID:
                    container.stop()
            currentContainer.stop()
        except Exception as e:
            logging.error(f"Error stopping the containers: {e}")

# Function for reading the state from synced state file
def readSyncState():
    if not os.path.exists(SYNCSTATEFILE):
            return "INIT"  # Default state
    with open(SYNCSTATEFILE, "r") as f:
            return f.read().strip() # JUst read the file

# Function for reading the contents of synced log file
def readSyncLog():
    if not os.path.exists(SYNCLOGFILE):
            return "This log is empty"  # Default log
    with open(SYNCLOGFILE, "r") as f:
            return f.read().strip() # Just read the file

# Function for writing new state to the synced state file
def writeSyncState(state):
     with open(SYNCSTATEFILE, "w") as f:
            f.write(state)

# Function for appending new log entry to the synced log file
def writeSyncLog(logEntry):
     with open(SYNCLOGFILE, "a") as f:
            f.write(logEntry + '\n')

def run():
    logging.basicConfig(level=logging.INFO)
    server_address = ('0.0.0.0', 5050)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    logging.info('Starting server...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()