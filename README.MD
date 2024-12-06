# Real-Time Shipment Tracker (SPEEDY.BG)

This project provides a **WebSocket server** and a **simple HTTP server** to track the real-time location of a shipment using a token and barcode. It allows clients to receive live updates on a shipment's latitude and longitude via WebSocket messages, while also serving a map interface via HTTP.

---

## Features

- **Real-Time Location Updates**: Periodically fetches shipment location from an external API and sends updates to connected WebSocket clients.
- **WebSocket Server**: Handles connections and dynamically updates configuration for token and barcode.
- **HTTP Server**: Serves a map interface (`shipment_map.html`) for visualizing shipment location.
- **Automatic Map Launch**: Opens the map interface in the default web browser upon starting the application.

---

## Requirements

- **Python**: 3.8 or newer
- **Dependencies**: 
  - `websockets`
  - `requests`

Install dependencies using:

```bash
pip install websockets requests
```

---

## How It Works

1. **WebSocket Server**:
   - Runs on `ws://localhost:8765`.
   - Accepts JSON messages to configure the `token` and `barcode` for tracking:
     ```json
     {
       "token": "your-token-here",
       "barcode": "your-barcode-here"
     }
     ```
   - Sends location updates in the format:
     ```json
     {
       "lat": 42.12345,
       "lng": 24.67890
     }
     ```

2. **HTTP Server**:
   - Serves files from the `map_server` directory.
   - Accessible at `http://localhost:8000/shipment_map.html`.

3. **Location Tracker**:
   - Periodically fetches the shipment's location from the API:
     ```
     https://myspeedy.speedy.bg/rest/public/shipment/location
     ```
   - Notifies all connected WebSocket clients of location changes.

---

## Usage

1. **Run the Script**:
   ```bash
   python tracker.py
   ```
   This will:
   - Start the WebSocket server on `ws://localhost:8765`.
   - Start the HTTP server on `http://localhost:8000`.
   - Open the map interface (`shipment_map.html`) in the default browser.

2. **Configure via WebSocket**:
   - Use a WebSocket client (e.g., browser, Postman, or a custom script) to send a JSON message with the `token` and `barcode` to `ws://localhost:8765`.

3. **Visualize on the Map**:
   - The served `shipment_map.html` file will display the shipment's real-time location.

---

## File Structure

- **`tracker.py`**: Main script for running WebSocket and HTTP servers.
- **`map_server/`**: Directory to serve files for the HTTP server.
- **`shipment_map.html`**: OpenStreetMap.

---

## Troubleshooting

- **Dependencies Missing**:
  - Ensure all dependencies are installed: `pip install websockets requests`.
- **WebSocket Connection Issues**:
  - Verify the WebSocket server is running on `ws://localhost:8765`.
- **HTTP Server Not Serving Files**:
  - Ensure the `map_server` directory contains the required files.

---

Enjoy tracking shipments in real-time with this lightweight and extensible tracker! 🚚
