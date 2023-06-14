from typing import List, Callable


def button_row_layout(count: int) -> List[int]:
  """
  Расставляет кнопки по рядам, чтобы было красиво
  
  :param count: количество кнопок
  :return: список чисел, каждое из которых представляет сколько кнопок должно быть в данном ряду
  """
  return ([]      if count < 1  else
          [count] if count <= 3 else
          [2, 2]  if count == 4 else
          [3] + button_row_layout(count-3))


def list_to_layout(elems: [], transform: Callable) -> List[List]:
  """
  Распределяет элементы по рядам, чтобы было красиво:
  8 элементов:   7 элементов:
  * * *          * * *
  * * *           * *
   * *            * *
  
  :param elems: элементы, которые нужно распределить
  :param transform: функция трансформации элементов (то же, что первый аргумент функции map)
  :return: элементы, красиво распределённые по рядам
  """
  layout = button_row_layout(len(elems))
  pos = 0
  result = []
  for row_width in layout:
    result.append([transform(elems[i]) for i in range(pos, pos+row_width)])
    pos += row_width
  return result
