import os
import yaml
import json
import argparse
import logging
from typing import List
from pathlib import Path
from pydantic import ValidationError
from sqlite_utils import Database
import pyarrow as pa
import pyarrow.parquet as pq
from .awelist import parse_awesome_list
from .zotero import parse_zotero
from .zenodo import parse_zenodo
from .models import Settings, IndexRecord, SourceResults
from .pagefind import generate_pagefind_index

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger(__name__)


def generate_index_records(config: Settings) -> List[SourceResults]:
    results = []
    for source in config.sources:
        log.info(f"Indexing {source.name}...")
        result = SourceResults(name=source.name, homepage=source.homepage, description=source.description)
        result.records = []
        if source.type == "awesome-list":
            for ir in parse_awesome_list(source, result):
                result.records.append(ir)
        elif source.type == "zotero":
            for ir in parse_zotero(source, result):
                result.records.append(ir)
        elif source.type == "zenodo":
            for ir in parse_zenodo(source, result):
                result.records.append(ir)
        elif source.type == "jsonl":
            with open(source.file) as f:
                for line in f:
                    ir = IndexRecord.model_validate_json(line)
                    # Override the source field:
                    ir.source = source.name
                    ir.source_url = source.homepage
                    result.records.append(ir)
                    result.num_records += 1
        else:
            log.warning(f"No implementation for source type {source.type}! Skipping {source.name}.")
        log.info(f"Gathered {len(result.records)} records from source {source.name}.")
        results.append(result)

    return results

def collect_index_records(results: List[SourceResults]) -> List[IndexRecord]:
    # Collect:
    records = []
    for source in results:
        records += source.records
    return records

def add_templated_files(config, results, output_path, files):
    from jinja2 import Environment, PackageLoader, select_autoescape
    env = Environment(
        loader=PackageLoader("awindex"),
        autoescape=select_autoescape()
    )
    for file in files:
        template = env.get_template(file)
        with open(output_path / file, "w") as fh:
            fh.write(template.render(c=config, r=results))

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
    parser.add_argument('--jsonl', action=argparse.BooleanOptionalAction)
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
            results = generate_index_records(config)
            records = collect_index_records(results)

            # Set up paths, including directory for the PageFind index:
            output_path = Path(config.output)
            index_path = output_path / "pagefind"
            index_path.mkdir(parents=True, exist_ok=True)

            # Put templated index file in place:
            add_templated_files(config, results, output_path, ["index.html", "styles.css"])

            # Output stats summary of the sources:
            log.info("Generating JSONL summary...")
            with open( output_path / "summary.jsonl", "w" ) as f:
                for result in results:
                    f.write(result.model_dump_json(exclude={'records'}))
                    f.write("\n")

            # Generate raw JSONL output
            if args.jsonl:
                log.info("Generating JSONL export...")
                with open( output_path / "records.jsonl", "w") as f:
                    for ir in records:
                        f.write(ir.model_dump_json())
                        f.write("\n")

            # Generate SQLite DB
            log.info("Generating SQLite export...")
            sql_path = output_path / "records.db"
            db = Database(sql_path, recreate=True)
            for ir in records:
                db["index"].insert(ir.model_dump())
            db["index"].enable_fts(['title', 'abstract', 'full_text', 'creators', 'keywords', 'categories'])

            log.info("Generating Parquet export...")
            plain_records = [item.model_dump() for item in records]
            table = pa.Table.from_pylist(plain_records)
            pq.write_table(table,  output_path / "records.parquet" )

            # Generate the PageFind index file:
            generate_pagefind_index(index_path, records)

        except ValidationError as e:
            log.exception("Invalid configuration file", e)


if __name__ == "__main__":
    main()