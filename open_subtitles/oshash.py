import os
import struct
import sys


class File(object):
	_longlongformat = 'q'
	_word_size = struct.calcsize(_longlongformat)

	def __init__(self, path):
		self.path = path
		self.size = os.path.getsize(path)

	def get_hash(self):
		if self.size < 65536 * 2:
			raise ValueError('File is too small')

		with open(self.path, "rb") as f:
			hash = self.size
			hash += self._hash_part(f)

			f.seek(max(0, int(self.size) - 65536), 0)
			hash += self._hash_part(f)

			hash &= 0xFFFFFFFFFFFFFFFF

		return "%016x" % hash

	def _hash_part(self, f):
		result = 0

		for x in range(65536 // self._word_size):
			buffer = f.read(self._word_size)
			(l_value, ) = struct.unpack(self._longlongformat, buffer)
			result = (result + l_value) & 0xFFFFFFFFFFFFFFFF

		return result


if __name__ == "__main__":
	f = File(sys.argv[1])
	print(f.get_hash())
