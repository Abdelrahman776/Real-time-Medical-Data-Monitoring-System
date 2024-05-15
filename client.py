import socket
import json
import time
import random

# Define server address and port
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 12345

def generate_vital_signs(num_points):
    # Simulate generating a list of random values
    return [random.randint(0, 100) for _ in range(num_points)]

def send_data_to_server():
    try:
        # Create a TCP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        client_socket.connect((SERVER_ADDRESS, SERVER_PORT))
        print("Connected to server.")

        # Initial data send (100 points)
        patient_id = 1
        vital_signs = generate_vital_signs(100)
        data = {'patient_id': patient_id, 'vital_signs': vital_signs}
        client_socket.sendall(json.dumps(data).encode())
        print(f"Sent initial data to server: {data}")

        # Subsequent data sends (10 points each)
        while True:
            vital_signs = generate_vital_signs(10)
            data = {'patient_id': patient_id, 'vital_signs': vital_signs}
            client_socket.sendall(json.dumps(data).encode())
            print(f"Sent data to server: {data}")

            # Sleep for a short interval before sending next data
            time.sleep(1)  # Simulate sending data every second

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the socket
        client_socket.close()

if __name__ == "__main__":
    send_data_to_server()
