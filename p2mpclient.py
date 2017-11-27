import sys, socketserver, struct, threading, time, socket

__author__ = "Louis Le"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Louis Le"
__email__ = "lle3@ncsu.edu"
__status__ = "Development"

TIMEOUT = 30

seq_counter = 0
server_counter = 0
server_dict = {}
lock = threading.Lock()

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

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg), 2):
        w = msg[i] + (msg[i+1] << 8)
        s = carry_around_add(s, w)
    return ~s & 0xffff

def rdt_send(header, hostname, port, data):
    """
    Transfers data to P2MP-FTP servers
    Provides data from the file on a byte basis.
    """

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

        print("RDT_SEND")

    finally:
        sock.close()
    print("RDT SENT.\n")

#checksum():

def ticker():
    """
    """
    global timed_out
    life = TIMEOUT

    while(life > 0):
        print("LIFE: " + str(life))
        time.sleep(1)
        life -= 1
    timed_out = True

def controller(servers, port, file, MSS):
    global server_counter, seq_counter, server_dict, timed_out
    data = file.read(MSS)
    servers_amount = len(servers)
    seq_counter = 0
    first = True

    while(data != ""):
        if len(data) == MSS:
            header = Header((seq_counter).to_bytes(4, byteorder="big"), checksum(data.encode()).to_bytes(2, byteorder="big"), b'\x00\x00')
        else:
            header = Header((seq_counter).to_bytes(4, byteorder="big"), checksum(data.encode()).to_bytes(2, byteorder="big"), b'\x00\x04')

        server_counter = 0
        timed_out = False
        for hostname in servers:
            print("HOSTNAME: " + hostname)
            if first:
                server_dict[hostname] = False
            if server_dict[hostname]:
                continue
            

            t = threading.Thread(target=rdt_send, args=[header, hostname, port, data])
            t.daemon = True
            t.start()

        t = threading.Thread(target=ticker) # Starts timeout timer
        t.daemon = True
        t.start()

        first = False
        while server_counter != servers_amount or (timed_out == False):   # Loops until either the servers all acked or it times out
            pass
        if timed_out:   # If it times out, it will not skip below so it doesn't set up for the next segment
            continue

        first = True    # Resets dictionary to falses
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
