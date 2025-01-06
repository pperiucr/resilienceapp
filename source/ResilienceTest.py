import sys
import os
import zmq
import json


# Define the Operator class
class Operator:
    def __init__(self, BW, delay, packet_loss, name):
        self.name = name # Name of the operator
        self.BW = BW  # Bandwidth in Mbps
        self.delay = delay  # Delay in milliseconds
        self.packet_loss = packet_loss  # Packet loss rate %ge
    def to_dict(self):
        return {
            "name": self.name,
            "BW": self.BW,
            "delay": self.delay,
            "packet_loss": self.packet_loss,
        }
    def __repr__(self):
        # Custom string representation to easily print the operator's details
        return f"Operator(IP: {self.name}, BW: {self.BW}, Delay: {self.delay}ms, Loss: {self.packet_loss}%)"

def main():
    # Check if the number of arguments is between 1 and 6 (including the script name)
    if len(sys.argv) < 3 or len(sys.argv) > 8:
        print("Please provide between 3 and 10 numbers. 1: required BW, 2: resiliancy level and Others are operator BWs")
        return

    # Parse the input arguments
    try:
        min_bandwidth = int(sys.argv[1])  # second arg required BW
        res_level = int(sys.argv[2]) # third resiliancy level
        remaining_numbers = [int(arg) for arg in sys.argv[3:]]  # Remaining numbers
    except ValueError:
        print("All inputs must be valid integers.")
        return

    # Create a list of Number objects based on the inputs
    #operators = [Operator(BW=num, delay=num/10, packet_loss=num/100, name="Operator"+str(num)) for num in remaining_numbers]

    # Define the request data
    request_data = {
        "operators":[Operator(name="Operator"+str(num), BW=num, delay=0.0, packet_loss=0.0).to_dict() for num in remaining_numbers],
        "required_bandwidth": min_bandwidth,
        "resiliency_level": res_level
    }

    # Print the list of created Number objects
    print(f"Created Request: {request_data}")
    # Set up ZeroMQ REQ socket
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    #port = 5555
    #socket.connect(f"tcp://localhost:{port}")  # Ensure this matches the server's address and port
    socket.connect("tcp://localhost:5555")  # Ensure this matches the server's address and port
    # Send the request
    print("Sending request to server ...")
    socket.send_json(request_data)

    # Receive the response
    response = socket.recv_json()
    print("Response received:")
    print(json.dumps(response, indent=4))

if __name__ == "__main__":
    main()
