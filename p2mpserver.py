import sys, socketserver, struct

__author__ = "Stephen Worley"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Stephen Worley"
__email__ = "sworley1995@gmail.com"
__status__ = "Development"

# Port number
PORT = 0

# File store name
F_NAME = ""

# Probability of loss
PROB = 0

# Host for server
HOST = "localhost"

class ACK():
    """
    Acknowlegement segment
    """

    def __init__(self, seq_num):
        # 32-bit sequence number that is being ACKed
        self._seq_num = bytearray(seq_num)
        # 16-bit field that is all zeroes
        self._field_1 = bytearray(b'\x00\x00')
        # 16-bit field indicates that it is an ACK packe
        self._field_2 = bytearray(b'\xAA\xAA')
    # Returns sequence Number
    def get_seq_num(self):
        return self._seq_num

    # Return string of ACK segment
    def to_bits(self):
        bits = bytearray()
        print(bits)
        bits.append(self._seq_num[0])
        bits.append(self._seq_num[1])
        bits.append(self._seq_num[2])
        bits.append(self._seq_num[3])
        print(bits)
        bits.append(self._field_1[0])
        bits.append(self._field_1[1])
        print(bits)
        bits.append(self._field_2[0])
        bits.append(self._field_2[1])
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



def main():
    """
    Main method

    """

    try:
        PORT = int(sys.argv[1])
        F_NAME = sys.argv[2]
        PROB = int(sys.argv[3])

    except:
        print("Error in command line arguments.\
                \nShould be in the form 'p2mpserver port# file-name p'\n")

    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()



if __name__ == "__main__":
    main()



