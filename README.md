# Captura Movil

Bot personal de Telegram que conserva capturas en una cola local y las agrega como tareas TODO a un
archivo Org. Requiere Python 3.11, `uv`, y systemd; no usa contenedores ni base de datos.

## Instalación

```sh
uv sync --frozen
sudo install -m 600 deploy/mobile-org-capture.env.example /etc/mobile-org-capture/mobile-org-capture.env
sudo install -m 644 deploy/mobile-org-capture.service /etc/systemd/system/mobile-org-capture.service
sudo systemctl daemon-reload
sudo systemctl enable --now mobile-org-capture
```

Edite `/etc/mobile-org-capture/mobile-org-capture.env` con el token y chat ID reales. No copie secretos al
repositorio. Tras un reinicio, systemd reinicia el bot y el barrido local procesa los manifiestos
pendientes sin necesitar red.

Configure en cada Emacs una abreviatura compatible con `ORG_ARTIFACTS_LINK_PREFIX`, por ejemplo:

```elisp
(add-to-list 'org-link-abbrev-alist '("artifact" . "/srv/org/artifacts/"))
```

Configure Syncthing para ignorar los archivos temporales `.tmp` del directorio de artefactos; solo
los nombres finales publicados deben replicarse.
