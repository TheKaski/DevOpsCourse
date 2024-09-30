package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os/exec"
	"strings"
)

const port string = ":1234"

// Struct for the data to be sent in json
type Payload struct {
	IPAddress string `json:"ip_address"`
	Processes string `json:"running_processes"`
	DiskSpace string `json:"available_disk_space"`
	Uptime    string `json:"uptime"`
}

// Function for retrieving all the system information:
func RetrieveInformation() Payload {
	// Command to get the IP address
	ipCmd := "hostname -I"
	ip_address, _ := exec.Command("bash", "-c", ipCmd).Output()

	// Command to get running processes (limited)
	processCmd := "ps -ax"
	processes, _ := exec.Command("bash", "-c", processCmd).Output()

	// Command to get available disk space
	diskCmd := "df -h"
	diskSpace, _ := exec.Command("bash", "-c", diskCmd).Output()

	// Command to get system uptime
	uptimeCmd := "uptime -p"
	uptime, _ := exec.Command("bash", "-c", uptimeCmd).Output()

	// Construct and return the Payload struct
	return Payload{
		IPAddress: strings.TrimSpace(string(ip_address)),
		Processes: strings.TrimSpace(string(processes)),
		DiskSpace: strings.TrimSpace(string(diskSpace)),
		Uptime:    strings.TrimSpace(string(uptime)),
	}
}

// Endpoint for sending information:
func GetInfo(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-type", "Application/json")
	payload := RetrieveInformation()   // extract the container details in structed form
	json.NewEncoder(w).Encode(payload) // Send the payload
}

func main() {
	log.Println("Starting service 2 simple http server with new language Golang!")

	// Create only one endpoint for service 2 returning container information
	http.HandleFunc("/info", GetInfo)

	log.Println("Started http server on port: ", port)

	error := http.ListenAndServe(port, nil)
	if error != nil {
		log.Fatal(error)
	}

}
