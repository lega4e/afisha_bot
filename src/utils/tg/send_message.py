from copy import copy
from typing import Union, List

from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, InputMediaPhoto, InputMediaVideo, InputMediaAudio

from .tg_destination import TgDestination, proveTgDestination
from .piece import Pieces, provePiece


class TgMediaType:
  PHOTO = 'photo'
  VIDEO = 'video'
  AUDIO = 'audio'


def send_message(
  tg: TeleBot,
  chat: Union[TgDestination, str, int],
  text: Union[str, Pieces],
  media: [] = None,
  media_type: Union[str, TgMediaType] = None,
  disable_web_page_preview = True,
  reply_markup = None,
  answer_callback_query_id: int = None,
  answer_callback_query_text: str = None,
) -> List[Message]:
  """
  Отправляет или обновляет сообщение в телеграм

  :param tg: Телебот

  :param chat: куда отправить (или какое сообщение обновить)

  :param text: текст, который отправить

  :param media: фото, видео или аудио, которые нужно отправить

  :param media_type: тип медиа

  :param disable_web_page_preview: см. Telebot.send_message()

  :param reply_markup: см. Telebot.send_message()

  :param answer_callback_query_id: см. Telebot.send_message()

  :param answer_callback_query_text: см. Telebot.send_message()

  :return: то же, что и Telebot.send_message()
  """
  if media is not None and not isinstance(media, list):
    media = [media]

  chat = proveTgDestination(chat)
  pieces = provePiece(text)
  text, entities = pieces.toMessage()
  media_exists = media is not None and len(media) > 0 and media_type is not None
  if media_exists and len(text) > 1000 or len(text) > 3900:
    first_len = 1000 if media_exists else 3900
    m = []
    m += send_message(tg, chat, pieces[0:first_len],
                      media=media, media_type=media_type,
                      disable_web_page_preview=disable_web_page_preview,
                      reply_markup=reply_markup,
                      answer_callback_query_id=answer_callback_query_id,
                      answer_callback_query_text=answer_callback_query_text)
    original_chat = copy(chat)
    for i in range(first_len, len(text), 3900):
      if chat.translateToMessageId is not None:
        chat.translateToMessageId = original_chat.translateToMessageId + len(m)
      m += send_message(tg, chat, pieces[i:i+3900],
                        disable_web_page_preview=disable_web_page_preview)
    return m

  kwargs = {
    'chat_id' : chat.chatId,
  }

  if media_exists:
    kwargs['media'] = _transform_media(media, media_type, text, entities)
  else:
    kwargs['text'] = text
    kwargs['entities'] = entities
    kwargs['disable_web_page_preview'] = disable_web_page_preview
    kwargs['reply_markup'] = reply_markup

  if chat.translateToMessageId is not None:
    if 'media' in kwargs:
      media = kwargs.pop('media')
      m = [None] * len(media)
      def fun(index):
        m[index] = tg.edit_message_media(
          **kwargs,media=media[index],
          message_id=chat.translateToMessageId + index
        )
      for i in range(len(media)):
        _ignore_message_is_not_modified(lambda: fun(i))
    else:
      m = [None]
      def fun():
        m[0] = (tg.edit_message_text(**kwargs, message_id=chat.translateToMessageId))
      _ignore_message_is_not_modified(fun)
  else:
    kwargs['reply_to_message_id'] = chat.messageToReplayId
    m = (tg.send_media_group(**kwargs)
         if 'media' in kwargs else
         tg.send_message(**kwargs))

  if answer_callback_query_id is not None:
    tg.answer_callback_query(
      callback_query_id=answer_callback_query_id,
      text=answer_callback_query_text or text,
    )

  return m if isinstance(m, list) else [m]


def _transform_media(media: [], type: TgMediaType, text, entities) -> []:
  type = {
    TgMediaType.PHOTO: InputMediaPhoto,
    TgMediaType.VIDEO: InputMediaVideo,
    TgMediaType.AUDIO: InputMediaAudio,
  }.get(type)
  return [type(media=media[0], caption=text, caption_entities=entities),
          *[type(media=m) for m in media[1:]]]


def _ignore_message_is_not_modified(fun):
  try:
    fun()
  except ApiTelegramException as e:
    if 'message is not modified' not in str(e):
      raise e
