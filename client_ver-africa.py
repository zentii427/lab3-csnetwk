import socket
import sys

HOST = "127.0.0.1"
PORT = 65432
CLIENT_NAME = "Client of John Doe"

def run_client():
    client_sock = None
    try:
        # Accept and validate user keyboard input
        user_input = input("Enter an integer between 1 and 100: ").strip()
        try:
            client_num = int(user_input)
        except ValueError:
            print("[ERROR] Invalid input: You must enter an integer.")
            return

        print(f"[ACTION] User entered integer: {client_num}")

        # Instantiate TCP socket (IPv4, TCP stream)
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f"[ACTION] Connecting to server at {HOST}:{PORT}...")

        # Connect to the server
        client_sock.connect((HOST, PORT))
        print(f"[ACTION] Successfully connected to {HOST}:{PORT}")

        # Format and transmit message: "Client Name,Integer"
        message = f"{CLIENT_NAME},{client_num}"
        client_sock.sendall(message.encode("utf-8"))
        print(f"[ACTION] Sent message to server: '{message}'")

        # Await response from server
        print("[ACTION] Awaiting response from server...")
        data = client_sock.recv(1024).decode("utf-8")

        if not data:
            print("[ACTION] Server closed connection without sending data (likely out-of-range termination).")
            return

        print(f"[ACTION] Received raw reply from server: '{data}'")

        # Parse server payload
        parts = data.split(",")
        if len(parts) == 2:
            server_name = parts[0].strip()
            try:
                server_num = int(parts[1].strip())
            except ValueError:
                print("[ERROR] Received non-integer value from server.")
                return

            # Display required information and calculate the sum
            total_sum = client_num + server_num
            print("\n" + "=" * 40)
            print(f"Client Name   : {CLIENT_NAME}")
            print(f"Server Name   : {server_name}")
            print(f"Client Number : {client_num}")
            print(f"Server Number : {server_num}")
            print(f"Sum           : {total_sum}")
            print("=" * 40 + "\n")
        else:
            print(f"[ERROR] Invalid format received from server. Expected 'ServerName,ServerNum', received: '{data}'")

    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to server at {HOST}:{PORT}. Ensure server.py is running.")
    except socket.error as e:
        print(f"[ERROR] Socket error occurred: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    finally:
        # Release socket cleanly
        if client_sock:
            client_sock.close()
            print("[ACTION] Client socket closed successfully.")

if __name__ == "__main__":
    run_client()