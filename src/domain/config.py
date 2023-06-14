import json
from typing import Union


class Config:
  CONFIG_FILE_NAME = 'config.json'
  
  def __init__(self):
    self.data = dict()
    with open(Config.CONFIG_FILE_NAME) as file:
      self.data = json.load(file)
  
  def loggingDefaultChats(self) -> [int]:
    return self._paramOrNone('logging_default_chats', list)
  
  def loggingDateFormat(self) -> str:
    return self._paramOrNone('logging_date_format', str)
  
  def loggingFormat(self) -> str:
    return self._paramOrNone('logging_format', str)

  def locale(self) -> str:
    return self._paramOrNone('locale', str)

  def tgToken(self) -> str:
    return self._paramOrNone('tg_token', str)

  def tgChatId(self) -> Union[str, int]:
    return self.data.get('tg_chat_id')

  def vkToken(self) -> str:
    return self._paramOrNone('vk_access_token', str)

  def vkGroupId(self) -> int:
    return self._paramOrNone('vk_group_id', int)

  def _paramOrNone(self, name: str, tp):
    return Config._valueOrNone(self.data.get(name), tp)
  
  @staticmethod
  def _valueOrNone(value, tp):
    return value if type(value) is tp else None
