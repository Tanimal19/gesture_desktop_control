import socket
import json
import logging
from share.mouse_server.server import ActionType

logger = logging.getLogger(__name__)


class MouseServerClient:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logger.info(f"Connected to mouse server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to server: {e}")
            logger.info(
                "Please make sure the mouse server is running: python -m share.mouse_server.server"
            )
            return False

    def disconnect(self):
        if self.socket:
            self.socket.close()
            logger.info("Disconnected from mouse server")

    def send_command(self, command):
        if not self.socket:
            return None

        try:
            command_json = json.dumps(command)
            self.socket.send(command_json.encode("utf-8"))
            logger.debug(f"Sent command: {command_json}")

            response = self.socket.recv(1024)
            return json.loads(response.decode("utf-8"))

        except Exception as e:
            logger.error(f"Error sending command: {e}")
            return None

    def move_mouse(self, x, y):
        command = {"action": ActionType.MOVE.value, "x": x, "y": y}
        return self.send_command(command)

    def button_event(self, x, y, down, button):
        command = {
            "action": ActionType.BUTTON.value,
            "x": x,
            "y": y,
            "down": down,
            "button": button,
        }
        return self.send_command(command)

    def start_distance_recording(self):
        command = {"action": ActionType.START_RECORDING.value}
        return self.send_command(command)

    def stop_distance_recording(self):
        command = {"action": ActionType.STOP_RECORDING.value}
        return self.send_command(command)
