

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
        bits.append(self._checksum[0])
        bits.append(self._checksum[1])
        print(bits)
        bits.append(self._field[0])
        bits.append(self._field[1])
        print(bits)
        return bits




# Testing to get receiver working
import socket
import sys

HOST, PORT = "localhost", 9999

test_head = Header(b'\x00\x00\x00\x00', b'\xff\xf1')

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = test_head.to_bits()
# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(bytes(test_head.to_bits()), (HOST, PORT))
received = sock.recv(1024)


print("Sent:     {}".format(data))
print("Received: {}".format(bytearray(received)))
