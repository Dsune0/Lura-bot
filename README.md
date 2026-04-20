# Lura Bot

Bot that creates panels with buttons to move specific users between two voice channels.

---

## 1. Create and Set Up the Bot

Go to the [Discord Developer Portal](https://discord.com/developers/applications)

### Create the bot

1. Create a new application
2. Go to **Bot** → **Add Bot**
3. Copy the **Bot Token** (keep it secret)

---

### Enable required settings

**Bot → Privileged Gateway Intents**

* Enable **Server Members Intent**

---

### Configure install permissions

**Installation → Default Install Settings → Guild Install**

**Scopes:**

* `bot`
* `applications.commands`

**Permissions:**

* `Move Members`
* `View Channels`
* `Send Messages`
* `Embed Links`

Use the generated URL to invite the bot to your server.
Make sure the bot role has access to the relevant voice and text channels.

---

## 2. Run on Replit

1. Go to Replit
2. Click **Import code or design**
3. Choose **GitHub** and paste:

   ```
   https://github.com/Dsune0/Lura-bot
   ```
4. Import the repo
5. Open **Secrets**
6. Add:

   * Key: `DISCORD_TOKEN`
   * Value: your bot token
7. Click **Run**

---

## 3. Run Locally

### Clone and install

```bash
git clone https://github.com/Dsune0/Lura-bot
cd Lura-bot
pip install -U discord.py
```

---

### Configure token

Create a file named `config.json`:

```json
{
  "token": "your_token_here"
}
```

**Important:**
Do not upload `config.json` to GitHub. Keep it in `.gitignore`.

---

### Run the bot

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
/create_comp from_channel:Raid to_channel:Party1 users:@user1 @user2
```

---

## Panel Behavior

Each panel shows:

* **From channel**
* **To channel**
* **Users**

Buttons:

* **Move** → moves listed users from `from_channel` → `to_channel`
* **Move Back** → moves listed users from `to_channel` → `from_channel`

---

## Notes

* Panels are saved in `panels.json`
* Buttons persist after bot restarts
* Only users with **Move Members** permission can use the panel
