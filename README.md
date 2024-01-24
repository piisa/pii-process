# pii-process

[![version](https://img.shields.io/pypi/v/pii-process)](https://pypi.org/project/pii-process)
[![changelog](https://img.shields.io/badge/change-log-blue)](CHANGES.md)
[![license](https://img.shields.io/pypi/l/pii-process)](LICENSE)
[![build status](https://github.com/piisa/pii-process/actions/workflows/pii-process-pr.yml/badge.svg)](https://github.com/piisa/pii-process/actions)


Full end-to-end processing for PII (preprocess, extract, decide, transform)

## Description

This package wraps around the relevant API blocks in the full PIISA workflow:
 1. [`pii-preprocess`], to read document formats
 2. [`pii-extract`] (plus any installed pii-extract plugins), to detect and
    extract PII instances from documents
 3. [`pii-decide`], to consolidate the list of PII instances
 4. [`pii-transform`], to substitute detected PII instances in documents
 
It provides both a [Python API] and a [command-line interface]

## Installation

Dependencies have been included in the package so that all necessary PIISA
packages are installed along. So what is needed is just:
 * creation of a Python virtualenv (using Python >= 3.8)
 * and installation of the package in the virtualenv
 
Choices are:

 * **Simple installation**: this will install the package, the packages for the
   four above mentioned PIISA processing steps, and the extraction plugin for PII
    instances using regular expressions:
   
        pip install pii-process

   the dependencies installed automatically are thus `pii-preprocess`,
   `pii-extract-base`, `pii-extract-plg-regex`, `pii-decide` and
   `pii-transform`


 * **Complete installation**: this installs all the above, plus the extraction
   plugin for PII instances using trained [Transformer] models (usually to extract
   PERSON and LOCATION types for some languages):
   
        pip install pii-process[transformers]

   Over the previous installation, this adds also the 
   `pii-extract-plg-transformers` package. Note that **Pytorch needs to be
   installed too** (either GPU or CPU versionss) , so that the models used by
   the `pii-extract-plg-transformers` package can run. See the [transformers
   plugin documentation] for more information,


 * **Alternate installation**: this option performs the first install, and it adds
   the extraction plugin for PII instances using the [Presidio] library (usually
   to extract PERSON and LOCATION types for some languages):
   
        pip install pii-process[presidio]
		
   the additional package installed is in this case 
   `pii-extract-plg-presidio`. And in order to work the relevant models need
   to be downloaded, see the [presidio plugin documentation] for details


It is also possible to install all plugins, i.e. `pip install
pii-process[transformers,presidio]`, though the Transformers and Presidio
plugins overlap in functionality (note that detection overlaps would be resolved
by the `pii-decide` block).

[Transformer]: https://huggingface.co/docs/transformers/main/en/index
[Presidio]: https://microsoft.github.io/presidio/

[Python API]: doc/api.md
[command-line interface]: doc/scripts.md

[`pii-preprocess`]: https://github.com/piisa/pii-preprocess
[`pii-extract`]: https://github.com/piisa/pii-extract-base
[`pii-decide`]: https://github.com/piisa/pii-decide
[`pii-transform`]: https://github.com/piisa/pii-transform
[pii-extract-plg-transformers]: https://github.com/piisa/pii-extract-plg-transformers
[pii-extract-plg-presidio]: https://github.com/piisa/pii-extract-plg-presidio

[transformers plugin documentation]: https://github.com/piisa/pii-extract-plg-transformers
[presidio plugin documentation]: https://github.com/piisa/pii-extract-plg-presidio
