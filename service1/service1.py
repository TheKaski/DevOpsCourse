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

# Set up logging
logging.basicConfig(level=logging.INFO)

# Service 1 should keep record of the STATE

state = "INIT"

# Define basic HTTPRequestHandler:
class HTTPRequestHandler(BaseHTTPRequestHandler):
    # Create endpoint for GET request:
    def do_GET(self):
        if self.path == "/shutdown":
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

            # Write the state data as plain text to the response body
            self.wfile.write(state.encode())  # Encode to bytes as required by `wfile`

            return
        
        # Main endpoint for the excercise data retrieval: 
        if self.path == "/request":
            logging.info("I RECEIVED A API REQUEST FOR CURRENT SERVICE INFO")
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

# Start the server:
if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 5050), HTTPRequestHandler)
    logging.info('Starting httpd...\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
    logging.info('Stopping httpd...\n')