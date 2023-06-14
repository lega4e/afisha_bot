import json
import re
import traceback

from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEvent, VkBotEventType, DotDict

from src.domain.locator import LocatorStorage, Locator
from src.utils.tg.piece import P


class Vk(LocatorStorage):
  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.config = self.locator.config()
    self.logger = self.locator.logger()
    self.vk = VkApi(token=self.config.vkToken())
    self.groupId = self.config.vkGroupId()
    self.longpoll = VkBotLongPoll(self.vk, self.groupId)
    
    
  def startLongpoll(self):
    self.logger.info('longpoll started')
    while True:
      try:
        for event in self.longpoll.listen():
          self.handleEvent(event)
      except Exception as e:
        self.logger.error(str(e))
        self.logger.info('Переподключение...')
        
        
  def handleEvent(self, event: VkBotEvent):
    if event.type == VkBotEventType.MESSAGE_NEW:
      self.handleMessage(event.object.message)
    elif (event.type == VkBotEventType.WALL_POST_NEW and
          event.object['post_type'] == 'post'):
      try:
        if "copy_history" in event.object:
          self.handlePost(event.object.copy_history[0], event.object['text'])
        else:
          self.handlePost(event.object)
      except Exception:
        self.logger.error(traceback.format_exc())
        
        
  def handleMessage(self, message):
    self.logger.info('Message: ', message['text'])
        
        
  def handlePost(self, post: DotDict, title: str = None):
    self.logger.info(f'handle post {json.dumps(post)}')
    if 'fnon' in post['text']:
      return
    text = self._makePostText(post, title)

    if 'attachments' in post:
      attachments = post['attachments']
      photos = []
      for a in attachments:
        if 'photo' in a:
          photos.append(self._getPhoto(a['photo']['sizes']))
        elif a['type'] == 'poll':
          text += "\n\n" + P("Принять участие в опросе",
                             url=self._makePostLink(post['id'])) + "\n"
        elif a['type'] == 'link' and 'vk.com/@' in a['link']['url']:
          text += '\n\n' + P('Ссылка на статью',
                             url=self._makePostLink(post['id'])) + '\n'
    
      if len(photos) > 0:
        self.locator.tg().sendPhotos(photos, text)
      elif text != '':
        self.locator.tg().post(text)

    elif text != '':
      self.locator.tg().post(text)
      
      
  def _makePostLink(self, id: int):
    return f'https://vk.com/wall{self.groupId}_{id}'
    
    
  @staticmethod
  def _makePostText(post: DotDict, title: str = None):
    text = P(title + '\n—————\n\n' if title is not None and title != '' else '' + post['text'])
    text = P('  ') + text + '  '
    while True:
      m = re.search(r'\[(id|club)(\d+)\|([^]]+)]', text.toString())
      if m is None:
        break
      text = (text[:m.span(0)[0]] +
              P(m.group(3), url=f'vk.com/{m.group(1)}{m.group(2)}') +
              text[m.span(0)[1]:])
    strtext = text.toString()
    m = re.search(r'ссылка: (.*)', strtext, flags=re.IGNORECASE)
    if m is None:
      return text
    start = strtext.find(': ', strtext.find('\n')) + 2
    end = strtext.find('\n', start)
    return (
      text[:start] + P(strtext[start:end], url=m.group(1)) +
      text[end:m.span(0)[0]] + text[m.span(0)[1]+1:]
    )
  
  
  @staticmethod
  def _getPhoto(sizes):
    for x in ["w", "z", "y"]:
      for i in sizes:
        if i['type'] == x:
          return i['url']
    index = len(sizes) - 1
    return sizes[index]['url']

# END