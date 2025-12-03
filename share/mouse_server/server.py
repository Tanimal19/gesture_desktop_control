import socket
import threading
import json
import logging
from typing import Optional
from enum import Enum
from share.mouse_server.pointer_distance_recorder import PointerDistanceRecorder
from share.mouse_server.mouse_controller import MouseController
from share.utils import setup_logging

logger = logging.getLogger(__name__)


class ActionType(Enum):
    MOVE = "move"
    BUTTON = "button"
    START_RECORDING = "start_recording"
    STOP_RECORDING = "stop_recording"


class MouseServer:
    def __init__(self, host="localhost", port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []
        self.running = False

        self.pointer_recorder = PointerDistanceRecorder()
        self.mouse_controller = MouseController()

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(1.0)

        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            logger.info(f"Mouse server started on {self.host}:{self.port}")
            logger.info("Press Ctrl+C to stop the server")
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            self.stop_server()

        # Main loop to accept clients
        try:
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logger.info(f"Client connected from {client_address}")

                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except socket.timeout:
                    continue
                except socket.error as e:
                    logger.error(f"Socket error: {e}")

        except KeyboardInterrupt:
            logger.info("Shutting down server due to keyboard interrupt")
        finally:
            self.stop_server()

    def stop_server(self):
        self.running = False

        # Close all client connections
        for client in self.clients[:]:
            try:
                client.close()
            except:
                pass
        self.clients.clear()

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        self.pointer_recorder.stop()

        logger.info("Mouse server stopped")

    def handle_client(self, client_socket, client_address):
        self.clients.append(client_socket)

        try:
            while self.running:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    command = json.loads(data.decode("utf-8"))
                    logger.info(f"Processed command from {client_address}: {command}")

                    response = self.process_command(command)
                    logger.info(f"Response to {client_address}: {response}")

                    client_socket.send(json.dumps(response).encode("utf-8"))

                except socket.error as e:
                    # client disconnected
                    break

        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            logger.info(f"Client {client_address} disconnected")

    def process_command(self, command) -> dict:

        def move_command(command):
            x = command.get("x")
            y = command.get("y")

            if x is not None and y is not None:
                self.mouse_controller.move(int(x), int(y))
                return self.generate_response(True)
            else:
                return self.generate_response(False)

        def button_command(command):
            x = command.get("x")
            y = command.get("y")
            button = command.get("button", "left")
            event_type = command.get("event_type", "click")

            if x is not None and y is not None:
                self.mouse_controller.button_event(int(x), int(y), button, event_type)
                return self.generate_response(True)
            else:
                return self.generate_response(False)

        def start_command(command):
            self.pointer_recorder.start()
            return self.generate_response(True)

        def stop_command(command):
            distance = self.pointer_recorder.stop()
            return self.generate_response(True, {"distance": distance})

        ACTION_MAP = {
            ActionType.MOVE: move_command,
            ActionType.BUTTON: button_command,
            ActionType.START_RECORDING: start_command,
            ActionType.STOP_RECORDING: stop_command,
        }

        action = command.get("action")
        action_enum = (
            ActionType(action) if action in ActionType._value2member_map_ else None
        )

        if action_enum:
            return ACTION_MAP[action_enum](command)
        else:
            return self.generate_response(False)

    @staticmethod
    def generate_response(success: bool, data: Optional[dict] = None) -> dict:
        response = {"status": "success" if success else "failure"}
        if data:
            response.update(data)
        return response


if __name__ == "__main__":
    # run the mouse server
    setup_logging("mouse_server.log")

    server = MouseServer()
    server.start_server()
