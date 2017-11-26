import sys, socketserver, struct, random

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
PROB = 0.0

# Host for server
HOST = "localhost"

# Last received sequence number
last_seq = 0

# File for writing
f = None


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


    def get_seq_num(self):
        return self._seq_num


    def to_bits(self):
        """
        Converts header to bytearray
        """

        bits = bytearray()
        print(bits)
        bits.extend(self._seq_num)
        print(bits)
        bits.extend(self._field_1)
        print(bits)
        bits.extend(self._field_2)
        print(bits)
        return bits


class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    UDP Request Handler
    """

    def bit_add(num1, num2):
        """
        Adds bytes together with carryover
        """

        num_sum = num1 + num2
        return (num_sum & 0xffff) + (num_sum >> 16)


    def checksum(data):
        """
        Computes checksum
        """

        chk_sum = 0
        for i in range(0, len(data), 2):
            tmp = msg[i] + (msg[i+1] << 8)
            chk_sum = carry_around_add(chk_sum, tmp)
            return ~chk_sum & 0xffff


    def handle(self):
        """
        Request handler method
        """

        data = self.request[0].strip()

        seq_num, chk_sum, data_type, data = struct.unpack(">LHH%ds" % (len(data) - 8), data)

        socket = self.request[1]
        print("seq: " + str(seq_num) + "\n")
        print("check: " + str(chk_sum) + "\n")
        print("type: " + str(data_type) + "\n")
        print(data)

        if (random.uniform(0,1) > p):
            if (chk_sum == checksum(data)):
                if (seq_num == (last_seq + 1)):
                    last_seq += 1
                    f.write(data.decode("utf-8"))
                ack = ACK((last_seq).to_bytes(4, byteorder='big'))
                socket.sendto(ack.to_bits(), self.client_address)



def main():
    """
    ain method

    """

    try:
        PORT = int(sys.argv[1])
        F_NAME = sys.argv[2]
        PROB = float(sys.argv[3])        

    except:
        print("Error in command line arguments.\
                \nShould be in the form 'p2mpserver port# file-name p'\n")

    try:
        f = open(F_NAME, 'w')

    except IOError:
        print("Error opening file: " + F_NAME + "\n")


    try:
        server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
        server.serve_forever()
    except(KeyboardInterrupt, SystemExit):
        f.close()
        server.shutdown()



if __name__ == "__main__":
    main()



