import os, os.path, struct, sys

# file header layout
HDR_LGTH =			 	 36		# == 0x024
HDR_STR_LGTH =			 32		# == 0x020
HDR_FLAGS_LGTH =		  1		# one 2-byte short

class MIDISettings:

	# settings struct layout
	SETTINGS_LGTH =			340		# == 0x154
	SETTINGS_NAME_LGTH =	 41		# == 0x029
	PADDING1 =				111		# == 0x070
	LOCAL_CONTROL =			  1
	CLOCK_LGTH =			  1
	TRANSMIT_CLOCK_LGTH =	  1
	TRANSPOSE_MIDI_LGTH =  	  1
	START_STOP =  			  1
	SYSEX_MSGS =			  1		# one 2-byte short
	PADDING_LAST =			SETTINGS_LGTH - SETTINGS_NAME_LGTH - PADDING1 - LOCAL_CONTROL \
							- CLOCK_LGTH - TRANSMIT_CLOCK_LGTH - TRANSPOSE_MIDI_LGTH - START_STOP \
							- 2 * SYSEX_MSGS

	separator = '----------------------------------------------------------------------------\n'

	_sysex_labels =			('System Exclusive Message', 'Chord System Exclusive Message')
	_setting_labels =		('', 'Genos File', 'MIDI Settings', 'Clock', 'Transmit Clock',	\
		    				 'Transpose MIDI Input', 'Start/Stop',  'Local Control',		\
							 _sysex_labels[0], _sysex_labels[1])
	_setting_labels =		[f'{sl + ":":33s}' for sl in _setting_labels]		# pad labels to same width
	_setting_labels[0] =	' ' + _setting_labels[0][1:]					# replace colon with space

	_clock_labels =			('Internal', 'MIDI A', 'MIDI B', 'USB1', 'USB2', 'Wireless LAN')
	_off_on_labels =		('Off', 'On')
	_start_stop_labels =	('Song', 'Style')
	_local_ctl_labels =		((('Left', 0x10), ('Right1', 0x08), ('Right2', 0x04), ('Right3', 0x02)), \
		    				 (('Style', 0x40), ('Song', 0x80), ('M.Pad', 0x20)))
	_xmit_rcv_labels =		('Transmit', 'Receive')
	_may_be_inaccurate =	f'* "{_sysex_labels[0]}" and "{_sysex_labels[1]}"' \
							+ '\n    may be inaccurate - see Jupyter Notebook'

	def __init__(self, file_name, settings_bytes):

		self._file_name = file_name

		settings_name_bytes, self._local_control, self._clock, self._xmit_clock, \
		self._xpose_midi, self._start_stop, self._sysex_msgs = \
			struct.unpack(f'> \
		 					{self.SETTINGS_NAME_LGTH}s			\
							{self.PADDING1}x					\
		 					{self.LOCAL_CONTROL}B				\
		 					{self.CLOCK_LGTH}B					\
		 					{self.TRANSMIT_CLOCK_LGTH}B			\
		 					{self.TRANSPOSE_MIDI_LGTH}B			\
		 					{self.START_STOP}B					\
		 					{self.SYSEX_MSGS}H					\
		 					{self.PADDING_LAST}x',
						  settings_bytes)

		self.name = settings_name_bytes.decode('ascii').rstrip('\x00')

	def local_ctl(self, flags, labels):
		local_ctl_str = ''
		first = True
		local_ctl_setting = ''
		for lbl in labels:
			local_ctl_setting = lbl[0] + ':'
			if lbl[1] & flags == 0:
				local_ctl_setting += self._off_on_labels[0]
			else:
				local_ctl_setting += self._off_on_labels[1]
			local_ctl_str += f'{local_ctl_setting:11s}'
		local_ctl_str += '\n'
		return local_ctl_str

	def sysex_msgs(self, flags):
		byte_masks = (0xFF00, 0x00FF)
		sysex_msgs_str = ''
		for i in range(2):
			sysex_msgs_str += self._xmit_rcv_labels[i] + ':'
			if flags & byte_masks[i] == 0:
				sysex_msgs_str += self._off_on_labels[0]
			else:
				sysex_msgs_str += self._off_on_labels[1]
			if i == 0:
				sysex_msgs_str += ' '
		return sysex_msgs_str

	def __str__(self):

		local_ctl_str = self.local_ctl(self._local_control, self._local_ctl_labels[0])
		local_ctl_str += self._setting_labels[0]
		local_ctl_str += self.local_ctl(self._local_control, self._local_ctl_labels[1])
		
		return																					\
			f'{self._setting_labels[1]}{self._file_name}\n' + 										\
			f'{self._setting_labels[2]}{self.name}\n' + 										\
			self.separator +																	\
			f'{self._setting_labels[3]}{self._clock_labels[self._clock]}\n' +					\
			f'{self._setting_labels[4]}{self._off_on_labels[self._xmit_clock]}\n' +				\
			f'{self._setting_labels[5]}{self._off_on_labels[self._xpose_midi]}\n' +				\
			f'{self._setting_labels[6]}{self._start_stop_labels[self._start_stop]}\n' +			\
			f'{self._setting_labels[7]}{local_ctl_str}' +										\
			f'{self._setting_labels[8]}{self.sysex_msgs(self._sysex_msgs & 0x8080)}\n' +		\
			f'{self._setting_labels[9]}{self.sysex_msgs(self._sysex_msgs & 0x0808)}\n' +		\
			f'\n\n{self._may_be_inaccurate}\n'

def main(genos_file, analyze):

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
		if not analyze:
			for root, _, files in os.walk(settings_file_dir):	# delete previous directory contents
				for f in files:
					os.unlink(os.path.join(root, f))
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
			settings = MIDISettings(genos_file_name, settings_bytes)

			if analyze:
				# write out settings bytes for comparison
				settings_bytes_file = open(os.path.join(settings_file_dir, settings.name + '.stg'), 'wb')
				settings_bytes_file.write(settings_bytes)
				settings_bytes_file.close()

			# print settings info
			settings_txt_file = open(os.path.join(settings_file_dir, settings.name + '.txt'), 'w')
			sys.stdout = settings_txt_file
			print(f'{settings.name}', file=console_out)
			print(settings)
			settings_txt_file.close()

		settings_mask <<= 1

	genos_file_stream.close()

	return ''

if __name__ == '__main__':
	ret_str = main(sys.argv[1], bool(sys.argv[2]))
	if ret_str != '':
		print(f'main() -> {ret_str}')
