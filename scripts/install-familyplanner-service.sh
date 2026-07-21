#!/usr/bin/env bash
set -euo pipefail

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemd is not available on this host." >&2
  exit 1
fi

SERVICE_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
mkdir -p "$SERVICE_DIR" "$HOME/run" "$HOME/logs" "$HOME/.config/supervisor"
SERVICE_FILE="$SERVICE_DIR/familyplanner.service"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Family Planner Supervisor
After=network.target

[Service]
Type=forking
Environment=HOME=${HOME}
Environment=ENV_HOME=${HOME}
WorkingDirectory=${HOME}/src/familyplanner
ExecStart=/bin/bash -lc 'if [ -f "${HOME}/run/supervisord.pid" ] && kill -0 "$(cat "${HOME}/run/supervisord.pid")" 2>/dev/null; then echo "supervisord already running"; exit 0; fi; exec "${HOME}/.virtualenvs/familyplanner/bin/supervisord" -c "${HOME}/.config/supervisor/supervisord.conf"'
ExecStop=/bin/bash -lc 'if [ -f "${HOME}/run/supervisord.pid" ] && kill -0 "$(cat "${HOME}/run/supervisord.pid")" 2>/dev/null; then "${HOME}/.virtualenvs/familyplanner/bin/supervisorctl" -c "${HOME}/.config/supervisor/supervisord.conf" shutdown; fi'
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now familyplanner
systemctl --user status familyplanner --no-pager
