import socket

HOST = "0.0.0.0"          # listen on all network interfaces
PORT = 65432               # must be > 1023 (> 5000 to be safe)
SERVER_NAME = "Server of Your Name"
SERVER_NUMBER = 42        # server's chosen integer (1-100)

def main():
    server_sock = None
    try:
        # Create a TCP socket (same as socket() in C)
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Lets you restart the server right away without "address in use" errors
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(5)
        print(f"[SERVER] Listening on port {PORT} as '{SERVER_NAME}'")

        running = True
        while running:
            print("[SERVER] Waiting for a client...")
            conn, addr = server_sock.accept()   # blocks until a client connects
            print(f"[SERVER] Connection from {addr}")

            try:
                # Receive and decode the message, e.g. "Client of John|57"
                data = conn.recv(1024).decode().strip()
                print(f"[SERVER] Received raw message: {data}")

                # Split on the LAST '|' so names containing '|' wouldn't break us
                client_name, num_str = data.rsplit("|", 1)
                client_num = int(num_str)       # raises ValueError if not an int

                if not (1 <= client_num <= 100):
                    print(f"[SERVER] {client_num} is out of range. Shutting down.")
                    running = False             # exits the while loop
                else:
                    print(f"[SERVER] Client name: {client_name}")
                    print(f"[SERVER] Server name: {SERVER_NAME}")
                    print(f"[SERVER] Client number: {client_num}, "
                          f"Server number: {SERVER_NUMBER}, "
                          f"Sum: {client_num + SERVER_NUMBER}")

                    reply = f"{SERVER_NAME}|{SERVER_NUMBER}\n"
                    conn.sendall(reply.encode())
                    print("[SERVER] Reply sent.")

            except ValueError as e:
                print(f"[SERVER] Malformed message: {e}")
            except OSError as e:
                print(f"[SERVER] Error talking to client: {e}")
            finally:
                conn.close()                    # always release the client socket
                print("[SERVER] Client connection closed.")

    except OSError as e:
        print(f"[SERVER] Socket error: {e}")
    except KeyboardInterrupt:
        print("\n[SERVER] Interrupted by user.")
    finally:
        if server_sock:
            server_sock.close()                 # release the welcoming socket
            print("[SERVER] Server socket closed. Bye.")

if __name__ == "__main__":
    main()