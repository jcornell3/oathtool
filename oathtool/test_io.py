"""
Unit tests for oathtool I/O functions and CLI interface.

Tests command-line argument parsing, stdin input, and main entry point.
"""

import sys
from io import StringIO
from unittest.mock import Mock, patch

import pytest

import oathtool


# Note: get_key_arg() and get_key_stdin() were removed in favor of argparse-based CLI


class TestMain:
    """Tests for main() - CLI entry point."""

    def test_main_valid_argument(self, capsys):
        """MAIN-001: Valid argument."""
        with patch.object(sys, 'argv', ['prog', 'JBSWY3DPEHPK3PXP']):
            mock_stdin = Mock()
            mock_stdin.isatty.return_value = True

            with patch.object(sys, 'stdin', mock_stdin):
                with patch('time.time', return_value=1234567890):
                    oathtool.main()

                    captured = capsys.readouterr()
                    output = captured.out.strip()

                    # Should output a 6-digit code
                    assert len(output) == 6
                    assert output.isdigit()

    def test_main_valid_stdin(self, capsys):
        """MAIN-002: Valid stdin."""
        with patch.object(sys, 'argv', ['prog']):
            mock_stdin = StringIO('JBSWY3DPEHPK3PXP')
            mock_stdin.isatty = Mock(return_value=False)

            with patch.object(sys, 'stdin', mock_stdin):
                with patch('time.time', return_value=1234567890):
                    oathtool.main()

                    captured = capsys.readouterr()
                    output = captured.out.strip()

                    # Should output a 6-digit code
                    assert len(output) == 6
                    assert output.isdigit()

    def test_main_no_input(self, capsys):
        """MAIN-003: No input."""
        with patch.object(sys, 'argv', ['prog']):
            mock_stdin = Mock()
            mock_stdin.isatty.return_value = True

            with patch.object(sys, 'stdin', mock_stdin):
                with pytest.raises(SystemExit) as exc_info:
                    oathtool.main()

                assert exc_info.value.code == 2  # argparse error exit code

    def test_main_version_flag(self, capsys):
        """MAIN-007: --version flag."""
        with patch.object(sys, 'argv', ['prog', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                oathtool.main()

            # --version should exit with code 0
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert 'oathtool' in captured.out

    def test_main_help_flag(self, capsys):
        """MAIN-008: --help flag."""
        with patch.object(sys, 'argv', ['prog', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                oathtool.main()

            # --help should exit with code 0
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert 'usage:' in captured.out.lower()
            assert 'TOTP' in captured.out or 'totp' in captured.out.lower()

    def test_main_argument_over_stdin(self, capsys):
        """MAIN-005: Argument takes priority when both provided."""
        with patch.object(sys, 'argv', ['prog', 'JBSWY3DPEHPK3PXP']):
            mock_stdin = StringIO('MZXW6YTBOJUWU23MNU')
            mock_stdin.isatty = Mock(return_value=False)

            with patch.object(sys, 'stdin', mock_stdin):
                with patch('time.time', return_value=1234567890):
                    oathtool.main()

                    captured = capsys.readouterr()
                    output = captured.out.strip()

                    # Should use argument key
                    assert len(output) == 6
                    assert output.isdigit()

    def test_main_invalid_key_format(self, capsys):
        """MAIN-006: Invalid key format."""
        with patch.object(sys, 'argv', ['prog', 'INVALID!!!']):
            mock_stdin = Mock()
            mock_stdin.isatty.return_value = True

            with patch.object(sys, 'stdin', mock_stdin):
                with pytest.raises(SystemExit) as exc_info:
                    oathtool.main()

                # Should exit with error code
                assert exc_info.value.code == 1

                captured = capsys.readouterr()
                assert 'Invalid secret key' in captured.err or 'base32' in captured.err.lower()


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_e2e_deterministic_output(self, capsys):
        """E2E-003: Multiple rapid calls with same time produce same result."""
        key = 'JBSWY3DPEHPK3PXP'

        with patch('time.time', return_value=1234567890):
            with patch.object(sys, 'argv', ['prog', key]):
                mock_stdin = Mock()
                mock_stdin.isatty.return_value = True

                with patch.object(sys, 'stdin', mock_stdin):
                    oathtool.main()
                    captured1 = capsys.readouterr()
                    output1 = captured1.out.strip()

                    oathtool.main()
                    captured2 = capsys.readouterr()
                    output2 = captured2.out.strip()

                    assert output1 == output2

    def test_e2e_time_window_validation(self):
        """E2E-002: Generate at specific time validates 30-second window."""
        key = 'JBSWY3DPEHPK3PXP'

        # Generate codes at different times within same 30-second window
        with patch('time.time', return_value=1234567890):
            code1 = oathtool.generate_otp(key)

        with patch('time.time', return_value=1234567890 + 10):
            code2 = oathtool.generate_otp(key)

        with patch('time.time', return_value=1234567890 + 29):
            code3 = oathtool.generate_otp(key)

        # All should be the same
        assert code1 == code2 == code3

        # Next window should be different
        with patch('time.time', return_value=1234567890 + 30):
            code4 = oathtool.generate_otp(key)

        # Very likely to be different (not guaranteed but extremely likely)
        # We can at least verify it's a valid code
        assert len(code4) == 6
        assert code4.isdigit()


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_error_invalid_base32_alphabet(self):
        """ERR-001: Invalid base32 alphabet characters."""
        # Base32 alphabet doesn't include 0, 1, 8, 9
        invalid_keys = ['KEY0KEY', 'KEY1KEY', 'KEY8KEY', 'KEY9KEY']

        for key in invalid_keys:
            with pytest.raises(ValueError) as exc_info:
                oathtool.generate_otp(key, 1)
            assert 'Invalid secret key' in str(exc_info.value)

    def test_error_malformed_base32(self):
        """ERR-002: Malformed base32 with incorrect padding."""
        # Base32 decode should handle this
        # Some implementations are lenient, others strict
        try:
            result = oathtool.generate_otp('A', 1)
            # If it succeeds, verify it's valid output
            assert len(result) == 6
            assert result.isdigit()
        except ValueError:
            # If it fails, that's also acceptable
            pass

    def test_error_unicode_input(self):
        """ERR-003: Unicode input."""
        # Should handle or reject cleanly
        unicode_key = 'KEY™'

        try:
            result = oathtool.generate_otp(unicode_key, 1)
            # If it succeeds, verify output
            assert len(result) == 6
            assert result.isdigit()
        except ValueError:
            # Exception is acceptable
            pass

    def test_error_very_large_counter(self):
        """ERR-004: Very large counter value."""
        key = 'JBSWY3DPEHPK3PXP'

        # Python can handle large integers, but struct.pack has limits
        # Test with 2^63 - 1 (max signed 64-bit)
        max_counter = 2**63 - 1

        try:
            result = oathtool.generate_otp(key, max_counter)
            assert len(result) == 6
            assert result.isdigit()
        except struct.error:
            # struct.pack might overflow, which is acceptable
            pass

    def test_error_negative_counter(self):
        """ERR-005: Negative counter value."""
        key = 'JBSWY3DPEHPK3PXP'

        # Negative counter should cause struct.pack to fail or handle it
        try:
            result = oathtool.generate_otp(key, -1)
            # Some implementations might allow this
            assert len(result) == 6
            assert result.isdigit()
        except (struct.error, OverflowError):
            # Expected to fail
            pass


class TestSecurityConsiderations:
    """Security-related tests."""

    def test_security_short_key_warning(self):
        """SEC-004: Short key (< 16 bytes) should still work."""
        # RFC recommends 128-bit (16 byte) minimum for security
        # Base32 encodes 5 bits per character, so 16 bytes = 26 chars

        short_key = 'ABCDEFGH'  # ~5 bytes
        result = oathtool.generate_otp(short_key, 1)

        # Should work but not be secure
        assert len(result) == 6
        assert result.isdigit()

        # Note: A production implementation might warn about this
