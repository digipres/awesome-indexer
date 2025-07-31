Awesome Indexer
===============

Generates Awesome Indexes - tiny search engines build from curated sources:

- [Awesome Lists](https://github.com/sindresorhus/awesome/blob/main/awesome.md) (hence the name _Awesome Indexes!_)
- [Zotero](https://www.zotero.org/) libraries and collections
- [Zenodo Communities](https://zenodo.org/communities)
- Read as JSON objects via [JSONL](https://jsonlines.org/) files generated from other sources.

You can see a demonstration of the idea at _TBA_

## Usage

### Local installation

To install `awindex` locally, you need Python 3.11 or later.

```sh
pip install _TBA_
```
After which, you will be able to run the `awindex` command.

Or, if [uv](https://docs.astral.sh/uv/) is installed:

```sh
uvx _TBA_
```

### Building an Awesome Index

By default, the `awindex` command reads it's configuration from a file called `./config.yaml` (this can overridden at the command line, run `awindex -h` for help).

The tool reads the `config.yaml` file, downloads and caches the information sources, and generates an Awesome Index in the `./output` folder.

You can the open [`./output/index.html`](./output/index.html) in a browser to see the results

### Configuration

An example [`config.yaml`](./config.yaml) is provided that shows how it works. There are a set of fields that provide some basic information about the site, and then a list of sources to read in order to build the index.

_TBA_

### Running in a GitHub Action

_TBA_

## Development setup

### Linux/WSL2

```bash
sudo apt install python3.11
sudo apt install python3.11-venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install .
```

And to run from source rather than the installed version (i.e. during development):

```bash
python -m awindex.cli
```