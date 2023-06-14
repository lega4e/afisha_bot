#!python3
from src.domain.locator import glob


def main():
  vk = glob().vk()
  vk.startLongpoll()


if __name__ == '__main__':
  main()


# END