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
