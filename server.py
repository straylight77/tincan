import sys
import socket
import select


class ChatServer():

    def __init__(self):
        self.host = ""
        self.port = 9009
        self.buf_size = 4096
        self.max_clients = 10
        self.socket_list = [ ]  # list of socket objects
        self.registered = { }   # registered users: sockfd => name


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
                            client_name = self.get_client_name(sock)
                            if client_name is not None:
                                msg = f"\r[{client_name}] {data_str}"
                                self.broadcast(sock, msg)
                            else:
                                msg = f"\r> please register first, use /register <name>\n"
                                self.send(sock, msg)
                    else:
                        #remove the socket that's broken
                        self.remove_client(sock)


    def is_registered(self, sockfd):
        for name in list(self.registered):
            if sockfd == self.registered[name]:
                return True
        return False


    def get_client_name(self, sockfd):
        for name in list(self.registered):
            if sockfd == self.registered[name]:
                return name
        return None


    def get_connection_name(self, sock):
        p = sock.getpeername()
        return f"{p[0]}:{p[1]}"


    def add_client(self, sockfd, addr):
        self.socket_list.append(sockfd)
        name = self.get_connection_name(sockfd)
        #self.broadcast(sockfd, f"\r> new connection {name}\n")
        self.log(f"\r> new connection from {name}\n")


    def remove_client(self, socket):
        conn_name = self.get_connection_name(socket)
        if socket in self.socket_list:
            self.socket_list.remove(socket)
            client_name = self.get_client_name(socket)
            if client_name is not None:
                del(self.registered[client_name])
                self.broadcast(socket, f"\r> {client_name} has left the room\n")
            else:
                self.log(f"\r> unregistered client from {conn_name} dropped\n")

        socket.close()


    def send(self, sockfd, message):
        try:
            sockfd.send(message.encode('utf-8'))
        except Exception as e:
            self.log(f"!error: {e}")
            self.remove_client(s)


    def broadcast(self, sender_socket, message):
        self.log(message)
        for name, s in self.registered.items():
            if s != self.server_socket and s != sender_socket:
                try:
                    s.send(message.encode('utf-8'))
                except Exception as e:
                    self.log(f"!error: {e}")
                    self.remove_client(s)


    def log(self, msg):
        print(msg.strip())


    def do_command(self, sockfd, message):
        cmd = message[1:].strip().split()
        self.log(f"/{cmd[0]} from {sockfd.getpeername()}")

        if cmd[0] in ("help", "who", "register"):
            try:
                # dynamically call a function based on the command name
                method_name = "do_" + cmd[0]
                func = getattr(self, method_name)
                func(sockfd, cmd[1:])
            except AttributeError as e:
                self.log(f"!error: {e}")
                self.send(sockfd, f"\r> sorry, '{cmd[0]}' is not implemented.\n")

        else:
            self.send(sockfd, f"\r> sorry, '{cmd[0]}' is not implemented.\n")


    def do_register(self, sockfd, args):
        if len(args) < 1:
            msg = f"\r> missing nickname.  usage: /register <nick>\n"
            self.send(sockfd, msg)
            return

        name = args[0]
        self.broadcast(sockfd, f"\r> {name} has entered the chat room\n")
        self.registered[name] = (sockfd)


    def do_who(self, sockfd, args):
        #self.send(sockfd, f"\r> who\n")
        msg = "\r> Currently registered in this chat room:\n"
        for name in list(self.registered):
            msg += f">  {name}"
            if sockfd == self.registered[name]:
                msg += " (you)"
            msg += "\n"

        self.send(sockfd, msg)




#---------------------------------------------------------------------------
if __name__ == "__main__":
    s = ChatServer()
    s.start()
    s.main_loop()
    s.end()




