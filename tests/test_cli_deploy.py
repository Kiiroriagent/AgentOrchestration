"""Tests for CLI deploy manifest validation."""

import subprocess
import sys

import pytest


class TestDeployManifestValidation:
    """Verify deploy command fails when manifest is missing."""

    def test_deploy_missing_manifest_exits_nonzero(self, tmp_path):
        missing = str(tmp_path / "nonexistent.yaml")
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "deploy", missing],
            capture_output=True,
            text=True,
            cwd="/tmp/agent-orchestration",
        )
        assert result.returncode != 0

    def test_deploy_missing_manifest_prints_error(self, tmp_path):
        missing = str(tmp_path / "nonexistent.yaml")
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "deploy", missing],
            capture_output=True,
            text=True,
            cwd="/tmp/agent-orchestration",
        )
        assert "manifest not found" in result.stderr

    def test_deploy_existing_manifest_succeeds(self, tmp_path):
        manifest = tmp_path / "agent.yaml"
        manifest.write_text("name: test-agent\ntype: worker\n")
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "deploy", str(manifest)],
            capture_output=True,
            text=True,
            cwd="/tmp/agent-orchestration",
        )
        assert result.returncode == 0
        assert "Deploying agent from manifest" in result.stdout

    def test_deploy_directory_path_exits_nonzero(self, tmp_path):
        """A directory is not a valid manifest file."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.main", "deploy", str(tmp_path)],
            capture_output=True,
            text=True,
            cwd="/tmp/agent-orchestration",
        )
        assert result.returncode != 0
        assert "manifest not found" in result.stderr
