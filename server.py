import sys
import socket
import select


class ChatServer():

    def __init__(self):
        self.host = ""
        self.port = 9009
        self.buf_size = 4096
        self.max_clients = 10
        self.socket_list = [ ]


    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        self.socket_list.append(self.server_socket)
        print(f"server listening on port {self.port}")


    def end(self):
        self.log("closing connection")
        self.server_socket.close()


    def main_loop(self):
        self.log("starting main loop")
        while True:

            try:
                rlist, wlist, elist = select.select(self.socket_list, [], [], 0)
            except KeyboardInterrupt:
                self.log("\nKeyboardInterrupt: ending main loop")
                break

            for sock in rlist:

                # a new connection received
                if sock == self.server_socket:
                    sockfd, addr = self.server_socket.accept()
                    self.add_client(sockfd, addr)

                # a message from a client, not a new connection
                else:
                    data = sock.recv(self.buf_size)
                    if data:
                        data_str = data.decode('utf-8')
                        if data_str[0] == '/':
                            # control message
                            self.do_command(sock, data_str)
                        else:
                            # chat message
                            msg = f"\r[{sock.getpeername()}] {data_str}"
                            self.broadcast(sock, msg)
                    else:
                        #remove the socket that's broken
                        self.remove_client(sock)


    def do_command(self, sockfd, message):
        commands = message[1:].strip().split()
        self.log(f"command '{commands[0]}' from {sockfd.getpeername()}")



    def add_client(self, sockfd, addr):
        self.socket_list.append(sockfd)
        self.broadcast(sockfd, f"new client connected from {addr}\n")


    def remove_client(self, socket):
        self.broadcast(socket, f"client [{socket.getpeername()}] is offline\n")
        if socket in self.socket_list:
            self.socket_list.remove(socket)
        socket.close()


    def broadcast(self, sender_socket, message):
        self.log(message)
        for s in self.socket_list:
            if s != self.server_socket and s != sender_socket:
                try:
                    s.send(message.encode('utf-8'))
                except Exception as e:
                    self.log(f"error: {e}")
                    self.remove_client(s)


    def log(self, msg):
        print(msg.rstrip())




#---------------------------------------------------------------------------
if __name__ == "__main__":
    s = ChatServer()
    s.start()
    s.main_loop()
    s.end()




