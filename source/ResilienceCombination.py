import zmq
import json
import os
from itertools import combinations

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

# Function to check if a combination meets the minimum bandwidth requirement
def __meets_bandwidth(combination, min_bandwidth):
    total_bandwidth = sum(operator.BW for operator in combination)
    return total_bandwidth >= min_bandwidth


def __getResiliency(operators, min_BW, resiliency):
    """
    Determine combinations of operators that meet the bandwidth and resiliency requirements.

    Args:
        operators (list): List of dictionaries representing operators with 'name' and 'bandwidth' keys.
        min_bandwidth (int): Minimum bandwidth required by the user.
        resiliency (int): Resiliency level (3 = 'High', 2 = 'Medium', 1 = 'Low').

    Returns:
        list: List of operator combinations that meet the requirements.
    """

    valid_combinations = []

    # Include single operators with BW >= min_BW for Low resiliency
    if resiliency == 1: # Low
        for op in operators:
            if op.BW >= min_BW:
                valid_combinations.append((op,))


    # Generate all combinations of at least 2 operators
    for r in range(2, len(operators) + 1):
        for combo in combinations(operators, r):
            total_BW = sum(op.BW for op in combo)

            if resiliency == 3: #High
                # Each operator in the combination must individually meet the minimum BW
                if all(op.BW >= min_BW for op in combo):
                    valid_combinations.append(combo)

            elif resiliency == 2: #Medium
                # Ensure at least two operators satisfy BW >= min_BW, and one fails
                bw_meeting_criteria = [op for op in combo if op.BW >= min_BW]
                bw_failing_criteria = [op for op in combo if op.BW < min_BW]
                if len(bw_meeting_criteria) >= 2 and len(bw_failing_criteria) >= 1:
                    valid_combinations.append(combo)
                elif len(bw_failing_criteria) >= 2: #incase more than less min_BW
                    for i in range(len(combo)):
                        without_one = total_BW - combo[i].BW
                        if without_one >= min_BW:
                            valid_combinations.append(combo)
                            break  # Once validated, no need to check further

            elif resiliency == 1: #Low
                # Include combinations where all operators have BW < min_BW, but total BW >= min_BW
                if all(op.BW < min_BW for op in combo) and total_BW >= min_BW:
                    valid_combinations.append(combo)
                # Exclude combinations with more than one operator having BW >= min_BW
                elif sum(1 for op in combo if op.BW >= min_BW) == 1:
                    valid_combinations.append(combo)

    return valid_combinations

# Input 1. List of oprators, 2 - required BW as int 3 - Option 3-High/2-Medium/1-Low 
def getCombinations(operators, required_bandwidth, resiliency):

    high_combinations = __getResiliency(operators, required_bandwidth, 3)

    if resiliency == 3:#High
        return high_combinations;

    med_list = __getResiliency(operators, required_bandwidth, 2) #Medium
    medium_combinations = list(set(med_list) | set(high_combinations))

    if resiliency == 2: #Medium
        return medium_combinations

    low_list =  __getResiliency(operators, required_bandwidth, 1) #Low
    low_combinations = list(set(low_list) | set(medium_combinations))

    return(low_combinations)

def main():

    # Read port from env variable
    # If nothing there default to 5555
    port = os.getenv("RESC_PORT", "5555")
    print("Listening in port:", port)
    # Set up ZeroMQ socket
    context = zmq.Context()
    # REP for Reply pattern
    socket = context.socket(zmq.REP)
    # Bind to all interfaces on the specified port 
    socket.bind(f"tcp://*:{port}")  

    print("Resiliancy App is running...")


    while True:
        # Receive the request
        received_message = socket.recv_json()
        response = {}
        errcode = 200 # Set default success error code
        errmsg = "Success" # Set default success error msg
        # Convert dictionaries to Operator instances
        operators = [Operator(**op) for op in received_message['operators']]
        required_bandwidth = received_message['required_bandwidth']
        resiliency_level = received_message['resiliency_level']
        #print("Input Operators:", len(operators), required_bandwidth, resiliency_level)

        if resiliency_level < 1 or resiliency_level > 3 :
            resiliency_level = 1 #Wrong value defaulted to 1

        if len(operators) <= 0:
            # Add ErrorCode and ErrorMessage fields at the end
            response["ErrorCode"] = 301
            response["ErrorMessage"] = "No operators provided as input. At least one operator is required."

        elif required_bandwidth <= 0:
            response["ErrorCode"] = 302
            response["ErrorMessage"] = "No operators Provided as input. Min 1 is required"

        else:
            try:
                # Process the request using the function
                valid_combinations = getCombinations(operators, required_bandwidth, resiliency_level)
                # Convert each operator in valid combinations to a dictionary
                response = [
                    [op if isinstance(op, dict) else op.to_dict() for op in comb]
                    for comb in valid_combinations
                ]
            except Exception as e:
                response["ErrorCode"] = 500
                response["ErrorMessage"] = "Error in computing resilency combinations -" + e.args[0]


            # Add ErrorCode and ErrorMessage fields at the end
            response.append({
                "ErrorCode": errcode,  
                "ErrorMessage":errmsg  # Set default or appropriate value
            }
            )
        print(response)
        # Send the response
        socket.send_json(response)

if __name__ == "__main__":
    main()
