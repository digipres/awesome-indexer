import os
import sys
import yaml
import asyncio
import logging
from pagefind.index import PagefindIndex, IndexConfig
from .awelist import parse_awesome_list
from .zotero import parse_zotero
from .models import Settings
from pydantic import ValidationError

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)


def prefix(pre: str, s: str) -> str:
    return pre + s.replace("\n", f"\n{pre}")


async def async_main(config: Settings):
    index_config = IndexConfig(
        root_selector="main", logfile="index.log", output_path="./output", verbose=True
    )
    async with PagefindIndex(config=index_config) as index:
        log.debug("opened index")
        # Add custom records:
        for source in config.sources:
            log.info(f"Indexing {source.name}...")
            if source.type == "awesome-list":
                for pf in parse_awesome_list(source.url, source=source.name):
                    await index.add_custom_record(**(dict(pf)))
            elif source.type == "zotero":
                for pf in parse_zotero(source.library_id, source.library_type, collection_id=source.collection_id, source=source.name):
                    await index.add_custom_record(**(dict(pf)))
            else:
                log.warning(f"No implementation for source type {source.type}! Skipping {source.name}.")
 
        files = await index.get_files()
        for file in files:
            print(prefix("files", f"{len(file['content']):10}B {file['path']}"))


def main(config):
    asyncio.run(async_main(config))


if __name__ == "__main__":    
    with open("config.yaml", "r") as file:
        try:
            config = Settings(**yaml.safe_load(file))
            main(config)
        except ValidationError as e:
            log.exception("Invalid configuration file", e)