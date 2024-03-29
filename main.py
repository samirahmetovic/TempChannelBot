import discord
import psycopg2


class Secret:
    host = ""
    database = ""
    user = ""
    password = ""
    token = ""


my_secrets = Secret()

class ArenaClient(discord.Client):

    async def on_ready(self):
        global my_secrets
        print("connect to Database")
        # connect to DB
        self.connection = psycopg2.connect(
            host=my_secrets.host,
            database=my_secrets.database,
            user=my_secrets.user,
            password=my_secrets.password,
        )
        self.message_handler = Message_Handler("t!", ["help", "setup", "reset", "admin"])


    async def on_message(self, message):
        command = self.message_handler.validate_message(message)

        if command["is_valid"]:

            auth = self.check_admin(message)

            if command["command"] == "setup":
                if auth == "role_admin" or auth == "guild_admin":
                    await self.setup(message)
                else:
                    await message.channel.send("not authorized")

            elif command["command"] == "reset":
                if auth == "role_admin" or auth == "guild_admin":
                    await self.reset(message)
                else:
                    await message.channel.send("not authorized")

            elif command["command"] == "admin":
                if auth == "guild_admin":
                    await self.admin(message)
                else:
                    await message.channel.send("not authorized for that command")



    # is called wenn member changes state in voice channel
    async def on_voice_state_update(self, member, before, after):
        if not before.channel and not after.channel:
            return
        guild_id = ""
        if before.channel:
            guild_id = before.channel.guild.id
        else:
            guild_id = after.channel.guild.id

        curser = self.connection.cursor()
        curser.execute(f"SELECT * FROM dc_server WHERE guild_id = '{guild_id}'")
        tupel = curser.fetchone()

        # if after is "create Tempchannel
        if after.channel:
            if tupel:
                if after.channel.id == int(tupel[2]):
                    tmpchannel = await after.channel.guild.create_voice_channel(f"{member.name}'s channel",
                                                                                category=after.channel.category)
                    await tmpchannel.edit(sync_permissions=False)
                    permsission = tmpchannel.permissions_for(member)
                    overwrite = discord.PermissionOverwrite(manage_channels=True)
                    await tmpchannel.set_permissions(member, overwrite=overwrite)
                    await member.move_to(tmpchannel)

            # if somebody change VC check if one of tempchannel is empty
        cat_id = int(tupel[1])
        try:
            if before.channel.category_id == cat_id:
                if len(before.channel.members) == 0 and not before.channel.id == int(tupel[2]):
                    await before.channel.delete()
        except:
            pass

    # ******************************************************************************************************

    async def setup(self, message):
        curser = self.connection.cursor()
        curser.execute(f"SELECT * FROM dc_server WHERE guild_id = '{message.guild.id}'")
        # curser.execute(f"INSERT INTO dc_server VALUES ('{message.guild.id}', '{}')")
        tupel = curser.fetchone()
        if not tupel:
            cat = await message.guild.create_category("TempChannel 🔊")
            vc = await message.guild.create_voice_channel("Create Tempchannel 🔊", category=cat)
            curser.execute(f"INSERT INTO dc_server VALUES ('{message.guild.id}', '{cat.id}', '{vc.id}')")
            self.connection.commit()
            await message.channel.send("Tempchannels are created and ready to use")
        else:
            await message.channel.send("You're server has tempchannels yet. If there is an error, try a!reset")

    # ******************************************************************************************************

    async def reset(self, message):
        curser = self.connection.cursor()
        curser.execute(f"SELECT * FROM dc_server WHERE guild_id = '{message.guild.id}'")
        tupel = curser.fetchone()
        curser.execute(f"DELETE FROM dc_server WHERE guild_id = '{message.guild.id}'")
        self.connection.commit()
        for channel in message.guild.channels:
            try:
                if channel.category.id == int(tupel[1]):
                    try:
                        await channel.delete()
                    except:
                        pass
            except:
                pass

        for category in message.guild.categories:
            try:
                if category.id == int(tupel[1]):
                    try:
                        await category.delete()
                    except:
                        pass
            except:
                pass

        await message.channel.send("You're tempchannels are deleted")

    # ******************************************************************************************************

    async def admin(self, message):
        if len(message.role_mentions) == 1:
            role = message.role_mentions[0]
            cursor = self.connection.cursor()
            cursor.execute(f"UPDATE dc_server SET admin_role = '{role.id}' WHERE guild_id = '{message.guild.id}'")
            self.connection.commit()
            await message.channel.send(f"Role {role.mention} is now able to execute commands")

    # ******************************************************************************************************

    def check_admin(self, message):
        admin_role_id = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT admin_role FROM dc_server WHERE guild_id = '{message.guild.id}'")
            admin_role_id = cursor.fetchone()[0]
        except:
            pass

        auth = False

        if message.author.guild_permissions.administrator:
            return "guild_admin"

        if admin_role_id:
            if any(role.id == int(admin_role_id) for role in message.author.roles):
                return "role_admin"

        return auth



class Message_Handler:
    def __init__(self, dc_prefix, accepted_commands):
        self.dc_prefix = dc_prefix
        self.accepted_commands = accepted_commands

    def validate_message(self, message):
        message_content = message.content.split()
        prefix_command = message_content[0]
        arguments = message_content[1:]
        if prefix_command.startswith(self.dc_prefix):
            command = prefix_command.split(self.dc_prefix)[1]
            if command in self.accepted_commands:
                return {
                    "is_valid": True,
                    "command": command,
                    "arguments": arguments
                }

        return {
            "is_valid": False
        }

client = ArenaClient()
client.run(my_secrets.token)