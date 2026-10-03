import socket
import sys

# Server host and port configuration
HOST = "127.0.0.1"  # Localhost
PORT = 65432        # Port number must be > 5000

SERVER_NAME = "Server of John Doe"
SERVER_NUM = 25     # Integer between 1 and 100

def run_server(): 
    server_sock = None
    client_conn = None
    try:
        # creates a new socket. AF_INET for IPv4, and SOCK_STREAM for TCP
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # configs the socket to look at the general socket layer, and allowing it to reuse the address
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # binds the socket to the HOST and PORT numbers
        server_sock.bind((HOST,PORT))

        # sets the server to passive listening mode, will only queue up to 1 connection before rejecting new requests
        server_sock.listen(1)
        print(f"[ACTION] {SERVER_NAME} listening on {HOST}:{PORT}...")

        while True:
            print("[ACTION] On standby for client connection...")

            # accept() pauses code execution up until a client establishes connection (TCP handshake)
            # also generates a new socket "client_conn" that is dedicated to sending and receiving data with the client
            # "client_addr" stores the IP add and ephemeral port num used by the client machine
            client_conn, client_addr = server_sock.accept()
            print(f"[ACTION] Successful connection to client at {client_addr}")

            # reads a max of 1024 bytes from the client, and decodes it into string
            data = client_conn.recv(1024).decode("utf-8")

            # if data is empty
            if not data:
                print("[ACTION] Message recieved was empty. Closing connection.")
                client_conn.close()
                continue

            print(f"[ACTION] Received raw message: '{data}'")

            # parses into specified message format
            parts = data.split(",")
            if len(parts) == 2:
                client_name = parts[0].strip()

                #checks if client num input are integers
                try:
                    client_num = int(parts[1].strip())
                except ValueError:
                    print(f"[ERROR] Received non-integer client number")
                    client_conn.close()
                    continue

            else:
                print("[ERROR] Invalid message format received from client. Expected 'Name,Number'.")
                client_conn.close()
                continue

            # prints client and server name
            print(f"Client Name: {client_name}")
            print(f"Server Name: {SERVER_NAME}")

            #checks if client num is within the specified range
            if not (1 <= client_num <= 100):
                print(f"[TERMINATION] Client number is out of range. Shutting down server...")
                client_conn.close()
                break

            # prints client and server numbers, and computes the sum
            total_sum = client_num + SERVER_NUM
            print(f"Client Number: {client_num}")
            print(f"Server Number: {SERVER_NUM}")
            print(f"Sum: {total_sum}")

            # sends server name and server num back
            response = f"{SERVER_NAME},{SERVER_NUM}"
            client_conn.sendall(response.encode("utf-8"))
            print(f"[ACTION] Response sent back to client: '{response}'")

            #close connection with client
            client_conn.close()
            client_conn = None
            print(f"Client socket closed successfully")

    except socket.error as e:
        print(f"[ERROR] Socket error encountered: {e}")

    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

    finally:
        # release all sockets upon closing connection
        if client_conn:
            client_conn.close()
        if server_sock:
            server_sock.close()
            print("[ACTION] Server socket closed. Clean exit complete.")

if __name__ == "__main__":
    run_server()