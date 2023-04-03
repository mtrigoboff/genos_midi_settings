import struct

HDR_LGTH = 36  # == 0x024
HDR_STR_LGTH = 32  # == 0x020
HDR_FLAGS_LGTH = 1	# one 2-byte short

SETTINGS_LGTH = 340  # == 0x154
SETTINGS_NAME_LGTH = 41  # == 0x029


def main(file_name):
    # open file
    try:
        file_stream = open(file_name, 'rb')
    except FileNotFoundError:
        return f'could not open file: {file_name}'

    # read file header
    hdr_str, setting_flags = \
        struct.unpack(f'> {HDR_STR_LGTH}s {HDR_FLAGS_LGTH}H 2x',
                      file_stream.read(HDR_LGTH))
    print(f'{hdr_str}, 0x{setting_flags:02X}')

    # read individual settings
    for i in range(10):
        setting_name_bytes, = \
            struct.unpack(f'> {SETTINGS_NAME_LGTH}s {SETTINGS_LGTH - SETTINGS_NAME_LGTH}x',
                          file_stream.read(SETTINGS_LGTH))
        print(setting_name_bytes.decode('ascii').rstrip('\x00'))

    file_stream.close()
    return ''


if __name__ == '__main__':
    main('genos_files/no_local.msu')
