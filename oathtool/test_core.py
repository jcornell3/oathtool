"""
Unit tests for oathtool core functions.

Tests the core cryptographic and utility functions.
"""

import hashlib
import hmac as stdlib_hmac
from unittest.mock import patch

import pytest

import oathtool


class TestHMAC:
    """Tests for the HMAC-SHA1 implementation."""

    def test_hmac_standard_key_message(self):
        """HMAC with normal key/message matches stdlib."""
        key = b'key'
        msg = b'message'
        result = oathtool.hmac(key, msg)
        expected = stdlib_hmac.new(key, msg, hashlib.sha1).digest()
        assert result == expected
        assert len(result) == 20  # SHA1 produces 20 bytes

    def test_hmac_long_key(self):
        """HMAC with key > 64 bytes (SHA1 block size)."""
        key = b'a' * 100
        msg = b'test'
        result = oathtool.hmac(key, msg)
        expected = stdlib_hmac.new(key, msg, hashlib.sha1).digest()
        assert result == expected

    def test_hmac_empty_inputs(self):
        """HMAC with empty key and message."""
        # Empty message
        assert oathtool.hmac(b'key', b'') == stdlib_hmac.new(b'key', b'', hashlib.sha1).digest()
        # Empty key
        assert oathtool.hmac(b'', b'msg') == stdlib_hmac.new(b'', b'msg', hashlib.sha1).digest()


class TestPad:
    """Tests for the Base32 padding function."""

    @pytest.mark.parametrize("input_val,expected", [
        ('foo', 'foo====='),
        ('MZXW6YTBOJUWU23MNU', 'MZXW6YTBOJUWU23MNU======'),
        ('ABCDEFGH', 'ABCDEFGH'),  # exact multiple, no padding needed
        ('', ''),  # empty string
    ])
    def test_pad_default_size(self, input_val, expected):
        """Test padding with default block size of 8."""
        assert oathtool.pad(input_val) == expected

    @pytest.mark.parametrize("input_val,size,expected", [
        ('ABC', 4, 'ABC='),
        ('ABCD', 4, 'ABCD'),
        ('ABC', 5, 'ABC=='),
    ])
    def test_pad_custom_sizes(self, input_val, size, expected):
        """Test padding with custom block sizes."""
        assert oathtool.pad(input_val, size=size) == expected


class TestClean:
    """Tests for the input sanitization function."""

    @pytest.mark.parametrize("input_val,expected", [
        ('AB CD EF', 'ABCDEF'),
        ('ABCDEF', 'ABCDEF'),
        ('AB  CD', 'ABCD'),
        (' ABCD ', 'ABCD'),
        ('   ', ''),
        ('', ''),
        ('AB\tCD\n', 'AB\tCD\n'),  # only spaces removed, not tabs/newlines
    ])
    def test_clean(self, input_val, expected):
        """Test space removal from input strings."""
        assert oathtool.clean(input_val) == expected


class TestGenerateOTP:
    """Tests for the OTP generation function."""

    def test_generate_otp_known_vectors(self):
        """Known TOTP test vectors from doctests."""
        assert oathtool.generate_otp('MZXW6YTBOJUWU23MNU', 52276810) == '487656'
        assert oathtool.generate_otp('MZXW6YTBOJUWU23MNU' * 10, 52276810) == '295635'

    def test_generate_otp_deterministic(self):
        """Same key and counter always produce same 6-digit code."""
        key = 'JBSWY3DPEHPK3PXP'
        code1 = oathtool.generate_otp(key, hotp_value=12345)
        code2 = oathtool.generate_otp(key, hotp_value=12345)
        assert code1 == code2
        assert len(code1) == 6
        assert code1.isdigit()

    def test_generate_otp_different_counters(self):
        """Same key with different counters produces different codes."""
        key = 'JBSWY3DPEHPK3PXP'
        codes = [oathtool.generate_otp(key, hotp_value=i) for i in range(1, 4)]
        assert len(set(codes)) == 3  # All different

    def test_generate_otp_key_normalization(self):
        """Keys with spaces and lowercase are normalized."""
        result1 = oathtool.generate_otp('MZXW6YTBOJUWU23MNU', 52276810)
        result2 = oathtool.generate_otp('MZXW 6YTB OJUW U23M NU', 52276810)
        result3 = oathtool.generate_otp('mzxw6ytbojuwu23mnu', 52276810)
        assert result1 == result2 == result3

    def test_generate_otp_invalid_base32(self):
        """Invalid base32 characters raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            oathtool.generate_otp('INVALID!!!', 1)
        assert 'Invalid secret key' in str(exc_info.value)

    def test_generate_otp_edge_cases(self):
        """Edge cases: empty key, very short key, very long key."""
        # All should produce valid 6-digit codes
        for key in ['', 'AAAA', 'A' * 1000]:
            result = oathtool.generate_otp(key, 1)
            assert len(result) == 6
            assert result.isdigit()

    @patch('time.time')
    def test_generate_otp_time_window(self, mock_time):
        """Verify 30-second time window for TOTP."""
        mock_time.return_value = 1234567890
        result1 = oathtool.generate_otp('JBSWY3DPEHPK3PXP')

        # Same 30-second window should produce same code
        mock_time.return_value = 1234567890 + 15
        result2 = oathtool.generate_otp('JBSWY3DPEHPK3PXP')
        assert result1 == result2

        # Next 30-second window should produce different code
        mock_time.return_value = 1234567890 + 30
        result3 = oathtool.generate_otp('JBSWY3DPEHPK3PXP')
        assert result3 != result1  # Different window, different code


class TestRFCCompliance:
    """Tests for RFC 4226 (HOTP) and RFC 6238 (TOTP) compliance."""

    def test_rfc4226_hotp_test_vectors(self):
        """RFC 4226 Appendix D test vectors (counters 1-9)."""
        # Secret: "12345678901234567890" in base32
        secret = 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ'
        expected = {
            1: '287082', 2: '359152', 3: '969429',
            4: '338314', 5: '254676', 6: '287922',
            7: '162583', 8: '399871', 9: '520489',
        }
        for counter, expected_code in expected.items():
            assert oathtool.generate_otp(secret, counter) == expected_code

    def test_rfc6238_totp_test_vectors(self):
        """RFC 6238 Appendix B test vectors (SHA1)."""
        secret = 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ'
        test_vectors = {
            59: '287082', 1111111109: '081804', 1111111111: '050471',
            1234567890: '005924', 2000000000: '279037', 20000000000: '353130',
        }
        for timestamp, expected_code in test_vectors.items():
            counter = timestamp // 30
            result = oathtool.generate_otp(secret, counter)
            assert result == expected_code
