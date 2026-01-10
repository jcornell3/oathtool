"""
Unit tests for Windows executable functionality.

Tests the PyInstaller-built executable and MSIX packaging on Windows.
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


class TestWindowsExecutable:
    """Tests for the Windows executable."""

    @pytest.fixture
    def exe_path(self):
        """Path to the built executable."""
        return os.path.join(os.path.dirname(__file__), '..', 'dist', 'oathtool.exe')

    def test_executable_exists(self, exe_path):
        """WIN-001: Executable generation - verify oathtool.exe exists."""
        if not os.path.exists(exe_path):
            pytest.skip("Executable not built. Run: pyinstaller oathtool.spec")

    def test_executable_functionality(self, exe_path):
        """WIN-002: Executable functionality - run with key."""
        if not os.path.exists(exe_path):
            pytest.skip("Executable not built. Run: pyinstaller oathtool.spec")

        # Test with a known key
        result = subprocess.run(
            [exe_path, 'JBSWY3DPEHPK3PXP'],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0
        output = result.stdout.strip()
        assert len(output) == 6
        assert output.isdigit()

    def test_executable_no_arguments(self, exe_path):
        """WIN-002: Executable error handling - no arguments."""
        if not os.path.exists(exe_path):
            pytest.skip("Executable not built. Run: pyinstaller oathtool.spec")

        result = subprocess.run(
            [exe_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 1
        assert 'provide secret key' in result.stdout.lower()

    def test_executable_piped_input(self, exe_path):
        """WIN-007: Piped input on Windows."""
        if not os.path.exists(exe_path):
            pytest.skip("Executable not built. Run: pyinstaller oathtool.spec")

        result = subprocess.run(
            [exe_path],
            input='JBSWY3DPEHPK3PXP',
            capture_output=True,
            text=True,
            timeout=10
        )

        assert result.returncode == 0
        output = result.stdout.strip()
        assert len(output) == 6
        assert output.isdigit()


class TestMSIXPackage:
    """Tests for MSIX package creation and structure."""

    @pytest.fixture
    def msix_dir(self):
        """Path to MSIX packaging directory."""
        return os.path.join(os.path.dirname(__file__), '..', 'msix')

    def test_msix_manifest_exists(self, msix_dir):
        """WIN-004: MSIX manifest file exists."""
        manifest_path = os.path.join(msix_dir, 'AppxManifest.xml')
        assert os.path.exists(manifest_path), "AppxManifest.xml not found"

    def test_msix_assets_exist(self, msix_dir):
        """WIN-004: MSIX assets exist."""
        assets_dir = os.path.join(msix_dir, 'Assets')
        assert os.path.exists(assets_dir), "Assets directory not found"

        # Check required logo files
        required_assets = [
            'StoreLogo.png',
            'Square44x44Logo.png',
            'Square150x150Logo.png',
            'Wide310x150Logo.png'
        ]

        for asset in required_assets:
            asset_path = os.path.join(assets_dir, asset)
            assert os.path.exists(asset_path), f"{asset} not found"

    def test_msix_build_script_exists(self):
        """WIN-004: MSIX build script exists."""
        script_path = os.path.join(os.path.dirname(__file__), '..', 'build-msix.ps1')
        assert os.path.exists(script_path), "build-msix.ps1 not found"

    def test_msix_manifest_structure(self, msix_dir):
        """WIN-004: MSIX manifest has correct structure."""
        manifest_path = os.path.join(msix_dir, 'AppxManifest.xml')

        if not os.path.exists(manifest_path):
            pytest.skip("AppxManifest.xml not found")

        with open(manifest_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify key manifest elements
        assert 'com.jaraco.oathtool' in content
        assert 'OathTool' in content
        assert 'oathtool.exe' in content
        assert 'runFullTrust' in content

    def test_msix_package_exists(self):
        """WIN-004: Check if MSIX package has been built."""
        dist_dir = os.path.join(os.path.dirname(__file__), '..', 'dist')

        if not os.path.exists(dist_dir):
            pytest.skip("dist directory not found")

        msix_files = [f for f in os.listdir(dist_dir) if f.endswith('.msix')]

        if not msix_files:
            pytest.skip("No MSIX package found. Run: .\\build-msix.ps1")

        # If MSIX exists, verify it has content
        msix_path = os.path.join(dist_dir, msix_files[0])
        file_size = os.path.getsize(msix_path)
        assert file_size > 0, "MSIX package is empty"


class TestPyInstallerSpec:
    """Tests for PyInstaller specification file."""

    def test_spec_file_exists(self):
        """Verify oathtool.spec exists."""
        spec_path = os.path.join(os.path.dirname(__file__), '..', 'oathtool.spec')
        assert os.path.exists(spec_path), "oathtool.spec not found"

    def test_spec_file_structure(self):
        """Verify spec file has correct structure."""
        spec_path = os.path.join(os.path.dirname(__file__), '..', 'oathtool.spec')

        if not os.path.exists(spec_path):
            pytest.skip("oathtool.spec not found")

        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verify key spec file elements
        assert 'Analysis' in content
        assert 'EXE' in content
        assert '__main__.py' in content
        assert "name='oathtool'" in content
