import sys, socketserver, struct, threading, time, socket

__author__ = "Louis Le"
__credits__ = ["Stephen Worley", "Louis Le"]
__license__ = "GPL"
__maintainer__ = "Louis Le"
__email__ = "lle3@ncsu.edu"
__status__ = "Development"

servers_amount = 0
seq_counter = 0
server_counter = 0
server_dict = {}
lock = threading.Lock()
timed_out = False
sleep_time = 3

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

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, t=None, a=()):
        super(StoppableThread, self).__init__(target = t, args=a)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def send_packets(sock, servers, port, header, data):
    for server in servers:
        if(not server_dict[server]):
            # As you can see, there is no connect() call; UDP has no connections.
            # Instead, data is directly sent to the recipient via sendto().
            segment = header.to_bits()
            segment.extend(data.encode())

            sock.sendto(segment, (server, port))
            print("SENT: " + str(bytes(header.get_seq_num())))

def waiter(sock, servers, port):
    global server_counter, server_dict, seq_counter
    while(True):
        data, address = sock.recvfrom(1024)
        seq_num, field_1, field_2 = struct.unpack(">LHH", data)
        try:
            hostname = socket.gethostbyaddr(address[0])[0]
        except:
            hostname = address[0]
        if (seq_num == seq_counter and not server_dict[str(hostname)]):
            print("CORRECT ACK: " + str(seq_num))
            with lock:
                server_counter += 1
                server_dict[hostname] = True
            print("SERVER_COUNTER: " + str(server_counter))
            print("SERVER_DICT: " + str(server_dict))
            print("SEQ_COUNTER: " + str(seq_counter))
        else:
            print("INCORRECT ACK: " + str(seq_num))
            sys.exit()


def ticker():
    """
    """
    global timed_out, sleep_time
    time.sleep(sleep_time)

    timed_out = True

def rdt_send(sock, servers, port, header,data):
    """
    Transfers data to P2MP-FTP servers
    Provides data from the file on a byte basis.
    """
    global servers_amount, server_dict, server_counter

    t1 = StoppableThread(t=waiter, a=[sock, servers, port])
    t1.daemon = True
    t1.start()

    t2 = StoppableThread(t=send_packets, a=[sock, servers, port, header, data])
    t2.daemon = True
    t2.start()

    t3 = StoppableThread(t=ticker)
    t3.daemon = True
    t3.start()

    while(not timed_out and servers_amount != server_counter):
        pass

    

    t1.stop()
    t2.stop()
    t3.stop()

#checksum():

def controller(sock, servers, port, file, MSS):
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

        rdt_send(sock, servers, port, header, data)

        if(servers_amount == server_counter):
            for h in servers:
                server_dict[h] = False
            data = file.read(MSS)   # Reads next line
            seq_counter += 1
            server_counter = 0
        else:
            print("Timeout, sequence number = " + str(seq_counter))
            timed_out = False
            # time.sleep(5)

if __name__ == "__main__":
    """
    Main method
    """
    try:
        SERVERS, PORT, F_NAME, MSS = sys.argv[1:-3], int(sys.argv[-3]), sys.argv[-2], int(sys.argv[-1])
    except:
        print("Error in command line arguments.\
                \nShould be in the form 'p2mpclient server-1 server-2 server-3 server-port# file-name MSS\n")
        sys.exit()

    try:
        file = open(F_NAME, "r")
    except:
        print("File does not exit: " + F_NAME + "\n")
        sys.exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    controller(sock, SERVERS, PORT, file, MSS)
