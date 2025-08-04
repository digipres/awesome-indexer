import asyncio
from typing import List
import logging
from pagefind.index import PagefindIndex, IndexConfig
from .models import Settings, IndexRecord, PageFindRecord

log = logging.getLogger(__name__)

async def async_generator(index_path, records: List[IndexRecord]):
    # Set up index config and generate:
    log.info("Generating PageFind index...")
    index_config = IndexConfig(
        root_selector="main", logfile="index.log", output_path=str(index_path), verbose=True
    )
    async with PagefindIndex(config=index_config) as index:
        # Add custom records:
        count = 0
        for ir in records:
            pf = PageFindRecord.from_index_record(ir)
            await index.add_custom_record(**(dict(pf)))
            count += 1
        # Report (don't call get_files as it returns the actual files and locks up the pipes):
        log.info(f"Indexed {count} records, now writing PageFind index files...")
    log.info("Indexing complete.")


# Take the records and convert them into a PageFind index.
def generate_pagefind_index(config: Settings, records: List[IndexRecord]):
    asyncio.run(async_generator(config, records))