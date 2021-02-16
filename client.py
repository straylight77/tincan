import sys
import socket
import select

def chat_client():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <hostname> <port>")
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((host, port))
    except Exception as e :
        print(f"Unable to connect: {e}")
        sys.exit()

    print('Connected to remote host. You can start sending messages')
    sys.stdout.write('[Me] ');
    sys.stdout.flush()

    while True:
        socket_list = [ sys.stdin, s ]

        try:
            ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt: exiting.")
            sys.exit()

        for sock in ready_to_read:
            if sock == s:
                 # incoming message from remote server, s
                data = sock.recv(4096)
                if not data :
                    print('\nDisconnected from chat server')
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data.decode('utf-8'))
                    sys.stdout.write('[Me] ');
                    sys.stdout.flush()

            else:
                # user entered a message
                msg = sys.stdin.readline()
                s.send(msg.encode('utf-8'))
                sys.stdout.write('[Me] ');
                sys.stdout.flush()

if __name__ == "__main__":
    sys.exit( chat_client() )



