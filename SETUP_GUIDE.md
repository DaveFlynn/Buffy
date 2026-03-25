# Plex And Telegram Setup Guide

This guide covers the two things you need before running Buffy:

- a Plex `X-Plex-Token`
- a Telegram bot token and target group chat ID

## 1. Get A Plex Token

Plex documents `X-Plex-Token` as the auth value used when calling Plex server URLs.

### Fast path in Plex Web

1. Sign in to Plex Web in a browser.
   - Recommended URL: `https://app.plex.tv/desktop`
2. Open any movie or episode details page.
3. Open the item actions menu.
   - In Plex Web, this is the three-dots menu on the media item page.
4. Choose `Get Info`.
5. In the info panel, choose `View XML`.
   - Plex support documents viewing a library item's XML to expose the tokenized URL.
6. Look at the page URL.
7. Find the `X-Plex-Token=...` query parameter.
8. Copy that value into your `.env` file as `PLEX_TOKEN`.

Example:

```text
https://your-plex-host:32400/library/metadata/12345?X-Plex-Token=YOUR_TOKEN_HERE
```

### If You Cannot Find The XML View

Use browser developer tools:

1. Open Plex Web and sign in.
2. Open developer tools in the browser.
3. Go to the `Network` tab.
4. Click into any media item.
5. Trigger an action that loads item details.
6. Inspect a request to your Plex server.
7. Find the `X-Plex-Token` parameter in the request URL or query string.

### Important Notes

- Plex support says this token can be temporary.
- In practice, it usually remains usable until you sign out devices or rotate account credentials.
- If you change your Plex password and choose to sign out connected devices, old tokens are invalidated.
- For this notifier, a token from the Plex account that can see the target library is enough.

## 2. Create A Telegram Bot

Telegram’s official flow is through `@BotFather`.

1. Open Telegram.
2. Search for `@BotFather`.
3. Start the chat.
4. Send `/newbot`.
5. Enter a display name for the bot.
6. Enter a username for the bot.
   - Telegram requires the username to end in `bot`, for example `buffy_now_playing_bot`.
7. BotFather returns a bot token.
8. Copy that token into `.env` as `TELEGRAM_BOT_TOKEN`.

Example token shape:

```text
123456789:AAExampleTokenValueHere
```

### Recommended Bot Settings

These are optional but useful:

1. In `@BotFather`, send `/mybots`.
2. Select your bot.
3. Set a profile photo, description, and group privacy settings if you want.

For this project, the bot only sends messages. It does not need commands.

## 3. Add The Bot To Your Telegram Group

1. Create the target group if it does not already exist.
   - Example: `The 7th Floor Video Shop`
2. Open the group info screen.
3. Choose `Add members`.
4. Add your bot by username.
5. In `@BotFather`, run `/setjoingroups`.
6. Choose your bot and set it to `Disable`.

That sequence matters:

- add the bot to your own group first
- then disable future group joins

Telegram does not offer a "only this group" setting. Disabling future group joins after setup is the closest practical option.

### Admin Rights

For this notifier, the bot normally only needs permission to post messages.

If Telegram blocks posting in your group after you add it, promote the bot to admin and allow it to post messages.

## 4. Get The Telegram Group Chat ID

The easiest path is `getUpdates`.

1. Add the bot to the group.
2. In the group, send either:
   - `/start@YOUR_BOT_USERNAME`
   - or a message that mentions the bot, for example `@YOUR_BOT_USERNAME hello`
3. If `getUpdates` still comes back empty, temporarily disable privacy:
   - open `@BotFather`
   - run `/setprivacy`
   - choose your bot
   - choose `Disable`
4. Send a fresh message in the group.
5. Open this URL in a browser, replacing the token:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates
```

6. Find the object for your group.
7. Copy `message.chat.id` into `.env` as `TELEGRAM_CHAT_ID`.
8. If you disabled privacy in step 3, you can turn it back on afterward.

For groups, the ID usually looks like a negative number such as:

```text
-1001234567890
```

### What To Look For

The response usually contains a block similar to:

```json
{
  "message": {
    "chat": {
      "id": -1001234567890,
      "title": "The 7th Floor Video Shop",
      "type": "supergroup"
    }
  }
}
```

What you do with that value:

- put it into `.env` as `TELEGRAM_CHAT_ID`
- Buffy uses it as the destination chat for all notifications

Example:

```dotenv
TELEGRAM_CHAT_ID=-1001234567890
```

### If `getUpdates` Returns An Empty Result

This usually means one of these:

- privacy mode is enabled and the bot did not receive a command or mention
- nobody has sent a message to the bot or group yet
- the bot was added after the last visible update and has not seen any new message
- another bot client already consumed the pending updates

Try this:

1. Send `/start@YOUR_BOT_USERNAME` in the group.
2. Refresh `getUpdates`.
3. If it is still empty, disable privacy temporarily with `/setprivacy`.
4. Send a fresh message in the group.
5. Refresh `getUpdates` again.

## 5. Fill In `.env`

Copy the example file:

```bash
cp .env.example .env
```

Then set values like this:

```dotenv
PLEX_BASE_URL=http://YOUR_PLEX_SERVER:32400
PLEX_TOKEN=your-plex-token
TELEGRAM_BOT_TOKEN=123456789:your-bot-token
TELEGRAM_CHAT_ID=-1001234567890
OMDB_API_KEY=optional-omdb-key
POLL_INTERVAL_SECONDS=15
NOTIFICATION_DELAY_MINUTES=
REPEAT_PLAY_SUPPRESSION_MINUTES=
STATE_FILE=.state/active_sessions.json
```

The key Telegram values are:

- `TELEGRAM_BOT_TOKEN`: the token returned by `@BotFather`
- `TELEGRAM_CHAT_ID`: the `message.chat.id` value from `getUpdates` for your group

Keep the bot token secret. If it is ever pasted somewhere unsafe, revoke and regenerate it in `@BotFather`, then update `.env`.

## 6. Get An OMDb API Key

OMDb is optional, but you need it if you want Buffy to include Rotten Tomatoes or IMDb ratings in notifications.

1. Open `https://www.omdbapi.com/apikey.aspx`
2. Choose a free or paid API key option.
3. Complete the signup form.
4. Check your email for the API key.
5. Put that value into `.env` as `OMDB_API_KEY`.

Example:

```dotenv
OMDB_API_KEY=your-omdb-api-key
```

If `OMDB_API_KEY` is missing, Buffy still works. It just sends notifications without ratings.

## 7. Optional Notification Delay

If you want Buffy to wait before sending a play alert, set:

```dotenv
NOTIFICATION_DELAY_MINUTES=2
```

How it works:

- Buffy sees a new playback and starts a timer
- it only sends the alert if the playback is still active after that many minutes
- if the user stops the video before the timer finishes, no alert is sent
- if this setting is blank or missing, alerts are sent immediately

## 8. Optional Repeat-Play Suppression

If you want Buffy to suppress quick repeat alerts when the same user starts the same video again, set:

```dotenv
REPEAT_PLAY_SUPPRESSION_MINUTES=15
```

How it works:

- Buffy remembers recent alerts by `user + video`
- if the same user starts the same item again inside that many minutes, the alert is skipped
- if this setting is blank or missing, Buffy reports every new playback session

## 9. Start The Notifier

If you use `pyenv`, select the project interpreter first:

```bash
pyenv local 3.11.13
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m buffy
```

## 10. Run Buffy On A Linux Server All The Time

For an always-on home server, use `systemd`.

1. Copy the project to the server, for example to `/opt/buffy`.
2. Make sure the directory is owned by your normal Linux user:

```bash
sudo mkdir -p /opt/buffy
sudo chown "$USER":"$USER" /opt/buffy
```

3. Create the virtual environment and install Buffy on the server:

```bash
cd /opt/buffy
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

4. Make sure `/opt/buffy/.env` contains your real settings.
5. Copy the included service file into place:

```bash
sudo cp deploy/buffy.service /etc/systemd/system/buffy.service
sudo systemctl daemon-reload
sudo systemctl enable --now buffy
```

6. Check that it is running:

```bash
sudo systemctl status buffy
sudo journalctl -u buffy -f
```

The included unit file expects:

- the project to live at `/opt/buffy`
- the service to run as your normal Linux user
- the virtual environment at `/opt/buffy/.venv`

If you deploy somewhere else, edit `deploy/buffy.service` first.

## Troubleshooting

### Telegram message does not appear

- Make sure the bot is actually in the target group.
- Make sure `TELEGRAM_CHAT_ID` is the group ID, not your personal user ID.
- If needed, make the bot a group admin with permission to post.
- Test the bot directly:

```text
https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/sendMessage?chat_id=<TELEGRAM_CHAT_ID>&text=Buffy%20test
```

- If that fails, the chat ID is wrong or the bot cannot post to the group.

### Plex sessions never show up

- Confirm `PLEX_BASE_URL` points to the server that is actually playing media.
- Test the sessions endpoint manually:

```text
http://YOUR_PLEX_SERVER:32400/status/sessions?X-Plex-Token=YOUR_TOKEN
```

- If that returns auth errors, the token is wrong or expired.

### Ratings do not show up

- Rotten Tomatoes data depends on OMDb finding the correct title.
- Set `OMDB_API_KEY`.
- Some items will only have IMDb data or no matching data.

### Buffy exits after a network error

- The service now retries transient request failures automatically.
- On Linux, `systemd` also restarts the process if it exits for any other reason.
- Check logs with `journalctl -u buffy -f`.

## Sources

- Plex Support: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/
- Plex Support: https://support.plex.tv/articles/201638786-plex-media-server-url-commands/
- Telegram Bot Tutorial: https://core.telegram.org/bots/tutorial
- Telegram Bot Features / BotFather: https://core.telegram.org/bots/features
- OMDb API key signup: https://www.omdbapi.com/apikey.aspx
- Supporting walkthrough: https://dev.to/sarafian/creating-a-private-telegram-chatbot-2n9
