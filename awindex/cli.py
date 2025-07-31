import os
import sys
import yaml
import argparse
import asyncio
import logging
from pathlib import Path
from pagefind.index import PagefindIndex, IndexConfig
from .awelist import parse_awesome_list
from .zotero import parse_zotero
from .zenodo import parse_zenodo
from .models import Settings, IndexRecord, PageFindRecord
from pydantic import ValidationError

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)


def generate_pagefind_records(config):
    # Add custom records:
    for source in config.sources:
        log.info(f"Indexing {source.name}...")
        if source.type == "awesome-list":
            for pf in parse_awesome_list(source.url, source=source.name):
                yield pf
        elif source.type == "zotero":
            for pf in parse_zotero(source.library_id, source.library_type, collection_id=source.collection_id, source=source.name):
                yield pf
        elif source.type == "zenodo":
            for pf in parse_zenodo(source):
                yield pf
        elif source.type == "jsonl":
            with open(source.file) as f:
                for line in f:
                    ir = IndexRecord.model_validate_json(line)
                    # Override the source field:
                    ir.source = source.name
                    ir.source_url = source.homepage
                    yield PageFindRecord.from_index_record(ir)
        else:
            log.warning(f"No implementation for source type {source.type}! Skipping {source.name}.")

def add_templated_files(config, output_path, files):
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader("awindex"),
        autoescape=select_autoescape()
    )
    for file in files:
        template = env.get_template(file)
        with open(output_path / file, "w") as fh:
            fh.write(template.render(c=config))

def prefix(pre: str, s: str) -> str:
    return pre + s.replace("\n", f"\n{pre}")

async def async_main(config: Settings):
    # Set up paths:
    output_path = Path(config.output)
    index_path = output_path / "pagefind"
    index_path.mkdir(parents=True, exist_ok=True)

    # TODO Process sources here, so we have stats and outputs ready:

    # Put templated index file in place:
    add_templated_files(config, output_path, ["index.html", "styles.css"])

    # Set up index config and generate:
    log.info("Generating PageFind index...")
    index_config = IndexConfig(
        root_selector="main", logfile="index.log", output_path=str(index_path), verbose=True
    )
    async with PagefindIndex(config=index_config) as index:
        # Add custom records:
        count = 0
        for pf in generate_pagefind_records(config):
            await index.add_custom_record(**(dict(pf)))
            count += 1
        # Report (don't call get_files as it returns the actual files and locks up the pipes):
        log.info(f"Indexed {count} records, now writing PageFind index files...")
    log.info("Indexing complete.")

def main(config):
    asyncio.run(async_main(config))


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser(description="Generate Awesome Indexes")
    parser.add_argument(
        '-c', '--config',
        type=str,
        default="config.yaml",
        help="Path to the configuration YAML file."
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help="Path to the output directory for HTML files. Overrides the value in the config file."
    )
    args = parser.parse_args()

    # Run with the config:
    config_file = args.config
    with open(config_file, "r") as file:
        try:
            config = Settings(**yaml.safe_load(file))
            # Add/override output path if specified:
            if args.output:
                config.output = args.output
            # Run:
            log.info(f"Reading config in {config_file}, generating output here: {config.output}")
            main(config)
        except ValidationError as e:
            log.exception("Invalid configuration file", e)