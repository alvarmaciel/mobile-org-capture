from pathlib import Path


def test_systemd_unit_uses_external_environment_file():
    unit = Path("deploy/mobile-org-capture.service").read_text(encoding="utf-8")
    assert "EnvironmentFile=/etc/mobile-org-capture/mobile-org-capture.env" in unit
    assert "Restart=always" in unit
    assert "TELEGRAM_BOT_TOKEN" not in unit
