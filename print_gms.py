import struct

HDR_LGTH =			36	# == 0x024
HDR_STR_LGTH =		32	# == 0x020
HDR_FLAGS_LGTH =	 1	# one 2-byte short

SETTINGS_LGTH = 340  # == 0x154
SETTINGS_NAME_LGTH = 41  # == 0x029


def main(file_name):
	print(file_name)

	# open file
	try:
		file_stream = open(file_name, 'rb')
	except FileNotFoundError:
		return f'could not open file: {file_name}'

	# read file header
	hdr_str, setting_flags = \
		struct.unpack(f'> {HDR_STR_LGTH}s {HDR_FLAGS_LGTH}H 2x',
						file_stream.read(HDR_LGTH))
	flags_str = f'{setting_flags:2X}'.zfill(4)	# 4 hex digits via zero fill if needed
	print(f'{hdr_str}, 0x{flags_str}')

	# setting_flags = 0x301

	# read individual settings
	setting_mask = 0x200
	for i in range(10):
		setting_bytes = file_stream.read(SETTINGS_LGTH)
		if setting_flags & setting_mask != 0:
			setting_name_bytes, = \
				struct.unpack(f'> {SETTINGS_NAME_LGTH}s {SETTINGS_LGTH - SETTINGS_NAME_LGTH}x',
							  setting_bytes)
			print(setting_name_bytes.decode('ascii').rstrip('\x00'))
		setting_mask >>= 1

	file_stream.close()
	return ''


if __name__ == '__main__':
	ret_str = main('genos_files/no_local.msu')
	if ret_str != '':
		print(f'main() -> {ret_str}')
