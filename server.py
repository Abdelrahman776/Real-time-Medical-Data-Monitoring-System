import socket
import json
import redis

# Define server address and port
SERVER_ADDRESS = '127.0.0.1'
SERVER_PORT = 12345

# Redis connection
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def handle_client_connection(client_socket):
    try:
        while True:
            # Receive data from the client
            data = client_socket.recv(4096)
            if not data:
                break

            # Decode JSON data
            json_data = data.decode()
            received_data = json.loads(json_data)

            # Extract patient ID and vital signs list
            patient_id = received_data['patient_id']
            new_vital_signs = received_data['vital_signs']

            # Retrieve existing data from Redis
            key = f'patient:{patient_id}:vital_signs'
            existing_data_json = redis_client.get(key)
            if existing_data_json:
                existing_vital_signs = json.loads(existing_data_json)
            else:
                existing_vital_signs = []

            # Update the data
            updated_vital_signs = (existing_vital_signs + new_vital_signs)[-100:]

            # Store updated data in Redis
            redis_client.set(key, json.dumps(updated_vital_signs))

            # Publish update to Redis Pub/Sub channel
            redis_client.publish('vital_signs_update', json.dumps({'patient_id': patient_id, 'vital_signs': updated_vital_signs}))

            print(f"Received and updated data for patient {patient_id}: {updated_vital_signs}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the client socket
        client_socket.close()

def start_server():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the server address and port
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))

    # Listen for incoming connections
    server_socket.listen(5)
    print("Server is listening for incoming connections...")

    try:
        while True:
            # Accept incoming connection
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            # Handle client connection in a separate thread
            handle_client_connection(client_socket)

    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    start_server()
