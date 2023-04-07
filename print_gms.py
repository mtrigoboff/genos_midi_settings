import os, os.path, struct, sys

# file header layout
HDR_LGTH =			 	 36		# == 0x024
HDR_STR_LGTH =			 32		# == 0x020
HDR_FLAGS_LGTH =		  1		# one 2-byte short

class MIDISettings:

	# settings struct layout
	SETTINGS_LGTH =			340		# == 0x154
	SETTINGS_NAME_LGTH =	 41		# == 0x029
	PADDING1 =				112		# == 0x070
	CLOCK_LGTH =			  1
	TRANSMIT_CLOCK_LGTH =	  1
	TRANSPOSE_MIDI_LGTH =  	  1
	START_STOP =  			  1
	PADDING_LAST =			SETTINGS_LGTH - SETTINGS_NAME_LGTH - PADDING1 \
							- CLOCK_LGTH - TRANSMIT_CLOCK_LGTH - TRANSPOSE_MIDI_LGTH - START_STOP

	separator = '-----------------------------------\n'

	_clock_labels = ('Internal', 'MIDI A', 'MIDI B', 'USB1', 'USB2', 'Wireless LAN')
	_off_on_labels = ('Off', 'On')
	_start_stop_labels = ('Song', 'Style')

	def __init__(self, settings_bytes):

		settings_name_bytes, self._clock, self._xmit_clock, self._xpose_midi, self._start_stop = \
			struct.unpack(f'> \
		 					{self.SETTINGS_NAME_LGTH}s \
							{self.PADDING1}x \
		 					{self.CLOCK_LGTH}B \
		 					{self.TRANSMIT_CLOCK_LGTH}B \
		 					{self.TRANSPOSE_MIDI_LGTH}B \
		 					{self.START_STOP}B \
		 					{self.PADDING_LAST}x',
						  settings_bytes)

		self.name = settings_name_bytes.decode('ascii').rstrip('\x00')

	def __str__(self):
		return f'{"Genos MIDI Setting:":26s} {self.name}\n' + 								\
			   self.separator +																\
			   f'{"Clock:":26s} {self._clock_labels[self._clock]}\n' +						\
			   f'{"Transmit Clock:":26s} {self._off_on_labels[self._xmit_clock]}\n'			\
			   f'{"Transpose MIDI Input:":26s} {self._off_on_labels[self._xpose_midi]}\n'	\
			   f'{"Start/Stop:":26s} {self._start_stop_labels[self._start_stop]}\n'

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

	# read file header
	hdr_str, settings_flags = \
		struct.unpack(f'> {HDR_STR_LGTH}s {HDR_FLAGS_LGTH}H 2x',
					  genos_file_stream.read(HDR_LGTH))
	flags_str = f'{settings_flags:2X}'.zfill(4)				# 4 hex digits via zero fill if needed
	print(f'{hdr_str}, 0x{flags_str}')

	# set up directory for output files
	settings_file_dir = os.path.join(genos_file_path, genos_file_root)
	if os.path.isdir(settings_file_dir):
		# for root, _, files in os.walk(settings_file_dir):	# delete previous directory contents
		# 	for f in files:
		# 		os.unlink(os.path.join(root, f))
		pass
	else:
		os.mkdir(settings_file_dir)

	# setting_flags = 0x301

	# read individual settings
	# (settings slots in file are filled in reverse order from end of file)
	settings_mask = 0x0001
	for i in range(10):
		settings_bytes = genos_file_stream.read(MIDISettings.SETTINGS_LGTH)
		if settings_flags & settings_mask != 0:

			# unpack settings bytes
			settings = MIDISettings(settings_bytes)

			# write out settings bytes for comparison
			settings_bytes_file = open(os.path.join(settings_file_dir, settings.name + '.stg'), 'wb')
			settings_bytes_file.write(settings_bytes)
			settings_bytes_file.close()

			# print settings info
			settings_txt_file = open(os.path.join(settings_file_dir, settings.name + '.txt'), 'w')
			sys.stdout = settings_txt_file
			print(f'{genos_file_name}: {settings.name}')
			print(settings)
			print(f'{genos_file_name}: {settings.name}', file=console_out)
			settings_txt_file.close()

		settings_mask <<= 1

	genos_file_stream.close()

	return ''

if __name__ == '__main__':
	ret_str = main(sys.argv[1])
	if ret_str != '':
		print(f'main() -> {ret_str}')
