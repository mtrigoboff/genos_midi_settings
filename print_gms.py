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
	SYSEX_MSGS =			  1		# 2-byte short
	TRANSMIT = 				 34		# 2-byte shorts
	RECEIVE = 				 32		# 2-byte shorts
	PADDING2 =				  1
	ON_BASS_NOTE =			  1		# one 4-byte int
	CHORD_DETECT =			  1		# one 4-byte int
	PADDING_LAST =			SETTINGS_LGTH - SETTINGS_NAME_LGTH - PADDING1 - LOCAL_CONTROL					\
							- CLOCK_LGTH - TRANSMIT_CLOCK_LGTH - TRANSPOSE_MIDI_LGTH - START_STOP			\
							- 2 * SYSEX_MSGS - 2 * TRANSMIT - 2 * RECEIVE - PADDING2						\
							- 4 * ON_BASS_NOTE - 4 * CHORD_DETECT

	separator = '----------------------------------------------------------------------------\n'

	_sysex_labels =			('System Exclusive Message', 'Chord System Exclusive Message')
	_setting_labels =		('', 'Genos File', 'MIDI Settings', 'Clock', 'Transmit Clock',					\
		    				 'Transpose MIDI Input', 'Start/Stop',  'Local Control',						\
							 _sysex_labels[0], _sysex_labels[1], 'Transmit', 'Receive',						\
							 'On Bass Note', 'Chord Detect')
	_setting_labels =		[f'{sl + ":":33s}' for sl in _setting_labels]		# pad labels to same width
	_setting_labels[0] =	' ' + _setting_labels[0][1:]						# replace colon with space

	_clock_labels =			('Internal', 'MIDI A', 'MIDI B', 'USB1', 'USB2', 'Wireless LAN')
	_off_on_labels =		('Off', 'On')
	_start_stop_labels =	('Song', 'Style')
	_local_ctl_labels =		((('Left', 0x10), ('Right1', 0x08), ('Right2', 0x04), ('Right3', 0x02)),		\
		    				 (('Style', 0x40), ('Song', 0x80), ('M.Pad', 0x20)))
	_xmit_rcv_labels =		('Transmit', 'Receive')

	_may_be_inaccurate =	f'* "{_sysex_labels[0]}" and "{_sysex_labels[1]}"'								\
							+ '\n    may be inaccurate due to Genos bug - see Jupyter Notebook'
	
	_xmit_part_labels =		['Off'] + [f'Right{i}' for i in range(1, 4)]									\
							+ ['Left', 'Upper', 'Lower']													\
							+ [f'Multi Pad{i}' for i in range(1, 5)]										\
							+ [f'Style Rhythm{i}' for i in range(1, 3)]										\
							+ ['Style Bass']																\
							+ [f'Style Chord{i}' for i in range(1, 3)]										\
							+ ['Style Pad']																	\
							+ [f'Style Phrase{i}' for i in range(1, 3)]										\
							+ [f'Song Ch{i}' for i in range(1, 17)]
	
	_rcv_part_labels =		['Off', 'Song'] + [f'Right{i}' for i in range(1, 4)]							\
							+ ['Left', 'Keyboard'] + [f'Style Rhythm{i}' for i in range(1, 3)]				\
							+ ['Style Bass'] + [f'Style Chord{i}' for i in range(1, 3)]						\
							+ ['Style Pad'] + [f'Style Phrase{i}' for i in range(1, 3)]						\
							+ [f'Extra Part{i}' for i in range(1, 6)]
	
	_channel_labels =		['Off'] + [f'Port{p} Ch{c}' for p in range(1, 3) for c in range(1, 17)]

	def __init__(self, file_name, settings_bytes):

		self._file_name = file_name

		settings_name_bytes, self._local_control, self._clock, self._xmit_clock,							\
		self._xpose_midi, self._start_stop, self._sysex_msgs, self._transmit, self._receive,				\
		self._on_bass_note, self._chord_detect =															\
			struct.unpack(f'> 																				\
		 					{self.SETTINGS_NAME_LGTH}s														\
							{self.PADDING1}x																\
		 					{self.LOCAL_CONTROL}B															\
		 					{self.CLOCK_LGTH}B																\
		 					{self.TRANSMIT_CLOCK_LGTH}B														\
		 					{self.TRANSPOSE_MIDI_LGTH}B														\
		 					{self.START_STOP}B																\
		 					{self.SYSEX_MSGS}H																\
							{2 * self.TRANSMIT}s															\
							{2 * self.RECEIVE}s																\
							{self.PADDING2}x																\
							{self.ON_BASS_NOTE}I															\
							{self.CHORD_DETECT}I															\
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
				sysex_msgs_str += f'{self._off_on_labels[0]:3s}'
			else:
				sysex_msgs_str += f'{self._off_on_labels[1]:3s}'
			if i == 0:
				sysex_msgs_str += ' '
		return sysex_msgs_str
	
	def transmit(self, flags):
		part_channel_str = ''
		c = 0
		for part_label in self._xmit_part_labels[1:]:
			if c > 0:
				part_channel_str += self._setting_labels[0]
			part_channel_str += f'{part_label:15}{self._channel_labels[flags[c]]}\n'
			c += 2
		return part_channel_str

	def receive(self, flags):
		part_labels = self._rcv_part_labels
		channel_part_str = ''
		p = 0
		for channel_label in self._channel_labels[1:]:
			if p > 0:
				channel_part_str += self._setting_labels[0]
			channel_part_str += f'{channel_label:15}{part_labels[flags[p]]}\n'
			p += 2
			if p == 32:				# Port2 does not have Song option
				part_labels = part_labels[1:2] + part_labels[2:]
		return channel_part_str

	def on_bass_note_chord_detect(self, flags):

		def obn_cd_port(self, flags):
			mask = 0x0001
			obn_cd_port_str = ''
			for i in range(1, 17):
				if i == 9:
					obn_cd_port_str += '\n' + self._setting_labels[0] + spacer
				obn_cd_port_str += f'{i:2d}:'
				if flags & mask == 0:
					obn_cd_port_str += f'{self._off_on_labels[0]:3s}'
				else:
					obn_cd_port_str += f'{self._off_on_labels[1]:3s}'
				obn_cd_port_str += ' '
				mask <<= 1
			return obn_cd_port_str

		spacer = '      '
		mask = 0x00000001
		obn_cd_str = 'Port1:'
		obn_cd_str += obn_cd_port(self, flags & 0x0000FFFF)
		obn_cd_str += '\n' + self._setting_labels[0] + 'Port2:'
		obn_cd_str += obn_cd_port(self, (flags & 0xFFFF0000) >> 16) + spacer
		obn_cd_str += '\n'
		return obn_cd_str

	def __str__(self):

		local_ctl_str = self.local_ctl(self._local_control, self._local_ctl_labels[0])	 					\
						+ self._setting_labels[0]															\
						+ self.local_ctl(self._local_control, self._local_ctl_labels[1])
		
		return																								\
			f'{self._setting_labels[1]}{self._file_name}\n' + 												\
			f'{self._setting_labels[2]}{self.name}\n' + 													\
			self.separator +																				\
			f'{self._setting_labels[3]}{self._clock_labels[self._clock]}\n' +								\
			f'{self._setting_labels[4]}{self._off_on_labels[self._xmit_clock]}\n' +							\
			f'{self._setting_labels[5]}{self._off_on_labels[self._xpose_midi]}\n' +							\
			f'{self._setting_labels[6]}{self._start_stop_labels[self._start_stop]}\n' +						\
			f'{self._setting_labels[7]}{local_ctl_str}' +													\
			f'{self._setting_labels[8]}{self.sysex_msgs(self._sysex_msgs & 0x8080)}\n' +					\
			f'{self._setting_labels[9]}{self.sysex_msgs(self._sysex_msgs & 0x0808)}\n' +					\
			f'{self._setting_labels[10]}{self.transmit(self._transmit)}' +									\
			f'{self._setting_labels[11]}{self.receive(self._receive)}' +									\
			f'{self._setting_labels[12]}{self.on_bass_note_chord_detect(self._on_bass_note)}' +				\
			f'{self._setting_labels[13]}{self.on_bass_note_chord_detect(self._chord_detect)}' +				\
			f'\n\n{self._may_be_inaccurate}'

def main(genos_file, analyze=False):

	global console_out
	console_out = sys.stdout

	genos_file_path, genos_file_name = os.path.split(genos_file)
	genos_file_root, genos_file_ext = os.path.splitext(genos_file_name)
	print(f'Genos File: {genos_file_name}', file=console_out)

	# open Genos file
	if genos_file_ext != '.msu':
		return f'incorrect file type: "{genos_file_ext}"'
	try:
		genos_file_stream = open(genos_file, 'rb')
	except FileNotFoundError:
		return f'could not open file: "{genos_file}"'

	# read file header
	hdr_str, settings_flags = \
		struct.unpack(f'> {HDR_STR_LGTH}s {HDR_FLAGS_LGTH}H 2x',
					  genos_file_stream.read(HDR_LGTH))
	flags_str = f'{settings_flags:2X}'.zfill(4)				# 4 hex digits via zero fill if needed
	if analyze:
		print(f'{hdr_str}, 0x{flags_str}', file=console_out)

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
			print(f'Setting:    {settings.name}', file=console_out)
			print(settings)
			settings_txt_file.close()

		settings_mask <<= 1

	genos_file_stream.close()

	return ''

if __name__ == '__main__':
	if len(sys.argv) > 2:
		ret_str = main(sys.argv[1], True)
	else:
		ret_str = main(sys.argv[1])
	if ret_str != '':
		print(f'main() -> {ret_str}', file=console_out)
