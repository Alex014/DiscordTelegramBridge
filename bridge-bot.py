import discord

from telegram.ext import Updater

import re
import json
from pprint import pprint

# Discord -> telegram Bridge BOT by Chosen One

class MyClient(discord.Client):
    def __init__(self):
        super(MyClient, self).__init__()
        self.__load_settings()
        self.updater = Updater(token=self.config["telegram"]["token"], use_context=True)

    def run(self):
        super(MyClient, self).run(self.config["discord"]["token"])

    def __load_settings(self):
        try:
            f = open('config.json', 'r')
        except IOError:
            print('No config.json file, you must create it, see readme.md !')
        finally:
            f.close()
            content = f.read()
            self.config = json.loads(content)

    @staticmethod
    def __file_type(attachment):
        a_filename = attachment.filename.split('.')
        ext = a_filename[len(a_filename) - 1]
        if ext == 'mp4' or ext == 'avi' or ext == 'mkv':
            return 'v'
        elif attachment.width is not None:
            return 'p'
        else:
            return 'o'

    @staticmethod
    def __message_has_links(message):
        res = re.search("(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?", message.content)
        return res is not None

    @staticmethod
    def __make_message(message):
        txt = " *{}* \n".format(message.author.name) + \
              message.content + \
              "\n [Discord link]({})".format(message.jump_url)
        return txt

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        disable_web_page_preview = not self.__message_has_links(message)

        if self.config["channels"][message.channel.name]:
            txt = self.__make_message(message)
            message_sent = self.updater.bot.send_message(chat_id=self.config["channels"][message.channel.name],
                                                         text=txt,
                                                         parse_mode='Markdown',
                                                         disable_web_page_preview=disable_web_page_preview)

            for attachment in message.attachments:
                if self.__file_type(attachment) == 'v':
                    self.updater.bot.send_video(chat_id=self.config["channels"][message.channel.name],
                                                video=attachment.url,
                                                reply_to_message_id=message_sent.message_id)
                elif self.__file_type(attachment) == 'p':
                    self.updater.bot.send_photo(chat_id=self.config["channels"][message.channel.name],
                                                photo=attachment.url,
                                                reply_to_message_id=message_sent.message_id)

            return

        return


client = MyClient()
client.run()