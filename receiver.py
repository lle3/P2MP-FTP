
class ACK():
	"""
	Acknowlegement segment
	"""

	def __init__(self, seq_num):
		# 32-bit sequence number that is being ACKed
		self._seq_num = seq_num
		# 16-bit field that is all zeroes
		self._field_1 = 0000000000000000
		# 16-bit field indicates that it is an ACK packe
		self._field_2 = 1010101010101010
	# Returns sequence Number
	def get_seq_num(self):
		return self._seq_num

	# Return string of ACK segment
	def __str__(self):
		return str(self._seq_num) + str(_field_1) + str(_field_2)
