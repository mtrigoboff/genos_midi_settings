import os, os.path, struct, sys

# code version number
version = [1, 0, 0]
app_hdr_str = f'Print Genos2 MIDI Settings File  ({version[0]}.{version[1]}.{version[2]})'

# file layout
FILE_LGTH =			 	 	298
HDR_LGTH =			 	 	35

class MIDISettings:

	# settings struct layout (bytes, except where noted)
	SETTINGS_LGTH =			FILE_LGTH - HDR_LGTH
	LOCAL_CONTROL =			 1		# [0]
	CLOCK =					 1		# [1]
	TRANSMIT_CLOCK =		 1		# [2]
	TRANSPOSE_MIDI = 	 	 1		# [3]
	START_STOP =  			 1		# [4]
	SYSEX_XMIT =  			 1		# [5]
	SYSEX_CHORD_XMIT =  	 1		# [6]
	SYSEX_RCV =  			 1		# [7]
	SYSEX_CHORD_RCV =  		 1		# [8]
	PADDING1 =				 4		# [9 - 12]
	TRANSMIT = 				34		# [13] (2-byte shorts)
	RECEIVE = 				32		# [70] (2-byte shorts)
	PADDING2 =				 1
	ON_BASS_NOTE =			 1		# one 4-byte int
	CHORD_DETECT =			 1		# one 4-byte int
	PADDING_LAST =			SETTINGS_LGTH - LOCAL_CONTROL - CLOCK - TRANSMIT_CLOCK - TRANSPOSE_MIDI			\
							- START_STOP - SYSEX_XMIT - SYSEX_CHORD_XMIT - SYSEX_RCV						\
							- SYSEX_CHORD_RCV - PADDING1 - 2 * TRANSMIT - 2 * RECEIVE - PADDING2			\
							- 4 * ON_BASS_NOTE - 4 * CHORD_DETECT

	seperator = '----------------------------------------------------------------------------\n'

	_sysex_labels =			('System Exclusive Message', 'Chord System Exclusive Message')
	_setting_labels =		('', 'Genos2 File', 'MIDI Settings', 'Clock', 'Transmit Clock',					\
		    				 'Transpose MIDI Input', 'Start/Stop',  'Local Control',						\
							 _sysex_labels[0], _sysex_labels[1], 'Transmit', 'Receive',						\
							 'On Bass Note', 'Chord Detect')
	_setting_labels =		[f'{sl + ":":33s}' for sl in _setting_labels]		# pad labels to same width
	_setting_labels[0] =	' ' + _setting_labels[0][1:]						# replace colon with space
	# _setting_labels[0] is a blank label to maintain identing for multiple-line setting printout

	_clock_labels =			('Internal', 'MIDI A', 'MIDI B', 'USB1', 'USB2', 'Wireless LAN')
	_off_on_labels =		('Off', 'On')
	_start_stop_labels =	('Song', 'Style')
	_local_ctl_labels =		((('Left', 0x10), ('Right1', 0x08), ('Right2', 0x04), ('Right3', 0x02)),		\
		    				 (('Style', 0x40), ('Song', 0x80), ('M.Pad', 0x20)))
	_xmit_rcv_labels =		('Transmit', 'Receive')

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

		self._local_control, self._clock, self._xmit_clock,	self._xpose_midi, self._start_stop,				\
		self._sysex_xmit, self._sysex_chord_xmit, self._sysex_rcv, self._sysex_chord_rcv,					\
		self._transmit, self._receive, self._on_bass_note, self._chord_detect =								\
			struct.unpack(
				f'> {self.LOCAL_CONTROL}B {self.CLOCK}B {self.TRANSMIT_CLOCK}B'
				+ f' {self.TRANSPOSE_MIDI}B {self.START_STOP}B'
				+ f' {self.SYSEX_XMIT}B {self.SYSEX_CHORD_XMIT}B'
				+ f' {self.SYSEX_RCV}B {self.SYSEX_CHORD_RCV}B {self.PADDING1}x'
				+ f' {2 * self.TRANSMIT}s {2 * self.RECEIVE}s {self.PADDING2}x'
				+ f' {self.ON_BASS_NOTE}I {self.CHORD_DETECT}I'
				+ f' {self.PADDING_LAST}x'
				, settings_bytes)
		
	def local_ctl(self, flags, labels):
		local_ctl_str = ''
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

	def sysex(self, xmit, rcv):
		return self._xmit_rcv_labels[0] + ':' + self._off_on_labels[xmit]									\
			   + ' ' + self._xmit_rcv_labels[1] + ':' + self._off_on_labels[rcv]

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
			app_hdr_str + '\n'																				\
			f'{self._setting_labels[1]}{self._file_name}\n' + 												\
			self.seperator +																				\
			f'{self._setting_labels[3]}{self._clock_labels[self._clock]}\n' +								\
			f'{self._setting_labels[4]}{self._off_on_labels[self._xmit_clock]}\n' +							\
			f'{self._setting_labels[5]}{self._off_on_labels[self._xpose_midi]}\n' +							\
			f'{self._setting_labels[6]}{self._start_stop_labels[self._start_stop]}\n' +						\
			f'{self._setting_labels[7]}{local_ctl_str}' +													\
			f'{self._setting_labels[8]}{self.sysex(self._sysex_xmit, self._sysex_rcv)}\n' +					\
			f'{self._setting_labels[9]}{self.sysex(self._sysex_chord_xmit, self._sysex_chord_rcv)}\n' +		\
			f'{self._setting_labels[10]}{self.transmit(self._transmit)}' +									\
			f'{self._setting_labels[11]}{self.receive(self._receive)}' +									\
			f'{self._setting_labels[12]}{self.on_bass_note_chord_detect(self._on_bass_note)}' +				\
			f'{self._setting_labels[13]}{self.on_bass_note_chord_detect(self._chord_detect)}'

def print_genos_midi_settings(genos_file, analyze=False):

	global console_out
	console_out = sys.stdout

	genos_file_path, genos_file_name = os.path.split(genos_file)
	genos_file_root, genos_file_ext = os.path.splitext(genos_file_name)

	print(app_hdr_str)
	print(f'Genos2 File: {genos_file_name}', file=console_out)

	# open Genos file
	if genos_file_ext != '.mis':
		return f'incorrect file type: "{genos_file_ext}"'
	try:
		genos_file_stream = open(genos_file, 'rb')
	except FileNotFoundError:
		return f'could not open file: "{genos_file}"'

	# read file header
	genos_file_stream.read(HDR_LGTH)

	settings_bytes = genos_file_stream.read(MIDISettings.SETTINGS_LGTH)

	# unpack settings bytes
	settings = MIDISettings(genos_file_name, settings_bytes)

	# print settings info
	settings_txt_file = open(os.path.join(genos_file_name + '.txt'), 'w')
	sys.stdout = settings_txt_file
	print(settings)
	settings_txt_file.close()
	sys.stdout = console_out

	genos_file_stream.close()

	return ''

if __name__ == '__main__':
	if len(sys.argv) > 2:
		ret_str = print_genos_midi_settings(sys.argv[1], True)
	else:
		ret_str = print_genos_midi_settings(sys.argv[1])
	if ret_str != '':
		print(f'print_genos_midi_settings() -> {ret_str}', file=console_out)
