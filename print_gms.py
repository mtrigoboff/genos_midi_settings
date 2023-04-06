import os, os.path, struct, sys

HDR_LGTH =			36	# == 0x024
HDR_STR_LGTH =		32	# == 0x020
HDR_FLAGS_LGTH =	 1	# one 2-byte short

SETTINGS_LGTH = 340  # == 0x154
SETTINGS_NAME_LGTH = 41  # == 0x029


def main(genos_file):

	console_out = sys.stdout

	genos_file_path, genos_file_name = os.path.split(genos_file)
	genos_file_root, genos_file_ext = os.path.splitext(genos_file_name)
	print(genos_file_root, file=console_out)

	# open Genos file
	if genos_file_ext != '.msu':
		return 'incorrect file type'
	try:
		genos_file_stream = open(genos_file, 'rb')
	except FileNotFoundError:
		return f'could not open file: {genos_file_path}'

	settings_file_dir = os.path.join(genos_file_path, genos_file_root)
	if os.path.isdir(settings_file_dir):
		for root, _, files in os.walk(settings_file_dir):	# delete previous directory contents
			for f in files:
				os.unlink(os.path.join(root, f))
	else:
		os.mkdir(settings_file_dir)

	# read file header
	hdr_str, setting_flags = \
		struct.unpack(f'> {HDR_STR_LGTH}s {HDR_FLAGS_LGTH}H 2x',
					  genos_file_stream.read(HDR_LGTH))
	flags_str = f'{setting_flags:2X}'.zfill(4)				# 4 hex digits via zero fill if needed
	print(f'{hdr_str}, 0x{flags_str}')

	# setting_flags = 0x301

	# read individual settings
	# (settings slots in file are filled in reverse order from end of file)
	setting_mask = 0x0001
	for i in range(10):
		setting_bytes = genos_file_stream.read(SETTINGS_LGTH)
		if setting_flags & setting_mask != 0:
			setting_name_bytes, = \
				struct.unpack(f'> {SETTINGS_NAME_LGTH}s {SETTINGS_LGTH - SETTINGS_NAME_LGTH}x',
							  setting_bytes)
			setting_name = setting_name_bytes.decode('ascii').rstrip('\x00')
			setting_file = open(os.path.join(settings_file_dir, setting_name + '.txt'), 'w')
			sys.stdout = setting_file
			print(f'{genos_file_name}: {setting_name}')
			print(f'{genos_file_name}: {setting_name}', file=console_out)
			setting_file.close()
		setting_mask <<= 1

	genos_file_stream.close()
	return ''


if __name__ == '__main__':
	ret_str = main('clock_files/clock.msu')
	if ret_str != '':
		print(f'main() -> {ret_str}')
