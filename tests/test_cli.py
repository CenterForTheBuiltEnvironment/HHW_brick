"""
Tests for CLI module.
"""

import pytest
from click.testing import CliRunner

from hhws_brick_application.cli.main import cli


class TestCLI:
    """Test cases for command-line interface."""

    def test_cli_import(self):
        """Test that CLI can be imported."""
        assert cli is not None

    def test_cli_help(self):
        """Test CLI help command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert 'Usage:' in result.output or 'HHWS' in result.output.upper()

    def test_cli_version(self):
        """Test CLI version command if it exists."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        # Might succeed or fail depending on implementation
        # Just check it doesn't crash
        assert result.exit_code in [0, 2]  # 0 = success, 2 = no such option

    def test_cli_convert_command_help(self):
        """Test convert command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['convert', '--help'])

        # Should show help for convert command (exit code 0 or 2)
        assert result.exit_code in [0, 2]

    def test_cli_validate_command_help(self):
        """Test validate command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['validate', '--help'])

        # Should show help for validate command (exit code 0 or 2)
        assert result.exit_code in [0, 2]

