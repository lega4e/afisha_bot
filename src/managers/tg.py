from telebot import TeleBot

from src.domain.locator import LocatorStorage, Locator
from src.utils.tg.send_message import send_message


class Tg(LocatorStorage):
  def __init__(self, locator: Locator, tg: TeleBot):
    super().__init__(locator)
    self.tg = tg
    self.config = locator.config()
    self.chatId = self.config.tgChatId()
    self.logger = locator.logger()

  def post(self, text):
    self.logger.info(f'post {text}')
    send_message(self.tg, self.chatId, text=text)

  def sendPhotos(self, urls, text):
    self.logger.info(f'send photos {urls} | {text}')
    send_message(self.tg, self.chatId, text=text, media=urls, media_type='photo')
 