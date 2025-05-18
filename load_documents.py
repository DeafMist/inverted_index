import asyncio
from typing import List, Dict

import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_documents_from_urls(file_path: str, max_docs: int = 40000) -> List[Dict]:
    """
    Асинхронная загрузка документов из URL-адресов, указанных в файле
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        logger.info(f"Найдено {len(lines)} URL-адресов в файле {file_path}")
        urls = [line.strip().split()[0] for line in lines[:max_docs]]

        # Запуск асинхронной обработки
        loop = asyncio.get_event_loop()
        documents = loop.run_until_complete(process_batch(urls))

        logger.info(f"Успешно загружено {len(documents)} документов")
        return documents

    except Exception as e:
        logger.error(f"Ошибка чтения файла {file_path}: {str(e)}")
        raise


async def process_batch(urls: List[str], max_workers: int = 10) -> List[Dict]:
    """Обработка пакета URL-адресов с ограниченной параллельностью"""
    connector = aiohttp.TCPConnector(limit=max_workers)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for doc_id, url in enumerate(urls, 1):
            tasks.append(fetch_and_process(session, url, doc_id))

        results = []
        for future in tqdm(asyncio.as_completed(tasks), total=len(urls), desc="Обработка URL-адресов"):
            result = await future
            if result:
                results.append(result)
        return results


async def fetch_and_process(session: aiohttp.ClientSession, url: str, doc_id: int) -> Dict:
    """Загрузка и обработка одного URL-адреса"""
    try:
        # Пропуск бинарных файлов
        if any(url.lower().endswith(ext) for ext in
               ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx']):
            logger.debug(f"Пропуск бинарного файла: {url}")
            return None

        async with session.get(url, timeout=10) as response:
            # Пропуск ответов с ошибками
            if response.status != 200:
                logger.debug(f"Пропуск URL с HTTP {response.status}: {url}")
                return None

            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.debug(f"Пропуск не-HTML контента: {url} ({content_type})")
                return None

            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Удаление ненужных элементов
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()

        text = soup.get_text(separator=' ', strip=True)
        title = soup.title.string if soup.title else url

        return {
            'doc_id': doc_id,
            'text': text,
            'metadata': {
                'title': title,
                'source': 'spbu.ru',
                'url': url
            }
        }

    except Exception as e:
        logger.debug(f"Ошибка обработки {url}: {str(e)}")
        return None
