from typing import Union


class TgDestination:
  """
  Представляет собой чат или топик, куда может быть отправлено сообщение; либо
  само сообщение, которое должно быть обновлено
  """
  def __init__(
    self,
    chat_id: Union[int, str],
    message_to_replay_id: int = None,
    translate_to_message_id: int = None,
  ):
    self.chatId = chat_id
    self.messageToReplayId = message_to_replay_id
    self.translateToMessageId = translate_to_message_id
    
  def getUrl(self):
    chat = str(self.chatId) if isinstance(self.chatId, int) else self.chatId[1:]
    return (f't.me/{chat}' +
            ('' if self.messageToReplayId is None else f'/{self.messageToReplayId}') +
            ('' if self.translateToMessageId is None else f'/{self.translateToMessageId}'))


def proveTgDestination(chat) -> TgDestination:
  if isinstance(chat, TgDestination):
    return chat
  return TgDestination(chat_id=chat)



# END