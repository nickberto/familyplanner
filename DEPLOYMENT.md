# Deployment on Uberspace

This guide explains how to deploy the Family Planner app on Uberspace using virtualenv, uWSGI, and supervisord.

If you prefer a hassle-free alternative, this repository also includes a simple `Dockerfile` for containerized deployment. It is designed to work out of the box and avoids the manual virtualenv/uWSGI/supervisord setup.

## Optional Docker Alternative

A ready-to-use Docker image can be built from the repository root.

Build the container:

```bash
docker build -t familyplanner .
```

Run it with a mounted data directory:

```bash
docker run -p 5000:5000 -v "$PWD/data:/data" -e DATABASE_URL=sqlite:////data/familyplanner.db familyplanner
```

Open `http://localhost:5000` to verify the app is running.

## Quick Start

```bash
# 1. Set up directories and clone
ssh user@your-uberspace.de
mkdir -p ~/logs ~/data ~/etc/uwsgi ~/src
cd ~/src && git clone <repo> familyplanner
cd familyplanner

# 2. Create virtual environment and install
python3.11 -m venv ~/.virtualenvs/familyplanner
source ~/.virtualenvs/familyplanner/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cat > .env.production << EOF
ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:////home/user/data/familyplanner.db
EOF

# 4. Setup uWSGI and supervisord
cp uwsgi.ini ~/etc/uwsgi/familyplanner.ini
# Edit paths in ~/etc/uwsgi/familyplanner.ini (see Step 7 below)
pip install supervisor
supervisord -c ~/.config/supervisor/supervisord.conf
```

See detailed steps below for complete configuration.

## Prerequisites

- Uberspace account with SSH access
- Python 3.11+ installed (usually available on Uberspace)
- SSH key configured

## Step 1: Connect and Prepare

```bash
ssh user@your-uberspace.de
```

Create necessary directories:

```bash
mkdir -p ~/logs
mkdir -p ~/etc/uwsgi
mkdir -p ~/src
```

## Step 2: Clone Repository

```bash
cd ~/src
git clone <your-repo> familyplanner
cd familyplanner
```

## Step 3: Create Virtual Environment

```bash
python3.11 -m venv ~/.virtualenvs/familyplanner
source ~/.virtualenvs/familyplanner/bin/activate
```

## Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 5: Configure Application

Create a `.env` file with your configuration:

```bash
cat > .env.production << EOF
ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_URL=sqlite:////home/user/data/familyplanner.db
FLASK_ENV=production
EOF
```

Replace `user` with your Uberspace username.

Create the data directory:

```bash
mkdir -p ~/data
```

## Step 6: Initialize Database

```bash
source ~/.virtualenvs/familyplanner/bin/activate
cd ~/src/familyplanner
ENV=production python -c "from familyplanner.app import create_app; app = create_app(); print('Database initialized')"
```

## Step 7: Configure uWSGI

Copy the uWSGI configuration:

```bash
cp ~/src/familyplanner/uwsgi.ini ~/etc/uwsgi/familyplanner.ini
```

Edit `~/etc/uwsgi/familyplanner.ini` to update paths:

```ini
[uwsgi]
socket = 127.0.0.1:5001
protocol = http
chdir = /home/user/src/familyplanner
home = /home/user/.virtualenvs/familyplanner
wsgi-file = wsgi.py
callable = app
master = true
processes = 4
threads = 2
logto = /home/user/logs/uwsgi.log
python-autoreload = 1
http-timeout = 60
socket-timeout = 60
env = ENV=production
env = DATABASE_URL=sqlite:////home/user/data/familyplanner.db
```

## Step 8: Configure Supervisord

Create supervisord configuration:

```bash
cat > ~/.config/supervisor/supervisord.conf << 'EOF'
[supervisord]
nodaemon=true

[unix_http_server]
file=/home/user/run/supervisor.sock

[supervisorctl]
serverurl=unix:///home/user/run/supervisor.sock

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[program:familyplanner]
command=/home/user/.virtualenvs/familyplanner/bin/uwsgi --ini /home/user/etc/uwsgi/familyplanner.ini
autorestart=true
autostart=true
stdout_logfile=/home/user/logs/familyplanner-stdout.log
stderr_logfile=/home/user/logs/familyplanner-stderr.log
startsecs=3600
stopasgroup=true
killasgroup=true
EOF
```

Create the run directory:

```bash
mkdir -p ~/run
```

## Step 9: Install Supervisord

```bash
source ~/.virtualenvs/familyplanner/bin/activate
pip install supervisor
```

## Step 10: Start Supervisord

```bash
supervisord -c ~/.config/supervisor/supervisord.conf
```

Check if supervisord is running:

```bash
supervisorctl -c ~/.config/supervisor/supervisord.conf status
```

You should see:

```
familyplanner                        RUNNING   pid 1234, uptime 0:00:10
```

## Step 11: Configure Web Server

If using Apache (common on Uberspace), configure a reverse proxy:

```apache
<VirtualHost *:443>
    ServerName your-domain.example.com
    
    SSLEngine on
    SSLCertificateFile /path/to/cert.pem
    SSLCertificateKeyFile /path/to/key.pem
    
    ProxyPass / http://127.0.0.1:5001/
    ProxyPassReverse / http://127.0.0.1:5001/
    
    ProxyPreserveHost On
    
    <Location />
        Order allow,deny
        Allow from all
    </Location>
</VirtualHost>
```

## Step 12: Test the Application

Visit `https://your-domain.example.com` and verify the app works.

Check logs:

```bash
tail -f ~/logs/familyplanner-stdout.log
tail -f ~/logs/familyplanner-stderr.log
tail -f ~/logs/uwsgi.log
```

## Maintenance

### Restart Application

```bash
supervisorctl -c ~/.config/supervisor/supervisord.conf restart familyplanner
```

### Update Application

```bash
cd ~/src/familyplanner
git pull origin main
source ~/.virtualenvs/familyplanner/bin/activate
pip install -r requirements.txt
supervisorctl -c ~/.config/supervisor/supervisord.conf restart familyplanner
```

### Backup Database

```bash
cp ~/data/familyplanner.db ~/data/familyplanner.db.backup
```

### View Logs

```bash
supervisorctl -c ~/.config/supervisor/supervisord.conf tail familyplanner stdout
supervisorctl -c ~/.config/supervisor/supervisord.conf tail familyplanner stderr
```

## Environment Variables

The following environment variables can be set:

- `ENV`: Set to `production` for production deployments
- `SECRET_KEY`: Flask secret key for sessions (generate with `python3 -c 'import secrets; print(secrets.token_hex(32))'`)
- `DATABASE_URL`: SQLite database path (e.g., `sqlite:////home/user/data/familyplanner.db`)
- `FLASK_ENV`: Flask environment (defaults to value of `ENV`)

## Security Considerations

1. **SECRET_KEY**: Generate a strong random secret key and store it safely
2. **Database**: Use a strong path and ensure database files have restricted permissions
3. **SSL/TLS**: Always use HTTPS in production
4. **Backups**: Regularly backup your database
5. **Updates**: Keep dependencies updated for security patches

## Troubleshooting

### Application won't start

Check logs:

```bash
tail -f ~/logs/familyplanner-stdout.log
tail -f ~/logs/familyplanner-stderr.log
```

Verify database path is correct and writable:

```bash
ls -la ~/data/
```

### Supervisord won't start

Check if port is already in use:

```bash
netstat -tlnp | grep 5001
```

Verify supervisord configuration:

```bash
supervisord -c ~/.config/supervisor/supervisord.conf
```

### Database errors

Ensure the database directory exists and is writable:

```bash
mkdir -p ~/data
chmod 755 ~/data
```

Reinitialize database:

```bash
rm ~/data/familyplanner.db
source ~/.virtualenvs/familyplanner/bin/activate
cd ~/src/familyplanner
ENV=production python -c "from familyplanner.app import create_app; app = create_app()"
```

## Performance Tuning

For better performance, adjust uWSGI settings:

```ini
processes = 4        # Increase for more load
threads = 2          # Increase for more concurrency
http-timeout = 120   # Increase if requests timeout
```

Monitor resource usage and adjust accordingly.
