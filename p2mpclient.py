import sys, socketserver, struct

__author__ = "Louis Le"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Louis Le"
__email__ = "lle3@ncsu.edu"
__status__ = "Development"

class Header():
    """
        Header of the segment
    """

    def __init__(self, seq_num, checksum):
        # 32-bit sequence number
        self._seq_num = bytearray(seq_num)
        # 16-bit checksum of datapart, computer in the same way as the UDP checksum
        self._checksum = bytearray(checksum)
        # 16-bit field, indicates that this is a data packet
        # 0101010101010101
        # Using 5 because it is hexidecimal
        self._field = bytearray(b'\x55\x55')

    # Returns sequence number
    def get_seq_num(self):
        return self._seq_num

    # Returns checksum
    def get_checksum(self):
        return self._checksum

    # Returns string of header
    def to_bits(self):
        bits = bytearray()
        print(bits)
        bits.append(self._seq_num[0])
        bits.append(self._seq_num[1])
        bits.append(self._seq_num[2])
        bits.append(self._seq_num[3])
        print(bits)
        bits.append(self._checksum_checksum[0])
        bits.append(self._checksum[1])
        print(bits)
        bits.append(self._field[0])
        bits.append(self._field[1])
        print(bits)
        return bits

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    UDP Request Handler
    """

    def handle(self):
        data = self.request[0].strip()

        seq_num, checksum, data_type = struct.unpack('>LHH', data)

        socket = self.request[1]
        print("seq: " + str(seq_num) + "\n")
        print("check: " + str(checksum) + "\n")
        print("type: " + str(data_type) + "\n")
        print(data)

        # TODO: For testing, just inc
        seq_num = seq_num + 1
        ack = ACK((seq_num).to_bytes(4, byteorder='big'))
        socket.sendto(ack.to_bits(), self.client_address)

def rdt_send(hostname, port, file):
    """
    Transfers data to P2MP-FTP servers
    Provides data from the file on a byte basis.
    """
    # SOCK_DGRAM is the socket type to use for UDP sockets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # As you can see, there is no connect() call; UDP has no connections.
        # Instead, data is directly sent to the recipient via sendto().
        sock.sendto(file + "\n", (HOST, PORT))
        received = sock.recv(1024)
    finally:
        sock.close()
    print("RDT SENT.\n")

#checksum():


if __name__ == "__main__":
    """
    Main method
    """

    PORT = 0

    try:
        HOST = "localhost"
        SERVERS, PORT, F_NAME, MSS = sys.argv[1:-3], int(sys.argv[-3]), sys.argv[-2], int(sys.argv[-1])
        print("SERVERS: " + str(SERVERS))
        print("PORT: " + str(PORT))
        print("F_NAME: " + F_NAME)
        print("MSS: " + str(MSS))
    except:
        print("Error in command line arguments.\
                \nShould be in the form 'p2mpclient server-1 server-2 server-3 server-port# file-name MSS\n")
        sys.exit()

    try:

        for server in SERVERS:
            rdt_send(server, PORT, F_NAME)

        server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
        server.serve_forever()
    except(KeyboardInterrupt, SystemExit):
        print("Exiting...\n")

        server.shutdown()
        sys.exit()
