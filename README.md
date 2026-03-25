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
- Optional: `NOTIFICATION_DELAY_MINUTES` to wait before sending a play alert
- Optional: `REPEAT_PLAY_SUPPRESSION_MINUTES` to suppress quick repeat alerts for the same user and same video

## Linux Deployment

For a small always-on server, `systemd` is the simplest deployment target. If Buffy runs on the same box as Plex, use `PLEX_BASE_URL=http://127.0.0.1:32400` in `.env`.

1. Copy the project to the Linux server, for example to `/opt/buffy`.
2. Make sure the directory is owned by your normal Linux user:

   ```bash
   sudo mkdir -p /opt/buffy
   sudo chown "$USER":"$USER" /opt/buffy
   ```

3. As your normal user, create the virtual environment and install the app:

   ```bash
   cd /opt/buffy
   python -m venv .venv
   . .venv/bin/activate
   pip install -e .
   ```

4. Put your real settings in `/opt/buffy/.env`.
5. Install a `systemd` service that runs as your normal Linux user:

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
- If `NOTIFICATION_DELAY_MINUTES` is set, Buffy waits that long before notifying and skips the alert entirely if playback stops first.
- It stores active Plex session IDs in `.state/active_sessions.json` so a process restart does not spam duplicate alerts for sessions that are already in progress.
- If `REPEAT_PLAY_SUPPRESSION_MINUTES` is set, Buffy suppresses repeat alerts for the same user and the same video inside that time window.
- OMDb is used for ratings because it exposes Rotten Tomatoes data when available.
- On Linux, transient request failures are logged and retried automatically instead of crashing the process.
