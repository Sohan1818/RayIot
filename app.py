from flask import Flask, jsonify, render_template, request
from datetime import datetime
import time
import random
import threading
import requests

app = Flask(__name__)
data = []
data_sending_in_progress = False  # Flag to prevent concurrent data sending

def generate_sample_data():
    """Generate sample data."""
    timestamp = datetime.utcnow()
    temperature = round(random.uniform(20, 30), 2)
    humidity = round(random.uniform(50, 70), 2)
    pressure = round(random.uniform(1010, 1020), 2)
    return {
        "timestamp": timestamp.isoformat(),
        "temperature": temperature,
        "humidity": humidity,
        "pressure": pressure
    }

def send_data():
    """Periodically send generated data to the /data endpoint."""
    global data_sending_in_progress  # Access the flag defined outside the function
    while True:
        if not data_sending_in_progress:
            data_sending_in_progress = True
            data_point = generate_sample_data()
            requests.post('http://127.0.0.1:5000/data', json=data_point)
            data_sending_in_progress = False
        # Adjust sleep duration as needed
        time.sleep(10)

# Start a separate thread to send data periodically
data_thread = threading.Thread(target=send_data)
data_thread.daemon = True
data_thread.start()

@app.route('/data', methods=['POST'])
def receive_data():
    """Receive data in JSON format."""
    data.append(request.json)
    return jsonify({"message": "Data received successfully"})

@app.route('/graph')
def graph():
    """Render a simple graph with sample data."""
    # Check if data is available
    if not data:
        return render_template('graph.html', timestamps=[], temperatures=[], humidity=[], pressure=[])

    # Extract data for visualization
    timestamps = [datetime.fromisoformat(entry['timestamp']) for entry in data]
    temperatures = [entry['temperature'] for entry in data]
    humidity = [entry['humidity'] for entry in data]
    pressure = [entry['pressure'] for entry in data]

    return render_template('graph.html', timestamps=timestamps, temperatures=temperatures, humidity=humidity, pressure=pressure)


if __name__ == '__main__':
    app.run(debug=True)
