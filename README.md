# Buffy

Buffy watches a Plex server for newly started playback sessions and posts a Telegram notification to a group chat.

Each notification can include:

- Title
- User who started watching
- Player name
- Length
- Year
- Synopsis
- Rotten Tomatoes rating when OMDb can resolve the title
- Poster art uploaded from Plex when artwork is available

## Quickstart

1. Complete the external service setup in `SETUP_GUIDE.md`.
   This covers Plex, Telegram, the group chat ID, and OMDb.
2. Select the project Python with `pyenv`:

   ```bash
   pyenv local 3.11.13
   ```

3. Create a virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

4. Create your local config file:

   ```bash
   cp .env.example .env
   ```

5. Put your real values into `.env`.
6. Run the notifier:

   ```bash
   python -m buffy
   ```

`.env` is loaded automatically on startup. If you also export shell variables, the shell values win.

## Requirements

- Python 3.11+
- A Plex token with access to the server
- A Telegram bot token and target chat ID
- Optional: an OMDb API key for ratings enrichment

## Linux Deployment

For a small always-on server, `systemd` is the simplest deployment target. If Buffy runs on the same box as Plex, use `PLEX_BASE_URL=http://127.0.0.1:32400` in `.env`.

1. Copy the project to the Linux server, for example to `/opt/buffy`.
2. Install Python 3.11 and create a dedicated service account:

   ```bash
   sudo useradd --system --create-home --home-dir /opt/buffy --shell /usr/sbin/nologin buffy
   sudo chown -R buffy:buffy /opt/buffy
   ```

3. As the `buffy` user, create the virtual environment and install the app:

   ```bash
   cd /opt/buffy
   python -m venv .venv
   . .venv/bin/activate
   pip install -e .
   ```

4. Put your real settings in `/opt/buffy/.env`.
5. Install the service file from `deploy/buffy.service`:

   ```bash
   sudo cp deploy/buffy.service /etc/systemd/system/buffy.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now buffy
   ```

6. Check status and logs:

   ```bash
   sudo systemctl status buffy
   sudo journalctl -u buffy -f
   ```

## Notes

- The service polls `/status/sessions` and sends one notification per active playback session.
- It stores active Plex session IDs in `.state/active_sessions.json` so a process restart does not spam duplicate alerts for sessions that are already in progress.
- OMDb is used for ratings because it exposes Rotten Tomatoes data when available.
- On Linux, transient request failures are logged and retried automatically instead of crashing the process.
