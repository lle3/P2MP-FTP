import sys, socketserver, struct, random



__author__ = "Stephen Worley"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Stephen Worley"
__email__ = "sworley1995@gmail.com"
__status__ = "Development"



# Port number
port = 0

# File store name
f_name = ""

# Probability of loss
prob = 0.0

# Host for server
HOST = "localhost"

# Last received sequence number
last_seq = -1

# File for writing
f = None

# End of transmission
EOT = 4



def bit_add(num1, num2):
    """
    Adds bytes together with carryover
    """

    num_sum = num1 + num2
    return (num_sum & 0xffff) + (num_sum >> 16)


def checksum(d):
    """
    Computes checksum
    """

    chk_sum = 0
    for i in range(0, len(d), 2):
        tmp = d[i] + (d[i+1] << 8)
        chk_sum = bit_add(chk_sum, tmp)
        return ~chk_sum & 0xffff



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
        bits.extend(self._seq_num)
        bits.extend(self._field_1)
        bits.extend(self._field_2)
        return bits



class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    UDP Request Handler
    """

    def handle(self):
        """
        Request handler method
        """

        data = self.request[0].strip()

        print(data)

        seq_num, chk_sum, data_type, eot, msg = struct.unpack(">LHHH%ds" % (len(data) - 10), data)

        socket = self.request[1]

        print("seq: " + str(seq_num) + "\n")
        print("check: " + str(chk_sum) + "\n")
        print("type: " + str(data_type) + "\n")
        print("eot: " + str(eot) + "\n")
        print("msg: " + str(msg) + "\n")

        if (random.uniform(0,1) > prob):
            if (chk_sum == checksum(msg)):
                global last_seq
                if (seq_num == (last_seq + 1)):
                    last_seq += 1
                    f.write(msg.decode("utf-8"))

                ack = ACK((last_seq).to_bytes(4, byteorder='big'))
                socket.sendto(ack.to_bits(), self.client_address)

                if (eot == EOT):
                    f.write(msg.decode("utf-8").rstrip('\0'))
                    f.close()
                    sys.exit()


        else:
            print("Packet loss, sequence number = " + str(seq_num) + "\n")


def main():
    """
    Main method

    """

    global port
    global f_name
    global prob
    global f

    try:
        port = int(sys.argv[1])
        f_name = sys.argv[2]
        prob = float(sys.argv[3])        

    except:
        print("Error in command line arguments.\
                \nShould be in the form 'p2mpserver port# file-name p'\n")

    try:
        f = open(f_name, 'w')

    except IOError:
        print("Error opening file: " + f_name + "\n")


    try:
        server = socketserver.UDPServer((HOST, port), MyUDPHandler)
        server.serve_forever()
    except(KeyboardInterrupt, SystemExit):
        f.close()
        server.shutdown()



if __name__ == "__main__":
    main()



