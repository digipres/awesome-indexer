import os
import json
import asyncio
import logging
from pagefind.index import PagefindIndex, IndexConfig
from .awelist import parse_awesome_list

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)


def prefix(pre: str, s: str) -> str:
    return pre + s.replace("\n", f"\n{pre}")


async def async_main():
    config = IndexConfig(
        root_selector="main", logfile="index.log", output_path="./output", verbose=True
    )
    async with PagefindIndex(config=config) as index:
        log.debug("opened index")
        await index.add_custom_record(
                url="/elephants/",
                content="Some testing content regarding elephants",
                language="en",
                meta={"title": "Elephants"},
            )
        # Add custom records:
        with open('test/awesome-digital-preservation.md', 'r') as fin:
            for pf in parse_awesome_list(fin, source="Awesome Digital Preservation"):
                await index.add_custom_record(**(dict(pf)))
 
        files = await index.get_files()
        for file in files:
            print(prefix("files", f"{len(file['content']):10}B {file['path']}"))


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()