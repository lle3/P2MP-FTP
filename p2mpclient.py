import sys, socketserver, struct, threading, time, socket

__author__ = "Louis Le"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Louis Le"
__email__ = "lle3@ncsu.edu"
__status__ = "Development"

TIMEOUT = 10

servers_amount = 0
seq_counter = 0
server_counter = 0
server_dict = {}
lock = threading.Lock()
timed_out = False

class Header():
    """
        Header of the segment
    """

    def __init__(self, seq_num, checksum, EOT):
        # 32-bit sequence number
        self._seq_num = bytearray(seq_num)
        # 16-bit checksum of datapart, computer in the same way as the UDP checksum
        self._checksum = bytearray(checksum)
        # 16-bit EOF flag \x00\x00 if not end of transmission, \x00\x04 if EOF
        self._EOT = bytearray(EOT)
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

    def get_EOT(self):
        return self._EOT

    # Returns string of header
    def to_bits(self):
        bits = bytearray()
        bits.extend(self._seq_num)
        bits.extend(self._checksum)
        bits.extend(self._field)
        bits.extend(self._EOT)
        return bits

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

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

def rdt_send(header, hostname, port, data):
    """
    Transfers data to P2MP-FTP servers
    Provides data from the file on a byte basis.
    """
    global servers_amount, server_dict, server_counter

    # SOCK_DGRAM is the socket type to use for UDP sockets

    print("HOST STARTED: " + hostname)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # As you can see, there is no connect() call; UDP has no connections.
        # Instead, data is directly sent to the recipient via sendto().
        segment = header.to_bits()
        segment.extend(data.encode())
        sock.sendto(segment, (hostname, port))
        received = sock.recv(1024)

        print("Received: {}".format(bytearray(received)))

        seq_num, field_1, field_2 = struct.unpack(">LHH", received)

        print("seq_num: " + str(seq_num))
        print("field_1: " + str(field_1))
        print("field_2: " + str(field_2))

        if seq_num == seq_counter:
            with lock:
                server_counter += 1
                server_dict[hostname] = True
                print("HIT")
    finally:
        sock.close()

#checksum():

def ticker():
    """
    """
    global timed_out, server_counter, servers_amount
    life = TIMEOUT

    while(life > 0):
        print("LIFE: " + str(life))
        print("SERVER_COUNTER: " + str(server_counter))
        print("SERVER_WHAT: " + str(servers_amount))
        if(server_counter == servers_amount):
            return
        time.sleep(1)
        life -= 1

    print("TIMEOUT")
    timed_out = True

def controller(servers, port, file, MSS):
    global server_counter, seq_counter, server_dict, timed_out, servers_amount
    data = file.read(MSS)
    servers_amount = len(servers)
    seq_counter = 0
    first = True

    for h in servers:
        server_dict[h] = False

    while(data != ""):

        d = data.encode()

        if len(data) == MSS:
            header = Header((seq_counter).to_bytes(4, byteorder="big"), checksum(d).to_bytes(2, byteorder="big"), b'\x00\x00')
        else:
            space = (MSS - len(data))
            temp = bytearray(data.encode())
            for i in range(space):
                temp.extend(b"\x00")
            data = temp.decode()
            header = Header((seq_counter).to_bytes(4, byteorder="big"), checksum(d).to_bytes(2, byteorder="big"), b'\x00\x04')

        server_counter = 0
        timed_out = False

        thread_list = []

        for hostname in servers:
            print("HOSTNAME: " + hostname)
            if server_dict[hostname]:
                print("HEREJFKDJFKJD")
                continue
            

            t = threading.Thread(target=rdt_send, args=[header, hostname, port, data])
            t.daemon = True
            t.start()
            thread_list.append(t)

        ticker()

        print("OUT LOOP")
        print("TIMED OUT: " + str(timed_out))

        if timed_out:   # If it times out, it will not skip below so it doesn't set up for the next segment
            continue
        print("DIDN'T TIME OUT")

        for h in servers:
            server_dict[h] = False
        data = file.read(MSS)   # Reads next line
        seq_counter += 1
        server_counter = 0

if __name__ == "__main__":
    """
    Main method
    """

    try:
        SERVERS, PORT, F_NAME, MSS = sys.argv[1:-3], int(sys.argv[-3]), sys.argv[-2], int(sys.argv[-1])
        print("SERVERS: " + str(SERVERS))
        print("PORT: " + str(PORT))
        print("F_NAME: " + F_NAME)
        print("MSS: " + str(MSS))
        print("LENGTH: " + str(len(SERVERS)) + "\n")
    except:
        print("Error in command line arguments.\
                \nShould be in the form 'p2mpclient server-1 server-2 server-3 server-port# file-name MSS\n")
        sys.exit()

    try:
        file = open(F_NAME, "r")
    except:
        print("File does not exit: " + F_NAME + "\n")
        sys.exit()

    controller(SERVERS, PORT, file, MSS)
