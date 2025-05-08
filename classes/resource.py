from aiogram.types import FSInputFile
from aiofiles import open as aio_open
from typing import List, Optional, Dict, Union, AsyncIterator
from pathlib import Path

from classes.enums import ResourcePath, Extensions


class Button:
    def __init__(self, path: str) -> None:
        """
        Инициализирует кнопку с заданным путем.

        :param path: Имя файла без расширения (без .txt).
        """
        self.name: Optional[str] = None
        self._path: Path = Path(ResourcePath.PROMPTS.value, f'{path}{Extensions.TXT.value}')
        self.callback: str = path
    
    async def load_name(self) -> None:
        """
        Загружает имя знаменитости из текстового файла.

        :return: None
        """
        async with aio_open(self._path, 'r', encoding='UTF-8') as txt_file:
            self.name = await self._extract_celebrity_name(await txt_file.readline())
    
    @staticmethod
    async def _extract_celebrity_name(input_string: str) -> str:
        """
        Извлекает текст из строки, начиная с 5-го знака и заканчивая перед запятой.

        :param input_string: Исходная строка.
        :return: Извлеченный текст.
        """
        start_index = 4  # Начинаем с пятого знака (индекс 4)
        comma_index = input_string.find(',')
        
        if comma_index == -1:
            # Если запятая не найдена, возвращаем подстроку от "start_index" до конца строки
            return input_string[start_index:]
        
        return input_string[start_index:comma_index]


class Buttons:
    def __init__(self) -> None:
        """
        Инициализирует коллекцию кнопок.
        """
        self.buttons: List[Button] = []
    
    async def load_buttons(self) -> List[Button]:
        """
        Загружает кнопки из файлов, начинающихся с 'talk_'.

        :return: Список загруженных кнопок.
        """
        resource_path = Path(ResourcePath.PROMPTS.value)
        # Получаем список файлов, которые начинаются с 'talk_'
        buttons_list = [file for file in resource_path.iterdir() if file.is_file() and file.name.startswith('talk_')]
        self.buttons = [Button(file.stem) for file in buttons_list]
        
        # Загружаем имена кнопок асинхронно
        await self.load_buttons_names()
        return self.buttons
    
    async def load_buttons_names(self) -> None:
        """
        Загружает имена всех кнопок асинхронно.

        :return: None
        """
        for button in self.buttons:
            await button.load_name()
    
    def __iter__(self) -> AsyncIterator[Button]:
        """
        Возвращает итератор для кнопок.

        :return: Итератор кнопок.
        """
        return self
    
    def __next__(self) -> Button:
        """
        Возвращает следующую кнопку.

        :return: Следующая кнопка.
        :raises StopIteration: Если кнопки закончились.
        """
        if self.buttons:
            return self.buttons.pop(0)
        raise StopIteration


class Resource:
    """
    Класс для работы с ресурсами, такими как изображения и текстовые файлы.

    :param file_name: Имя файла, используемое для генерации путей к ресурсам.
    """
    
    def __init__(self, file_name: str) -> None:
        self._file_name = file_name
    
    def _get_path(self, resource_type: str, extension: str) -> Path:
        """
        Получает путь к ресурсу.

        :param resource_type: Тип ресурса (например, 'images' или 'messages').
        :param extension: Расширение файла (например, '.jpg' или '.txt').
        :return: Путь к ресурсу.
        """
        return Path(resource_type, f'{self._file_name}{extension}')
    
    @property
    def photo(self) -> Optional[FSInputFile]:
        """
        Получает объект изображения, если он существует.

        :return: Объект изображения или None, если файл не найден.
        """
        photo_path = self._get_path(ResourcePath.IMAGES.value, Extensions.JPG.value)
        if photo_path.exists():
            return FSInputFile(photo_path)
        return None
    
    @property
    async def text(self) -> Optional[str]:
        """
        Асинхронно получает текст из файла, если он существует.

        :return: Содержимое текстового файла или None, если файл не найден.
        """
        text_path = self._get_path(ResourcePath.MESSAGES.value, Extensions.TXT.value)
        if text_path.exists():
            async with aio_open(text_path, 'r', encoding='UTF-8') as file:
                return await file.read()
        return None
    
    def as_kwargs(self) -> Dict[str, Union[FSInputFile, str]]:
        """
        Возвращает словарь с ресурсами в виде ключей и значений.

        :return: Словарь с изображением и текстом.
        """
        return {'photo': self.photo, 'caption': self.text}
