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
        tmp = data[i] + (data[i+1] << 8)
        chk_sum = bit_add(chk_sum, tmp)
        return ~chk_sum & 0xffff



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
        # EOT
        self._eot = bytearray(b'\x00\x00')

    # Returns sequence number
    def get_seq_num(self):
        return self._seq_num

    # Returns checksum
    def get_checksum(self):
        return self._checksum

    # Marks EOT
    def mark_eot(self):
        self._eot = bytearray(b'\x00\x04')
    
    # Returns string of header
    def to_bits(self):
        bits = bytearray()
        bits.append(self._seq_num[0])
        bits.append(self._seq_num[1])
        bits.append(self._seq_num[2])
        bits.append(self._seq_num[3])
        bits.append(self._checksum[0])
        bits.append(self._checksum[1])
        bits.append(self._field[0])
        bits.append(self._field[1])
        bits.extend(self._eot)
        return bits




# Testing to get receiver working
import socket
import sys

HOST, PORT = "localhost", 9999
string = "Test\x00\x00\x00\x00".encode()
#string = "Test\n".encode()

test_head = Header(b'\x00\x00\x00\x02', checksum(string).to_bytes(2, byteorder='big'))

test_head.mark_eot()

# SOCK_DGRAM is the socket type to use for UDP sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = test_head.to_bits()
data.extend(string)
# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().
sock.sendto(bytes(data), (HOST, PORT))
received = sock.recv(1024)


print("Sent:     {}".format(data))
print("Received: {}".format(bytearray(received)))
