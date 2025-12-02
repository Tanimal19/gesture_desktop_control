#!/usr/bin/env python3
"""
Test client for the Mouse Server
Demonstrates how to send commands to control and inspect the mouse
"""

import socket
import json
import time


class MouseClient:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        """Connect to the mouse server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to mouse server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False

    def send_command(self, command):
        """Send a command to the server and return the response"""
        try:
            # Send command
            command_json = json.dumps(command)
            self.socket.send(command_json.encode("utf-8"))

            # Receive response
            response = self.socket.recv(1024)
            return json.loads(response.decode("utf-8"))
        except Exception as e:
            print(f"Error sending command: {e}")
            return None

    def ping(self):
        """Test server connectivity"""
        return self.send_command({"action": "ping"})

    def get_mouse_position(self):
        """Get current mouse position"""
        return self.send_command({"action": "get_position"})

    def move_mouse(self, x, y):
        """Move mouse to specified coordinates"""
        return self.send_command({"action": "move", "x": x, "y": y})

    def click_mouse(self, x, y, button="left", down=True):
        """Click mouse at specified coordinates"""
        return self.send_command(
            {"action": "click", "x": x, "y": y, "button": button, "down": down}
        )

    def start_distance_recording(self):
        """Start recording mouse movement distance"""
        return self.send_command({"action": "start_distance_recording"})

    def stop_distance_recording(self):
        """Stop recording and get total distance"""
        return self.send_command({"action": "stop_distance_recording"})

    def disconnect(self):
        """Disconnect from server"""
        if self.socket:
            self.socket.close()
            print("Disconnected from server")


def main():
    """Test the mouse server with various commands"""
    client = MouseClient()

    if not client.connect():
        return

    try:
        # Test ping
        print("\n1. Testing server connectivity...")
        response = client.ping()
        print(f"Ping response: {response}")

        # Get current mouse position
        print("\n2. Getting current mouse position...")
        response = client.get_mouse_position()
        print(f"Current position: {response}")

        # Move mouse to a new position
        print("\n3. Moving mouse to (500, 300)...")
        response = client.move_mouse(500, 300)
        print(f"Move response: {response}")
        time.sleep(1)

        # Get position again to verify move
        print("\n4. Verifying new position...")
        response = client.get_mouse_position()
        print(f"New position: {response}")

        # Start distance recording
        print("\n5. Starting distance recording...")
        response = client.start_distance_recording()
        print(f"Start recording response: {response}")

        # Move mouse in a small pattern
        print("\n6. Moving mouse in a pattern...")
        positions = [(520, 320), (480, 320), (500, 340), (500, 300)]
        for x, y in positions:
            client.move_mouse(x, y)
            time.sleep(0.5)

        # Stop distance recording
        print("\n7. Stopping distance recording...")
        response = client.stop_distance_recording()
        print(f"Distance recording result: {response}")

        # Demonstrate click
        print("\n8. Performing left click at current position...")
        pos_response = client.get_mouse_position()
        if pos_response and pos_response.get("status") == "success":
            x, y = pos_response["x"], pos_response["y"]

            # Press
            response = client.click_mouse(x, y, "left", True)
            print(f"Mouse press response: {response}")
            time.sleep(0.1)

            # Release
            response = client.click_mouse(x, y, "left", False)
            print(f"Mouse release response: {response}")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        client.disconnect()


if __name__ == "__main__":
    print("Mouse Server Test Client")
    print("========================")
    print("Make sure the mouse server is running before starting this test.")
    input("Press Enter to continue...")
    main()
