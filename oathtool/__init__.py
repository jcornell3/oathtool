import argparse
import base64
import binascii
import hashlib
import hmac as stdlib_hmac
import struct
import sys
import time


def hmac(key, msg, digest=hashlib.sha1):
    """HMAC implementation using standard library."""
    return stdlib_hmac.new(key, msg, digest).digest()


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


def generate_otp(key, hotp_value=None, digest=hashlib.sha1):
    """
    >>> generate_otp('MZXW6YTBOJUWU23MNU', 52276810)
    '487656'
    >>> generate_otp('MZXW6YTBOJUWU23MNU'*10, 52276810)
    '295635'
    """
    # convert HOTP to bytes
    # https://tools.ietf.org/rfc/rfc6238.txt
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
    # generate HMAC from HOTP based on key
    HMAC = hmac(key, hotp_value, digest)
    # compute hash truncation
    cut = HMAC[-1] & 0x0F
    # encode into smaller number of digits
    return '%06d' % (
        (struct.unpack('>L', HMAC[cut : cut + 4])[0] & 0x7FFFFFFF) % 1000000
    )


def get_version():
    """Get package version from importlib.metadata."""
    try:
        from importlib.metadata import version, PackageNotFoundError
        return version('oathtool')
    except (ImportError, PackageNotFoundError):
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
    parser.add_argument(
        '--totp',
        action='store_true',
        help='Generate TOTP code (default behavior, this option is for compatibility)'
    )
    parser.add_argument(
        '-b', '--base32',
        action='store_true',
        help='Indicate the secret key is Base32 encoded (validates 32-character length)'
    )
    parser.add_argument(
        '--sha256',
        action='store_true',
        help='Use SHA256 instead of SHA1 for HMAC'
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

    # Validate base32 key length when --base32 flag is provided
    if args.base32:
        cleaned_key = clean(key)
        if len(cleaned_key) != 32:
            print(f'Error: --base32 flag requires a 32-character secret key, got {len(cleaned_key)} characters', file=sys.stderr)
            sys.exit(1)

    # Select hash algorithm
    digest = hashlib.sha256 if args.sha256 else hashlib.sha1

    try:
        print(generate_otp(key, digest=digest))
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)
