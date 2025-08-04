Awesome Indexer
===============

Generates Awesome Indexes - tiny search engines build from curated sources:

- [Awesome Lists](https://github.com/sindresorhus/awesome/blob/main/awesome.md) (hence the name _Awesome Indexes!_)
- [Zotero](https://www.zotero.org/) libraries and collections
- [Zenodo Communities](https://zenodo.org/communities)
- Any other source that can be used to create suitable JSON objects formatted as [JSONL](https://jsonlines.org/) files.

The `awindex` tool gathers links and metadata from these sources, and uses them to build a static web page that provides a [Pagefind](https://pagefind.app/) faceted search interface. It can also package the index data as a downloadable database, to allow deeper analysis or custom visualisations to be created.

You can see a demonstration [here](https://anjackson.net/blog/awindex-test-1/).

## Usage

### Local installation

To install `awindex` locally, you need Python 3.11 or later.

```sh
pip install git+https://github.com/digipres/awesome-indexer@main
awindex -c config -o ./index
```
After which, you will be able to run the `awindex` command.

Or, if [uv](https://docs.astral.sh/uv/) is installed, the `awindex` tool can be run directly using:

```sh
uvx --from git+https://github.com/digipres/awesome-indexer@main awindex -c config.yaml -o ./index
```

### Building an Awesome Index

By default, the `awindex` command reads it's configuration from a file called `./config.yaml` (this can overridden at the command line, run `awindex -h` for help).

The tool reads the `config.yaml` file, downloads and caches the information sources, and generates an Awesome Index in the `./index` folder.

### Configuration

There are a set of fields that provide some basic information about the site, and then a list of sources to read in order to build the index. For example:

```yaml
title: "My Awesome Index Title"
homepage: https://my.website/page-about-this-index
description: "A brief description about this index and what's in it."
sources:
- name: "Awesome Digital Preservation"
  homepage: "https://github.com/digipres/awesome-digital-preservation/"
  type: awesome-list
  url: "https://raw.githubusercontent.com/digipres/awesome-digital-preservation/refs/heads/main/README.md"
```

An example [`config.yaml`](./config.yaml) is provided that shows how it works in more detail.

Each `type` of source should have a `name` and a `homepage` so people can find out more about the source that has been included in the index. Each source can also have a `description`, to be shown in the Awesome Index source summary.

The additional parameters for each source are...

#### Source: Awesome Lists

- __`type: awesome-list`__ (required)
- __`url`__: A URL to download the Markdown source content of the Awesome List. (required)
- __`view_url`__: A URL pointing to a web version of the source content that allows linking and highlighting of lines using a `#L10` fragment on the end of the URL.

#### Source: Zotero Collection

Note that `awindex` only supports public Zotero collections at present.

- __`type: zotero`__ (required)
- __`library_type`__: Either `user` or `group` (required).
- __`library_id`__: The identification number for this library, e.g. `8195999` (required).
- __`collection_id`__: The key of a specific collection within this library, e.g. `ERZIYJ3T` (optional). If this is specified, the index will only include records that are included in that hierarchy of collections.

The [pyzotero documentation](https://pyzotero.readthedocs.io/en/latest/#getting-started-short-version) has more information about these fields and how to find them.

#### Source: Zenodo Community

- __`type: zenodo`__ (required)
- __`community`__: The unique identifier for this community, e.g. `digital-preservation` (required).

#### Source: JSONL File

- __`type: jsonl`__ (required)
- __`file`__: A local file path for a set of records in JSONL format, e.g. `./test/ipres-awindex-test.jsonl` (required).


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
pip install -e .
```

Having installed in development mode (`pip install -e`), to run from source:

```bash
python -m awindex.cli
```

### Adding a new source

_TBA: JSONL or extend thusly_