import asyncio
import time
from typing import List, Dict

import aiohttp
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.core.document import Document
from src.core.index import InvertedIndex
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main function to run tests"""
    try:
        logger.info("Starting indexing tests")

        # Loading documents
        logger.info("Loading documents from URLs...")
        documents = load_documents_from_urls('internal_links.txt')

        if not documents:
            logger.error("Failed to load documents for testing")
            return

        # Testing without compression
        logger.info("Running test without compression...")
        no_compression = indexation(documents, False)

        # Testing with compression
        logger.info("Running test with compression...")
        with_compression = indexation(documents, True)

        # Logging results
        logger.info("\nTest results:")
        logger.info(f"Indexing time (no compression): {no_compression['indexing_time']:.2f} sec")
        logger.info(f"Indexing time (with compression): {with_compression['indexing_time']:.2f} sec")
        logger.info(f"Index size (no compression): {no_compression['index_size'] / (1024 * 1024):.2f} MB")
        logger.info(f"Index size (with compression): {with_compression['index_size'] / (1024 * 1024):.2f} MB")
        logger.info(f"Search time (no compression): {no_compression['search_time']:.4f} sec")
        logger.info(f"Search time (with compression): {with_compression['search_time']:.4f} sec")
        logger.info(f"Documents found (no compression): {no_compression['results_count']}")
        logger.info(f"Documents found (with compression): {with_compression['results_count']}")

        # Calculating ratios
        compression_ratio = no_compression['index_size'] / with_compression['index_size']
        slowdown_factor = with_compression['indexing_time'] / no_compression['indexing_time']

        logger.info(f"\nCompression ratio: {compression_ratio:.2f}x")
        logger.info(f"Indexing slowdown: {slowdown_factor:.2f}x")

    except Exception as e:
        logger.error(f"Error during testing: {str(e)}", exc_info=True)


def indexation(documents: list[dict], use_compression: bool) -> dict:
    """
    Testing indexing and search performance
    """
    index = InvertedIndex(use_compression=use_compression)
    start_time = time.time()

    # Indexing documents
    for doc in documents:
        try:
            index.add_document(Document(doc['doc_id'], doc['text'], doc['metadata']))
        except Exception as e:
            logger.debug(f"Error adding document {doc['doc_id']}: {str(e)}")
            continue

    indexing_time = time.time() - start_time

    # Calculate approximate index size
    index_size = sum(
        len(term.encode('utf-8')) + len(encoded_postings)
        for term, encoded_postings in index.index.items()
    )

    # Testing search performance
    search_start = time.time()
    results = index.search("Ректор СПбГУ")
    results_count = len(results)
    search_time = time.time() - search_start

    return {
        'indexing_time': indexing_time,
        'index_size': index_size,
        'search_time': search_time,
        'results_count': results_count
    }


async def fetch_and_process(session: aiohttp.ClientSession, url: str, doc_id: int) -> Dict:
    """Fetch and process single URL"""
    try:
        # Skip binary files
        if any(url.lower().endswith(ext) for ext in
               ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx']):
            logger.debug(f"Skipping binary file: {url}")
            return None

        async with session.get(url, timeout=10) as response:
            # Skip error responses
            if response.status != 200:
                logger.debug(f"Skipping URL with HTTP {response.status}: {url}")
                return None

            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type:
                logger.debug(f"Skipping non-HTML content: {url} ({content_type})")
                return None

            html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()

        text = soup.get_text(separator=' ', strip=True)
        title = soup.title.string if soup.title else url

        return {
            'doc_id': doc_id,
            'url': url,
            'text': text,
            'metadata': {
                'title': title,
                'source': 'spbu.ru'
            }
        }

    except Exception as e:
        logger.debug(f"Error processing {url}: {str(e)}")
        return None


async def process_batch(urls: List[str], max_workers: int = 10) -> List[Dict]:
    """Process batch of URLs with limited concurrency"""
    connector = aiohttp.TCPConnector(limit=max_workers)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for doc_id, url in enumerate(urls, 1):
            tasks.append(fetch_and_process(session, url, doc_id))

        results = []
        for future in tqdm(asyncio.as_completed(tasks), total=len(urls), desc="Processing URLs"):
            result = await future
            if result:
                results.append(result)
        return results


def load_documents_from_urls(file_path: str, max_docs: int = 40000) -> List[Dict]:
    """
    Loads documents from URLs listed in a file asynchronously
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        logger.info(f"Found {len(lines)} URLs in file {file_path}")
        urls = [line.strip().split()[0] for line in lines[:max_docs]]

        # Run async processing
        loop = asyncio.get_event_loop()
        documents = loop.run_until_complete(process_batch(urls))

        logger.info(f"Successfully loaded {len(documents)} documents")
        return documents

    except Exception as e:
        logger.error(f"Error reading file {file_path}: {str(e)}")
        raise


if __name__ == "__main__":
    main()
