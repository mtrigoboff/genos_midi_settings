import struct

FILE_HDR_LGTH = 36  # == 0x024
SETTINGS_LGTH = 340  # == 0x154
SETTINGS_NAME_LGTH = 41  # == 0x029


def main(file_name):
    # open file
    try:
        file_stream = open(file_name, 'rb')
    except FileNotFoundError:
        return f'could not open file: {file_name}'

    # read file header
    file_hdr = file_stream.read(FILE_HDR_LGTH)

    # read individual settings
    for i in range(10):
        setting_name_bytes, = \
        	struct.unpack(f'> {SETTINGS_NAME_LGTH}s {SETTINGS_LGTH - SETTINGS_NAME_LGTH}x',
                          file_stream.read(SETTINGS_LGTH))
        print(setting_name_bytes.decode('ascii').rstrip('\x00'))

    file_stream.close()
    return ''

if __name__ == '__main__':
    main('genos_files/MIDISetupPreset.msu')
