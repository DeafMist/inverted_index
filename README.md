# Inverted Index with Compression

This project implements an inverted index with support for delta and Elias gamma/delta compression.

## Installation

1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`

## Usage

```python
from src.core.index import InvertedIndex
from src.core.document import Document

# Create index
index = InvertedIndex(use_compression=True)

# Add documents
doc1 = Document(1, "This is a test document about SPbSU")
doc2 = Document(2, "Another document mentioning MSU and SPbSU")
index.add_document(doc1)
index.add_document(doc2)

# Search
results = index.search("SPbSU")
for doc in results:
    print(doc.text)
```
