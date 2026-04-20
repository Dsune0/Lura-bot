import json
import os
import re
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

PANELS_FILE = "panels.json"

def get_token():
    token = os.getenv("DISCORD_TOKEN")
    if token:
        return token

    if os.path.exists("config.json"):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("token")
        except (json.JSONDecodeError, OSError):
            pass

    return None

def load_panels() -> list[dict[str, Any]]:
    if not os.path.exists(PANELS_FILE):
        return []
    try:
        with open(PANELS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def save_panels(panels: list[dict[str, Any]]) -> None:
    with open(PANELS_FILE, "w", encoding="utf-8") as f:
        json.dump(panels, f, indent=2)


def next_panel_id(panels: list[dict[str, Any]]) -> int:
    if not panels:
        return 1
    return max(int(panel.get("panel_id", 0)) for panel in panels) + 1


def parse_user_ids(raw: str) -> list[int]:
    ids = set()
    for token in raw.split():
        match = re.fullmatch(r"<@!?(\d+)>", token)
        if match:
            ids.add(int(match.group(1)))
        elif token.isdigit():
            ids.add(int(token))
    return sorted(ids)


class MovePanelView(discord.ui.View):
    def __init__(self, panel_id: int):
        super().__init__(timeout=None)
        self.panel_id = panel_id

        self.add_item(
            discord.ui.Button(
                label="Move",
                style=discord.ButtonStyle.primary,
                custom_id=f"move:{panel_id}",
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Move Back",
                style=discord.ButtonStyle.secondary,
                custom_id=f"moveback:{panel_id}",
            )
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message(
                "You need the `Move Members` permission to use this panel.",
                ephemeral=True,
            )
            return False
        return True

    async def on_error(
        self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item
    ) -> None:
        return

    async def _handle_move(self, interaction: discord.Interaction, direction: str) -> None:
        panels = load_panels()
        panel = next((p for p in panels if int(p["panel_id"]) == self.panel_id), None)

        if panel is None:
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True, thinking=False)
            return

        guild = interaction.guild
        if guild is None or guild.id != int(panel["guild_id"]):
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True, thinking=False)
            return

        from_channel = guild.get_channel(int(panel["from_channel_id"]))
        to_channel = guild.get_channel(int(panel["to_channel_id"]))

        if not isinstance(from_channel, discord.VoiceChannel) or not isinstance(
            to_channel, discord.VoiceChannel
        ):
            if not interaction.response.is_done():
                await interaction.response.defer(ephemeral=True, thinking=False)
            return

        source = from_channel if direction == "move" else to_channel
        target = to_channel if direction == "move" else from_channel

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True, thinking=False)

        for user_id in panel["user_ids"]:
            member = guild.get_member(int(user_id))
            if member is None:
                try:
                    member = await guild.fetch_member(int(user_id))
                except (discord.NotFound, discord.HTTPException):
                    continue

            voice_state = member.voice
            if voice_state is None or voice_state.channel is None:
                continue

            if voice_state.channel.id != source.id:
                continue

            try:
                await member.move_to(target, reason=f"Voice Move Panel #{self.panel_id}")
            except discord.HTTPException:
                continue


class MoveButton(discord.ui.DynamicItem[discord.ui.Button], template=r"move:(?P<panel_id>\d+)"):
    def __init__(self, panel_id: int):
        super().__init__(
            discord.ui.Button(
                label="Move",
                style=discord.ButtonStyle.primary,
                custom_id=f"move:{panel_id}",
            )
        )
        self.panel_id = panel_id

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(int(match["panel_id"]))

    async def callback(self, interaction: discord.Interaction):
        view = MovePanelView(self.panel_id)
        await view._handle_move(interaction, "move")


class MoveBackButton(
    discord.ui.DynamicItem[discord.ui.Button], template=r"moveback:(?P<panel_id>\d+)"
):
    def __init__(self, panel_id: int):
        super().__init__(
            discord.ui.Button(
                label="Move Back",
                style=discord.ButtonStyle.secondary,
                custom_id=f"moveback:{panel_id}",
            )
        )
        self.panel_id = panel_id

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(int(match["panel_id"]))

    async def callback(self, interaction: discord.Interaction):
        view = MovePanelView(self.panel_id)
        await view._handle_move(interaction, "moveback")


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.members = True
        intents.voice_states = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        self.add_dynamic_items(MoveButton, MoveBackButton)

        for panel in load_panels():
            self.add_view(MovePanelView(int(panel["panel_id"])))

        await self.tree.sync()


bot = Bot()


@bot.tree.command(name="create_comp")
@app_commands.checks.has_permissions(move_members=True)
async def create_comp(
    interaction: discord.Interaction,
    from_channel: discord.VoiceChannel,
    to_channel: discord.VoiceChannel,
    users: str,
):
    user_ids = parse_user_ids(users)

    if not user_ids:
        await interaction.response.send_message(
            "Use mentions or space-separated user IDs.",
            ephemeral=True,
        )
        return

    panels = load_panels()
    panel_id = next_panel_id(panels)

    view = MovePanelView(panel_id)
    embed = discord.Embed(title="Voice Move Panel")

    await interaction.response.defer(ephemeral=True)

    message = await interaction.channel.send(embed=embed, view=view)

    panels.append(
        {
            "panel_id": panel_id,
            "guild_id": interaction.guild_id,
            "channel_id": interaction.channel_id,
            "message_id": message.id,
            "from_channel_id": from_channel.id,
            "to_channel_id": to_channel.id,
            "user_ids": user_ids,
        }
    )
    save_panels(panels)


if __name__ == "__main__":
    token = get_token()
    if not token:
        raise RuntimeError("Set DISCORD_TOKEN")
    bot.run(token)
