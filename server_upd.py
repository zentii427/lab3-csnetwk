import socket
import errno
import time

# Server host and port configuration
HOST = "127.0.0.1"  # Localhost
PORT = 65432        # Port number must be > 5000

SERVER_NAME = "Server of John Doe"
SERVER_NUM = 25     # Integer between 1 and 100

CLIENT_TIMEOUT = 10  # seconds to wait on a silent client before giving up on it
REPLY_DELAY = 3  # seconds the server waits before replying (testing only, set to 0 for the real demo)


def safe_close(sock, label):
    """Closes a socket without letting close() itself raise an error."""
    if sock is None:
        return
    try:
        sock.close()
    except OSError as e:
        print(f"[ERROR] Failed to close {label}: {e}")


def handle_client(client_conn):
    """
    Handles ONE client. Every error here is caught locally so a single bad
    client can never crash the server.
    Returns True  -> keep serving other clients
            False -> out-of-range number received, shut the server down
    """
    try:
        # if the client connects but never sends anything, recv() would block forever.
        # the timeout makes recv() raise socket.timeout instead
        client_conn.settimeout(CLIENT_TIMEOUT)

        # reads a max of 1024 bytes from the client
        raw = client_conn.recv(1024)

        # if data is empty (client connected and closed without sending)
        if not raw:
            print("[ACTION] Message received was empty. Closing connection.")
            return True

        # decoding can fail if the client sent bytes that are not valid UTF-8
        data = raw.decode("utf-8")
        print(f"[ACTION] Received raw message: '{data}'")

        # parses into the specified message format "Name,Number"
        # rsplit with maxsplit=1 splits on the LAST comma only, so a name with a comma still works
        parts = data.rsplit(",", 1)
        if len(parts) != 2:
            print("[ERROR] Invalid message format received from client. Expected 'Name,Number'.")
            return True

        client_name = parts[0].strip()

        # checks if the client number is an integer
        try:
            client_num = int(parts[1].strip())
        except ValueError:
            print("[ERROR] Received non-integer client number")
            return True

        # prints client and server name
        print(f"Client Name: {client_name}")
        print(f"Server Name: {SERVER_NAME}")

        # checks if the client number is within the specified range
        if not (1 <= client_num <= 100):
            print("[TERMINATION] Client number is out of range. Shutting down server...")
            return False

        # prints client and server numbers, and computes the sum
        total_sum = client_num + SERVER_NUM
        print(f"Client Number: {client_num}")
        print(f"Server Number: {SERVER_NUM}")
        print(f"Sum: {total_sum}")

        # testing aid: pause so there is time to press Ctrl+C on the client
        if REPLY_DELAY > 0:
            print(f"[ACTION] Waiting {REPLY_DELAY} seconds before replying (press Ctrl+C on the client now)...")
            time.sleep(REPLY_DELAY)

        # sends server name and server num back
        response = f"{SERVER_NAME},{SERVER_NUM}"
        client_conn.sendall(response.encode("utf-8"))
        print(f"[ACTION] Response sent back to client: '{response}'")
        return True

    # NOTE: order matters. socket.timeout and the Connection* errors are all
    # subclasses of OSError, so they must be listed BEFORE the generic OSError.
    except socket.timeout:
        print(f"[ERROR] Client did not send data within {CLIENT_TIMEOUT} seconds. Dropping it.")
    except UnicodeDecodeError:
        print("[ERROR] Client sent data that is not valid UTF-8 text.")
    except (ConnectionResetError, ConnectionAbortedError):
        print("[ERROR] Client reset or aborted the connection unexpectedly.")
    except BrokenPipeError:
        print("[ERROR] Client disconnected before the reply could be sent.")
    except OSError as e:
        print(f"[ERROR] Socket error while handling client: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error while handling client: {e}")
    finally:
        # always release the client socket, whatever happened above
        safe_close(client_conn, "client socket")
        print("[ACTION] Client socket closed.")

    # reached only when an error occurred: keep the server alive for the next client
    return True


def run_server():
    server_sock = None
    try:
        # creates a new socket. AF_INET for IPv4, and SOCK_STREAM for TCP
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Windows: SO_REUSEADDR lets two servers share a port, so use the exclusive option there.
        # Linux/Mac don't have SO_EXCLUSIVEADDRUSE, so they keep SO_REUSEADDR for quick restarts.
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # binds the socket to the HOST and PORT numbers
        server_sock.bind((HOST, PORT))

        # sets the server to passive listening mode, will only queue up to 1 connection
        server_sock.listen(1)
        server_sock.settimeout(1.0)   # wake up accept() every second so Ctrl+C can be noticed
        print(f"[ACTION] {SERVER_NAME} listening on {HOST}:{PORT}...")
        print("[ACTION] On standby for client connection...")

        keep_running = True
        while keep_running:
            try:
                client_conn, client_addr = server_sock.accept()
            except socket.timeout:
                continue              # nobody connected this second, just loop again

            print(f"[ACTION] Successful connection to client at {client_addr}")
            keep_running = handle_client(client_conn)
            if keep_running:
                print("[ACTION] On standby for client connection...")
        print(f"[ACTION] {SERVER_NAME} listening on {HOST}:{PORT}...")

        keep_running = True
        while keep_running:
            print("[ACTION] On standby for client connection...")

            # accept() pauses until a client connects (TCP handshake)
            # client_conn is the dedicated socket for that client,
            # client_addr is the client's IP address and ephemeral port
            client_conn, client_addr = server_sock.accept()
            print(f"[ACTION] Successful connection to client at {client_addr}")

            # handle_client closes client_conn itself and returns False on shutdown request
            keep_running = handle_client(client_conn)

    except OSError as e:
        # covers bind/listen/accept failures
        if e.errno == errno.EADDRINUSE:
            print(f"[ERROR] Port {PORT} is already in use. Close the other program or pick a different port.")
        elif isinstance(e, PermissionError):
            print(f"[ERROR] Permission denied when using {HOST}:{PORT}: {e}")
        else:
            print(f"[ERROR] Socket error encountered: {e}")
    except KeyboardInterrupt:
        # Ctrl+C
        print("\n[ACTION] Server interrupted by user (Ctrl+C).")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    finally:
        # release the welcoming socket on every exit path
        if server_sock:
            safe_close(server_sock, "server socket")
            print("[ACTION] Server socket closed. Clean exit complete.")


if __name__ == "__main__":
    run_server()
