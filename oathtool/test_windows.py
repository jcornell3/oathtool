"""
Unit tests for Windows executable and MSIX packaging.
"""

import os
import subprocess
import sys

import pytest

# Only run these tests on Windows
pytestmark = pytest.mark.skipif(
    sys.platform != 'win32',
    reason="Windows-specific tests"
)

# Paths
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')
EXE_PATH = os.path.join(ROOT_DIR, 'dist', 'oathtool.exe')
MSIX_DIR = os.path.join(ROOT_DIR, 'msix')
DIST_DIR = os.path.join(ROOT_DIR, 'dist')


def assert_valid_otp(output):
    """Assert output is a valid 6-digit OTP code."""
    assert len(output) == 6
    assert output.isdigit()


class TestWindowsExecutable:
    """Tests for the Windows executable."""

    @pytest.fixture(autouse=True)
    def require_executable(self):
        """Skip all tests in this class if executable not built."""
        if not os.path.exists(EXE_PATH):
            pytest.skip("Executable not built. Run: pyinstaller oathtool.spec")

    def test_executable_with_key(self):
        """Executable produces valid OTP with key argument."""
        result = subprocess.run(
            [EXE_PATH, 'JBSWY3DPEHPK3PXP'],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert_valid_otp(result.stdout.strip())

    def test_executable_no_arguments(self):
        """Executable shows error when no key provided."""
        result = subprocess.run(
            [EXE_PATH],
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 2  # argparse error code
        assert 'provide secret key' in result.stderr.lower()

    def test_executable_piped_input(self):
        """Executable accepts key from stdin."""
        result = subprocess.run(
            [EXE_PATH],
            input='JBSWY3DPEHPK3PXP',
            capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert_valid_otp(result.stdout.strip())


class TestMSIXPackage:
    """Tests for MSIX package structure."""

    def test_msix_manifest_structure(self):
        """MSIX manifest exists and has correct structure."""
        manifest_path = os.path.join(MSIX_DIR, 'AppxManifest.xml')
        if not os.path.exists(manifest_path):
            pytest.skip("AppxManifest.xml not found")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'com.jaraco.oathtool' in content
        assert 'OathTool' in content
        assert 'oathtool.exe' in content
        assert 'runFullTrust' in content

    def test_msix_assets_exist(self):
        """Required MSIX assets exist."""
        assets_dir = os.path.join(MSIX_DIR, 'Assets')
        if not os.path.exists(assets_dir):
            pytest.skip("Assets directory not found")

        required_assets = [
            'StoreLogo.png', 'Square44x44Logo.png',
            'Square150x150Logo.png', 'Wide310x150Logo.png'
        ]
        for asset in required_assets:
            assert os.path.exists(os.path.join(assets_dir, asset)), f"{asset} not found"

    def test_msix_package_exists(self):
        """MSIX package has been built and has content."""
        if not os.path.exists(DIST_DIR):
            pytest.skip("dist directory not found")

        msix_files = [f for f in os.listdir(DIST_DIR) if f.endswith('.msix')]
        if not msix_files:
            pytest.skip("No MSIX package found. Run: .\\build-msix.ps1")

        msix_path = os.path.join(DIST_DIR, msix_files[0])
        assert os.path.getsize(msix_path) > 0, "MSIX package is empty"


class TestPyInstallerSpec:
    """Tests for PyInstaller specification file."""

    def test_spec_file_structure(self):
        """Spec file exists and has correct structure."""
        spec_path = os.path.join(ROOT_DIR, 'oathtool.spec')
        if not os.path.exists(spec_path):
            pytest.skip("oathtool.spec not found")

        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'Analysis' in content
        assert 'EXE' in content
        assert '__main__.py' in content
        assert "name='oathtool'" in content
