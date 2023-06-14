class Locator:
  def __init__(self):
    self._config = None
    self._logger = None
    self._loggerStream = None
    self._master = None
    self._telebot = None
    self._tg = None
    self._vk = None

  def config(self):
    if self._config is None:
      from src.domain.config import Config
      self._config = Config()
    return self._config

  def logger(self):
    if self._logger is None:
      import logging
      logging.basicConfig(
        format=self.config().loggingFormat(),
        datefmt=self.config().loggingDateFormat(),
        stream=self.loggerStream(),
      )
      self._logger = logging.getLogger('global')
      self._logger.setLevel(logging.INFO)
      self._logger.com = lambda com, m: self._logger.info(f'{com} {m.chat.id}')
    return self._logger

  def loggerStream(self):
    if self._loggerStream is None:
      from src.utils.tg.tg_logger_stream import TelegramLoggerStream
      self._loggerStream = TelegramLoggerStream(
        chats=self.config().loggingDefaultChats(),
        tg=self.telebot()
      )
    return self._loggerStream

  def master(self):
    if self._master is None:
      from src.managers.master import Master
      self._master = Master()
    return self._master

  def telebot(self):
    if self._telebot is None:
      from telebot import TeleBot
      self._telebot = TeleBot(token=self.config().tgToken())
    return self._telebot

  def tg(self):
    if self._tg is None:
      from telebot import TeleBot
      from src.managers.tg import Tg
      self._tg = Tg(self, tg=self.telebot())
    return self._tg
  
  def vk(self):
    if self._vk is None:
      from src.managers.vk import Vk
      self._vk = Vk(self)
    return self._vk



class LocatorStorage:
  def __init__(self, locator: Locator = None):
    self.locator = locator or Locator


_global_locator = Locator()


def glob():
  return _global_locator



# END