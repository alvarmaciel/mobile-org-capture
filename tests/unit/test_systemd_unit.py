from pathlib import Path


def test_systemd_unit_uses_external_environment_file():
    unit = Path("deploy/captura-movil.service").read_text(encoding="utf-8")
    assert "EnvironmentFile=/etc/captura-movil/captura-movil.env" in unit
    assert "Restart=always" in unit
    assert "TELEGRAM_BOT_TOKEN" not in unit
