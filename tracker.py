"""
This module provides a WebSocket server and a simple HTTP server 
to track the location of a shipment in real-time.
"""
import os
import json
import asyncio
import webbrowser
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from websockets.server import serve

# Initialize variables
token = None
barcode = None
clients = set()
current_task = None


async def location_tracker():
    """
    Tracks the location of a shipment using a barcode and token.
    This function continuously checks the location of a shipment by making
    requests to a specified URL. If the location changes, it notifies all
    connected clients with the new latitude and longitude.
    Global Variables:
    - token: The authentication token for the API.
    - barcode: The barcode of the shipment to track.
    - current_task: The current asyncio task.
    - clients: A list of connected clients to notify.
    The function runs indefinitely, checking for updates every 30 seconds.
    If the token or barcode is not set, it waits for 1 second before retrying.
    In case of an error (e.g., network issues or JSON decoding errors), it
    prints the error and waits for 30 seconds before retrying.
    Raises:
    - asyncio.CancelledError: If the task is cancelled.
    - json.JSONDecodeError: If the response JSON is invalid.
    - requests.RequestException: If there is an issue with the HTTP request.
    """

    global token, barcode, current_task
    old_long_lat = None

    while True:
        if not token or not barcode:
            await asyncio.sleep(1)  
            continue

        try:
            url = f"https://myspeedy.speedy.bg/rest/public/shipment/location?barcode={barcode}&token={token}"
            headers = {
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            lat = data["shipment"]["latLng"]["lat"]
            lng = data["shipment"]["latLng"]["lng"]
            long_lat = f'{lat},{lng}'

            if long_lat != old_long_lat:
                print(f'New location: {lat}, {lng}')
                old_long_lat = long_lat
                # Notify all connected clients
                if clients:
                    message = json.dumps({"lat": lat, "lng": lng})
                    await asyncio.gather(*[client.send(message) for client in clients])

            await asyncio.sleep(30)
        except (asyncio.CancelledError, json.JSONDecodeError, requests.RequestException) as e:
            print(f"Error occurred: {e}")
            await asyncio.sleep(30)


async def ws_handler(websocket):
    """
    Handle incoming WebSocket connections and messages.
    This function listens for incoming messages on the WebSocket connection,
    parses the JSON data, and updates the global `token` and `barcode` variables
    if they are present in the message. It also restarts the location tracker
    task with the new configuration.
    Args:
        websocket (WebSocketServerProtocol): The WebSocket connection instance.
    Raises:
        asyncio.CancelledError: If the task is cancelled.
        json.JSONDecodeError: If the incoming message is not valid JSON.
        KeyError: If the expected keys are not found in the JSON data.
    Note:
        This function is designed to be used with an asyncio event loop.
    """
    global token, barcode, current_task
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if "token" in data and "barcode" in data:
                token = data["token"]
                barcode = data["barcode"]
                print(f"Received new config: Token={token}, Barcode={barcode}")

                # Restart the location tracker with the new config
                if current_task:
                    current_task.cancel()
                current_task = asyncio.create_task(location_tracker())
    except (asyncio.CancelledError, json.JSONDecodeError, KeyError) as e:
        print(f"WebSocket error: {e}")
    finally:
        clients.remove(websocket)


def start_ws_server():
    """
    Starts a WebSocket server.

    This function initializes a new asyncio event loop, sets it as the current event loop,
    and starts a WebSocket server on the specified host and port. The server will run
    indefinitely until manually stopped.

    The WebSocket server listens on all available IP addresses (0.0.0.0) and port 8765.
    It uses the `ws_handler` function to handle incoming WebSocket connections.

    Prints:
        A message indicating that the WebSocket server is running and the address it is accessible at.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ws_server = serve(ws_handler, "0.0.0.0", 8765)
    loop.run_until_complete(ws_server)
    print("WebSocket server running on ws://localhost:8765")
    loop.run_forever()


def start_web_server():
    """
    Starts a simple HTTP web server to serve files from the 'map_server' directory.

    This function creates the 'map_server' directory if it does not exist, changes the current
    working directory to 'map_server', and starts an HTTP server on port 8000. The server will
    serve files using the SimpleHTTPRequestHandler, and it will run indefinitely until manually
    stopped.

    The server can be accessed at http://localhost:8000/shipment_map.html.

    Note:
        This function does not handle any exceptions that may occur during the creation of the
        directory, changing the working directory, or starting the server.

    Raises:
        OSError: If there is an issue creating the directory or changing the working directory.
    """
    os.makedirs("map_server", exist_ok=True)  # Ensure the folder exists
    os.chdir("map_server")
    server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)
    print("Serving map on http://localhost:8000/shipment_map.html")
    server.serve_forever()

if __name__ == "__main__":
    Thread(target=start_ws_server, daemon=True).start()
    Thread(target=start_web_server, daemon=True).start()
    webbrowser.open('http://localhost:8000/shipment_map.html', new=0)
    asyncio.run(location_tracker())

