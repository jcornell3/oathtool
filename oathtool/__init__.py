import argparse
import base64
import binascii
import hashlib
import string
import struct
import sys
import time

trans_5C = bytes(x ^ 0x5C for x in range(256))
trans_36 = bytes(x ^ 0x36 for x in range(256))

# https://tools.ietf.org/html/rfc3548.html#page-6
b32_lookup = {letter: ord(letter) - ord('A') for letter in string.ascii_uppercase}

b32_lookup.update((str(number), number + 24) for number in range(2, 8))


def hmac(key, msg):
    # https://www.ietf.org/rfc/rfc2104.txt - sha1, 64 block
    outer = hashlib.sha1()
    inner = hashlib.sha1()
    if len(key) > 64:
        key = hashlib.sha1(key).digest()
    key = key + b'\x00' * (64 - len(key))
    outer.update(key.translate(trans_5C))
    inner.update(key.translate(trans_36))
    inner.update(msg)
    outer.update(inner.digest())
    return outer.digest()


def pad(input, size=8):
    """
    >>> pad('foo')
    'foo====='
    >>> pad('MZXW6YTBOJUWU23MNU')
    'MZXW6YTBOJUWU23MNU======'
    """
    quanta, remainder = divmod(len(input), size)
    padding = '=' * ((size - remainder) % size)
    return input + padding


def clean(input):
    return input.replace(' ', '')


def generate_otp(key, hotp_value=None):
    """
    >>> generate_otp('MZXW6YTBOJUWU23MNU', 52276810)
    '487656'
    >>> generate_otp('MZXW6YTBOJUWU23MNU'*10, 52276810)
    '295635'
    """
    # convert HOTP to bytes
    # https://tools.ietf.org/rfc/rfc6238.txt
    # http://opensource.apple.com//source/python/python-3/python/Modules/structmodule.c
    hotp_value = struct.pack('>q', hotp_value or int(time.time() / 30))
    # convert base32 key to bytes
    try:
        key = base64.b32decode(pad(clean(key)), casefold=True)
    except binascii.Error as e:
        raise ValueError(
            f"Invalid secret key: {e}\n"
            "Secret keys must be valid Base32 format (A-Z, 2-7).\n"
            "Example: JBSWY3DPEHPK3PXP"
        )
    # generate HMAC-SHA1 from HOTP based on key
    HMAC = hmac(key, hotp_value)
    # compute hash truncation
    cut = HMAC[-1] & 0x0F
    # encode into smaller number of digits
    return '%06d' % (
        (struct.unpack('>L', HMAC[cut : cut + 4])[0] & 0x7FFFFFFF) % 1000000
    )


def get_version():
    """Get package version from importlib.metadata."""
    try:
        from importlib.metadata import version
        return version('oathtool')
    except Exception:
        return 'unknown'


def main():
    parser = argparse.ArgumentParser(
        description='Generate TOTP (Time-based One-Time Password) codes',
        epilog='Examples:\n'
               '  oathtool JBSWY3DPEHPK3PXP\n'
               '  echo JBSWY3DPEHPK3PXP | oathtool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        'key',
        nargs='?',
        help='Base32-encoded secret key (e.g., JBSWY3DPEHPK3PXP). '
             'If not provided, reads from stdin.'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'oathtool {get_version()}'
    )

    args = parser.parse_args()

    # Get key from stdin if not provided as argument
    if not sys.stdin.isatty() and not args.key:
        key = sys.stdin.read().strip()
    elif args.key:
        key = args.key
    else:
        parser.error('provide secret key as argument or via stdin')

    if not key:
        parser.error('secret key cannot be empty')

    try:
        print(generate_otp(key))
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
