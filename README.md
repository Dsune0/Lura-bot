# Lura bot

Bot that creates panels with buttons to move specific users between two voice channels.

## Setup

### 1. Clone / Install

```bash
git clone https://github.com/Dsune0/Lura-bot
cd <repo>
pip install -U discord.py
```

---

### 2. Create a Bot

Go to the [Discord Developer Portal](https://discord.com/developers/applications)

**Steps:**

1. Create an application
2. Go to Bot -> Reset Token
3. Copy the Bot Token (keep it secret)

---

### 3. Grant bot permissions

In the Developer Portal:

Bot -> Privileged Gateway Intents -> Server Members Intent
Installation -> Default install settings -> Guild Install -> Scopes -> Add: `bot` `applications.commands`
Installation -> Default install settings -> Guild Install -> Permissions -> Add: `Move Members` `View Channels` `Send Messages` `Embed Links` ``

Use the generated URL to invite the bot to your server, make sure the bots Role is given access to the voice channels and whichever text channel you will be using for it 

---

### 4. Configure Token

Use an environment variable for the bot token saved locally
`.env`:
```
DISCORD_TOKEN=your_token
```

### 5. Run

```bash
python main.py
```

---

## Usage

```
/create_comp from_channel:<voice> to_channel:<voice> users:<mentions or IDs>
```

Example:

```
/create_comp from_channel:Lobby to_channel:Game users:@user1 @user2
```

This posts a panel with:

From channel, To channel, Users

Buttons to:

Move -> moves listed users from `from_channel` -> `to_channel`

Move Back -> move listed users `to_channel` -> `from_channel`

---

## Running on Replit

1. Create an account on Replit
2. Click on `Import code or design`
3. Choose github and paste the link `https://github.com/Dsune0/Lura-bot`
4. Click on `Import from Github`
5. Click on `Tools & files` and then on `Secrets`
6. Click on `New Secret`, as key you enter `DISCORD_TOKEN` and for value you paste your discord token
7. Click on `Add Secret` and then click on the Play button to start the bot
