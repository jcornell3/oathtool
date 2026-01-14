"""
Unit tests for oathtool CLI interface and I/O functions.
"""

import sys
from io import StringIO
from unittest.mock import Mock, patch

import pytest

import oathtool


def assert_valid_otp(output):
    """Assert output is a valid 6-digit OTP code."""
    assert len(output) == 6, f"Expected 6 digits, got {len(output)}"
    assert output.isdigit(), f"Expected digits only, got {output}"


@pytest.fixture
def mock_tty_stdin():
    """Mock stdin as a TTY (no piped input)."""
    mock_stdin = Mock()
    mock_stdin.isatty.return_value = True
    with patch.object(sys, 'stdin', mock_stdin):
        yield mock_stdin


@pytest.fixture
def fixed_time():
    """Mock time.time to return a fixed value."""
    with patch('time.time', return_value=1234567890):
        yield


class TestMain:
    """Tests for main() - CLI entry point."""

    def test_main_valid_argument(self, mock_tty_stdin, fixed_time, capsys):
        """Valid key argument produces 6-digit code."""
        with patch.object(sys, 'argv', ['prog', 'JBSWY3DPEHPK3PXP']):
            oathtool.main()
            output = capsys.readouterr().out.strip()
            assert_valid_otp(output)

    def test_main_valid_stdin(self, fixed_time, capsys):
        """Valid key from stdin produces 6-digit code."""
        with patch.object(sys, 'argv', ['prog']):
            mock_stdin = StringIO('JBSWY3DPEHPK3PXP')
            mock_stdin.isatty = Mock(return_value=False)
            with patch.object(sys, 'stdin', mock_stdin):
                oathtool.main()
                output = capsys.readouterr().out.strip()
                assert_valid_otp(output)

    def test_main_no_input(self, mock_tty_stdin):
        """No input raises error with exit code 2."""
        with patch.object(sys, 'argv', ['prog']):
            with pytest.raises(SystemExit) as exc_info:
                oathtool.main()
            assert exc_info.value.code == 2

    def test_main_version_flag(self, capsys):
        """--version shows version and exits 0."""
        with patch.object(sys, 'argv', ['prog', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                oathtool.main()
            assert exc_info.value.code == 0
            assert 'oathtool' in capsys.readouterr().out

    def test_main_help_flag(self, capsys):
        """--help shows usage and exits 0."""
        with patch.object(sys, 'argv', ['prog', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                oathtool.main()
            assert exc_info.value.code == 0
            output = capsys.readouterr().out
            assert 'usage:' in output.lower()
            assert '--totp' in output
            assert '--base32' in output

    def test_main_totp_flag(self, mock_tty_stdin, fixed_time, capsys):
        """--totp flag works (no-op for compatibility)."""
        with patch.object(sys, 'argv', ['prog', '--totp', 'JBSWY3DPEHPK3PXP']):
            oathtool.main()
            output = capsys.readouterr().out.strip()
            assert_valid_otp(output)

    def test_main_base32_flag_valid(self, mock_tty_stdin, fixed_time, capsys):
        """--base32 with valid 32-character key succeeds."""
        key = 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ'
        with patch.object(sys, 'argv', ['prog', '--base32', key]):
            oathtool.main()
            output = capsys.readouterr().out.strip()
            assert_valid_otp(output)

    def test_main_base32_flag_invalid_length(self, mock_tty_stdin, capsys):
        """--base32 with wrong length key fails with error."""
        with patch.object(sys, 'argv', ['prog', '--base32', 'JBSWY3DPEHPK3PXP']):
            with pytest.raises(SystemExit) as exc_info:
                oathtool.main()
            assert exc_info.value.code == 1
            err = capsys.readouterr().err
            assert '32-character' in err

    def test_main_base32_with_spaces(self, mock_tty_stdin, fixed_time, capsys):
        """--base32 ignores spaces when counting characters."""
        key = 'GEZD GNBV GY3T QOJQ GEZD GNBV GY3T QOJQ'
        with patch.object(sys, 'argv', ['prog', '--base32', key]):
            oathtool.main()
            output = capsys.readouterr().out.strip()
            assert_valid_otp(output)

    def test_main_invalid_key_format(self, mock_tty_stdin, capsys):
        """Invalid base32 key shows error message."""
        with patch.object(sys, 'argv', ['prog', 'INVALID!!!']):
            with pytest.raises(SystemExit) as exc_info:
                oathtool.main()
            assert exc_info.value.code == 1
            assert 'Invalid secret key' in capsys.readouterr().err

    def test_main_argument_priority(self, fixed_time, capsys):
        """Command line argument takes priority over stdin."""
        with patch.object(sys, 'argv', ['prog', 'JBSWY3DPEHPK3PXP']):
            mock_stdin = StringIO('DIFFERENT_KEY_HERE')
            mock_stdin.isatty = Mock(return_value=False)
            with patch.object(sys, 'stdin', mock_stdin):
                oathtool.main()
                output = capsys.readouterr().out.strip()
                assert_valid_otp(output)


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_deterministic_output(self, mock_tty_stdin, capsys):
        """Same input at same time produces same output."""
        with patch('time.time', return_value=1234567890):
            with patch.object(sys, 'argv', ['prog', 'JBSWY3DPEHPK3PXP']):
                oathtool.main()
                output1 = capsys.readouterr().out.strip()
                oathtool.main()
                output2 = capsys.readouterr().out.strip()
                assert output1 == output2


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.parametrize("invalid_key", ['KEY0KEY', 'KEY1KEY', 'KEY8KEY', 'KEY9KEY'])
    def test_invalid_base32_alphabet(self, invalid_key):
        """Base32 alphabet doesn't include 0, 1, 8, 9."""
        with pytest.raises(ValueError) as exc_info:
            oathtool.generate_otp(invalid_key, 1)
        assert 'Invalid secret key' in str(exc_info.value)
