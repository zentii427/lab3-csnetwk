import socket
import sys

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 65432
CLIENT_NAME = "Client of John Doe"

def main():
    sock = None
    try:
        # Read the number. No 1-100 check here on purpose: the lab says an
        # out-of-range value is how you shut the server down.
        client_num = int(input("Enter an integer (1-100): "))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)                     # don't hang forever
        print(f"[CLIENT] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
        sock.connect((SERVER_HOST, SERVER_PORT))
        print("[CLIENT] Connected.")

        msg = f"{CLIENT_NAME}|{client_num}\n"
        sock.sendall(msg.encode())
        print(f"[CLIENT] Sent: {msg.strip()}")

        data = sock.recv(1024).decode().strip()
        print(f"[CLIENT] Raw reply: {repr(data)}")
        if not data:
            # Server closed without replying (happens when we shut it down)
            print("[CLIENT] Server closed the connection with no reply.")
            return

        # print(f"[CLIENT] Received: {data}")
        server_name, num_str = data.rsplit("|", 1)
        server_num = int(num_str)

        print(f"Client name: {CLIENT_NAME}")
        print(f"Server name: {server_name}")
        print(f"Client number: {client_num}, Server number: {server_num}")
        print(f"Sum: {client_num + server_num}")

    except ValueError as e:
        print(f"[CLIENT] Bad number or malformed reply: {e}")
    except ConnectionRefusedError:
        print("[CLIENT] Connection refused. Is the server running?")
    except socket.timeout:
        print("[CLIENT] Timed out waiting for the server.")
    except OSError as e:
        print(f"[CLIENT] Socket error: {e}")
    finally:
        if sock:
            sock.close()
            print("[CLIENT] Socket closed.")

if __name__ == "__main__":
    main()