

class Header():
	"""
        Header of the segment
	"""

        def __init__(self, seq_num, checksum):
		# 32-bit sequence number
		self._seq_num = seq_num
		# 16-bit checksum of datapart, computer in the same way as the UDP checksum
                self._checksum = checksum
		# 16-bit field, indicates that this is a data packet
                self._field = 0101010101010101

	# Returns sequence number
	def get_seq_num(self):
		return self._seq_num

	# Returns checksum
	def get_checksum(self):
		return self._checksum
	# Returns string of header
	def __str__(self):
		return str(self._seq_num) + str(self._checksum) + str(self._field)
def rdt_send():
 
