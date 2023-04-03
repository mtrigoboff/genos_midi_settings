import struct

FILE_HDR_LGTH =			0x024
MIDI_SETTINGS_LGTH =	0x154

def main(file_name):
	# open file
	try:
		file_stream = open(file_name, 'rb')
	except FileNotFoundError:
		print(f'could not open file: {file_name}')
		return

	# read file header
	file_hdr = file_stream.read(FILE_HDR_LGTH)

	# read individual settings
	for i in range(10):
		setting_name_bytes, = struct.unpack('> 32s 308x', file_stream.read(MIDI_SETTINGS_LGTH))
		print(setting_name_bytes.decode('ascii').rstrip('\x00'))


	file_stream.close()

if __name__ == '__main__':
    main('genos_files/MIDISetupPreset.msu')