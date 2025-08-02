Awesome Indexer
===============

Generates Awesome Indexes - tiny search engines build from curated sources:

- [Awesome Lists](https://github.com/sindresorhus/awesome/blob/main/awesome.md) (hence the name _Awesome Indexes!_)
- [Zotero](https://www.zotero.org/) libraries and collections
- [Zenodo Communities](https://zenodo.org/communities)
- Any other source that can be used to create suitable JSON objects formatted as [JSONL](https://jsonlines.org/) files.

The `awindex` tool gathers links and metadata from these sources, and uses them to build a static web page that provides a [Pagefind](https://pagefind.app/) faceted search interface. It can also package the index data as a downloadable database, to allow deeper analysis or custom visualisations to be created.

You can see a demonstration at _TBA_

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

The tool reads the `config.yaml` file, downloads and caches the information sources, and generates an Awesome Index in the `./index` folder.

### Configuration

An example [`config.yaml`](./config.yaml) is provided that shows how it works. There are a set of fields that provide some basic information about the site, and then a list of sources to read in order to build the index.

_TBA_

### Using an Awesome Index

Unfortunately, the index itself won't work without a web server.  If you've got Python 3+ installed, you can run:

```sh
cd index
python -m http.server 8080
```

and then the index will be accessible at <http://localhost:8080>. Alternatively, you can upload your files to a static web host like [GitHub Pages](https://pages.github.com/), [Netlify](https://www.netlify.com/) (e.g. using [Netlify Drop](https://app.netlify.com/drop)) or [these EU alternatives](https://european-alternatives.eu/category/jamstack-hosting).

### As a GitHub Action

_TBA_

## Development setup

As well as needing Python 3.11+, the development environment needs NodeJS installed (because Pagefind is written in JavaScript).

The [search page template](./awindex/templates/index.html) uses the [Jinja2](https://jinja.palletsprojects.com/) templating library and the interface is built using [Bootstrap (v5)](https://getbootstrap.com/).

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

### Adding a new source

_TBA: JSONL or extend thusly_