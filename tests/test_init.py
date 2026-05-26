"""Tests for the schema-forge init command (Story C1 / EPIC C1)."""

from __future__ import annotations

import yaml
import pytest

from forge.cli import main


def run_init(tmp_path, domain="gtm", client="acme", subdir="eng"):
    output = tmp_path / subdir
    rc = main(["init", "--domain", domain, "--client", client, "--output", str(output)])
    return rc, output


class TestInitCreatesTree:
    def test_returns_zero(self, tmp_path):
        rc, _ = run_init(tmp_path)
        assert rc == 0

    def test_top_level_dirs(self, tmp_path):
        _, output = run_init(tmp_path)
        for d in ["01_interview_inputs", "02_baseline", "03_overrides", "04_output"]:
            assert (output / d).is_dir(), f"missing {d}/"

    def test_manifest_exists(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "manifest.yaml").is_file()

    def test_manifest_fields(self, tmp_path):
        _, output = run_init(tmp_path, domain="gtm", client="acme")
        manifest = yaml.safe_load((output / "manifest.yaml").read_text())
        assert manifest["domain"] == "gtm"
        assert manifest["client"] == "acme"
        assert manifest["baseline_version"] == "gtm_v2.0"
        assert "generated_at" in manifest


class TestInterviewInputs:
    def test_interview_templates_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        inputs = output / "01_interview_inputs"
        for name in [
            "01_company_overview.md",
            "02_icp_interview.md",
            "03_channel_interview.md",
            "04_qualification_interview.md",
            "05_failure_modes_interview.md",
            "06_gold_records.md",
        ]:
            assert (inputs / name).is_file(), f"missing {name}"

    def test_playbook_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "01_interview_inputs" / "INTERVIEW_PLAYBOOK.md").is_file()

    def test_gold_csv_stub(self, tmp_path):
        _, output = run_init(tmp_path)
        csv = output / "01_interview_inputs" / "06_gold_records.csv"
        assert csv.is_file()
        header = csv.read_text(encoding="utf-8").splitlines()[0]
        assert "record_id" in header
        assert "disposition" in header
        assert "raw_notes" in header


class TestBaselineCopied:
    def test_schema_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "02_baseline" / "gtm_schema.py").is_file()

    def test_modifiers_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "02_baseline" / "modifiers.yaml").is_file()

    def test_policy_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "02_baseline" / "policy.py").is_file()

    def test_failure_modes_dir_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        fm = output / "02_baseline" / "failure_modes"
        assert fm.is_dir()
        assert any(fm.glob("fm*.py")), "no failure mode files found"

    def test_synthetic_gold_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "02_baseline" / "synthetic_gold.jsonl").is_file()

    def test_gold_readme_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "02_baseline" / "GOLD_README.md").is_file()

    def test_private_gen_not_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert not (output / "02_baseline" / "_gen_gold.py").exists()

    def test_init_not_copied(self, tmp_path):
        _, output = run_init(tmp_path)
        assert not (output / "02_baseline" / "__init__.py").exists()


class TestOverridesScaffold:
    def test_override_files_exist(self, tmp_path):
        _, output = run_init(tmp_path)
        overrides = output / "03_overrides"
        for name in [
            "icp_overrides.yaml",
            "channel_overrides.yaml",
            "modifier_overrides.yaml",
            "policy_overrides.yaml",
        ]:
            assert (overrides / name).is_file(), f"missing {name}"

    def test_failure_mode_additions_dir(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "03_overrides" / "failure_mode_additions").is_dir()

    def test_override_files_are_commented(self, tmp_path):
        _, output = run_init(tmp_path)
        for name in ["icp_overrides.yaml", "channel_overrides.yaml"]:
            content = (output / "03_overrides" / name).read_text()
            assert "#" in content, f"{name} should contain comment scaffolding"


class TestOutputDirEmpty:
    def test_output_dir_created(self, tmp_path):
        _, output = run_init(tmp_path)
        assert (output / "04_output").is_dir()

    def test_output_dir_empty(self, tmp_path):
        _, output = run_init(tmp_path)
        assert not any((output / "04_output").iterdir())


class TestErrorCases:
    def test_unknown_domain_errors(self, tmp_path):
        rc, _ = run_init(tmp_path, domain="crm", subdir="bad")
        assert rc != 0

    def test_rerun_into_nonempty_errors(self, tmp_path):
        rc, output = run_init(tmp_path)
        assert rc == 0
        rc2 = main(["init", "--domain", "gtm", "--client", "acme", "--output", str(output)])
        assert rc2 != 0

    def test_output_created_by_init(self, tmp_path):
        output = tmp_path / "new_engagement"
        assert not output.exists()
        rc = main(["init", "--domain", "gtm", "--client", "test", "--output", str(output)])
        assert rc == 0
        assert output.is_dir()
