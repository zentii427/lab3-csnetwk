import socket

HOST = "127.0.0.1"
PORT = 65432
CLIENT_NAME = "Client of John Doe"

SOCKET_TIMEOUT = 10  # seconds to wait for connect/recv before giving up


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

        # without a timeout, connect() or recv() could hang forever if the server stalls
        client_sock.settimeout(SOCKET_TIMEOUT)

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
        raw = client_sock.recv(1024)

        # an empty result means the server closed the connection without replying
        if not raw:
            print("[ACTION] Server closed connection without sending data.")
            return

        # decoding can fail if the reply is not valid UTF-8
        data = raw.decode("utf-8")
        print(f"[ACTION] Received raw reply from server: '{data}'")

        # Parse server payload "ServerName,ServerNum"
        # rsplit(",", 1) splits on the last comma only
        parts = data.rsplit(",", 1)
        if len(parts) != 2:
            print(f"[ERROR] Invalid format received from server. Expected 'ServerName,ServerNum', received: '{data}'")
            return

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

    # NOTE: order matters. ConnectionRefusedError, socket.timeout and the other
    # specific errors below are all subclasses of OSError, so they must come
    # BEFORE the generic OSError handler or they would never be reached.
    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to server at {HOST}:{PORT}. Ensure the server is running.")
    except socket.timeout:
        print(f"[ERROR] Timed out after {SOCKET_TIMEOUT} seconds waiting for the server.")
    except socket.gaierror as e:
        print(f"[ERROR] Could not resolve server address '{HOST}': {e}")
    except ConnectionResetError:
        print("[ERROR] The server reset the connection unexpectedly.")
    except BrokenPipeError:
        print("[ERROR] The server closed the connection before the message could be sent.")
    except UnicodeDecodeError:
        print("[ERROR] The server's reply is not valid UTF-8 text.")
    except OSError as e:
        print(f"[ERROR] Socket error occurred: {e}")
    except EOFError:
        # input() has nothing to read (e.g. Ctrl+D or closed stdin)
        print("[ERROR] No input available from keyboard.")
    except KeyboardInterrupt:
        # Ctrl+C
        print("\n[ACTION] Client interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    finally:
        # Release socket cleanly; close() is wrapped so it can't raise either
        if client_sock:
            try:
                client_sock.close()
                print("[ACTION] Client socket closed successfully.")
            except OSError as e:
                print(f"[ERROR] Failed to close client socket: {e}")


if __name__ == "__main__":
    run_client()
