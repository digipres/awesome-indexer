import os
import yaml
import argparse
import logging
from pathlib import Path
from pydantic import ValidationError
from .awelist import parse_awesome_list
from .zotero import parse_zotero
from .zenodo import parse_zenodo
from .models import Settings, IndexRecord
from .pagefind import generate_pagefind_index

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)


def generate_index_records(config: Settings):
    # Add custom records:
    for source in config.sources:
        log.info(f"Indexing {source.name}...")
        if source.type == "awesome-list":
            for ir in parse_awesome_list(source):
                yield ir
        elif source.type == "zotero":
            for ir in parse_zotero(source):
                yield ir
        elif source.type == "zenodo":
            for ir in parse_zenodo(source):
                yield ir
        elif source.type == "jsonl":
            with open(source.file) as f:
                for line in f:
                    ir = IndexRecord.model_validate_json(line)
                    # Override the source field:
                    ir.source = source.name
                    ir.source_url = source.homepage
                    yield ir
        else:
            log.warning(f"No implementation for source type {source.type}! Skipping {source.name}.")

def collect_index_records(config: Settings):
    records = []
    for ir in generate_index_records(config):
        records.append(ir)
    return records

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

def main():
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

            # Collect the source records
            log.info(f"Reading config in {config_file}, generating output here: {config.output}")
            records = collect_index_records(config)

            # Set up paths:
            output_path = Path(config.output)
            index_path = output_path / "pagefind"
            index_path.mkdir(parents=True, exist_ok=True)

            # Put templated index file in place:
            add_templated_files(config, output_path, ["index.html", "styles.css"])

            # TODO Process sources here, so we have stats and outputs ready:

            # Generate the PageFind index file:
            generate_pagefind_index(index_path, records)

        except ValidationError as e:
            log.exception("Invalid configuration file", e)


if __name__ == "__main__":
    main()