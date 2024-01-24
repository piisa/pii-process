# Provided APIs

This package provides three different Python APIs for end-to-end processing.
For them to work the `pii-preprocess`, `pii-extract-base`, `pii-decide`
& `pii-transform` packages need to be installed (along with any required
detector task plugins); this is done automatically upon package installation.


## Document process API

This is an end-to-end process:
 - load a document, in the formats supported by `pii-preprocess` (text, Word,
   CSV)
 - detect PII instances (using all installed pii-extract plugins)
 - consolidate the detected instances
 - transform the detected instances in the original document
 - write an output document with the transformed instances

The API is provided by the `process_document` function. In its simplest form
it just needs the name of the input file and the output file:

```Python
from pii_process.api import process_document

process_document(inputname, outputname)
```

The function accepts many additional arguments to modify the default
behaviour, see [its implementation] for a full list.


The `pii-process-doc` command-line script performs the same processing.


## Process API for text buffers

This is similar to the previous one in that it processes end to end, but it
works with raw text buffers:

```Python
from pii_process.api import PiiTextProcessor

# Create the object, defining the language to use and the policy
# Further customization is possible by providing a config
proc = PiiTextProcessor(lang="en", default_policy="label")

# Process a text buffer and get the transformed buffer
outbuf = proc(inbuf)
```

This is a [thin wrapper] over the relevant objects in the PIISA libraries.
The procedure to use it is:
 1. Initialize a `PiiTextProcessor` object, giving as arguments the language
    the text will be in and a default [policy] to apply to transform the
	PII instances found (note that the default config might define other
	policies for specific PII types).
 2. Call the object with a text buffer. It will detect PII instances in it
    and apply the transformation, and will return the transformed text buffer.

Additional process customization is possible by adding a `config` argument to
the constructor. This will contain a PIISA [configuration], or a list of them,
that will be used to modify the behaviour of one or more elements in the
chain. Argument values can be:
 * filenames holding a configuration (in JSON format)
 * in-memory configurations, as a Python dictionary

The constructor contains also additional arguments to e.g. select a subset of
detection tasks to apply.

Note that all text buffers processed with this object must contain _the same_
language (the one indicated in the constructor). For multilingual processing
it is possible to create different objects, one for each desired language, but
it would be more practical to use the multilingual object described in the
next section.


## Multilingual process API for text buffers

This is a small variant over the previous API, which provides the
`MultiPiiTextProcessor` object. This one accepts a _list of languages_ in its
constructor; it then initializes a processor for each of them, and at processing
time allows to choose the language to use for each text buffer (but only from
among the ones that were initialized in the constructor). So it can be used to
process a list of text buffers that are _in different_ languages.


```Python
from pii_process.api import MultiPiiTextProcessor

# Create the object, defining the languages to use and the default policy
# Further customization is possible by providing a config
proc = MultiPiiTextProcessor(lang=["en", "es"], default_policy="label")

# Process a text buffer and get the transformed buffer
outbuf1 = proc(inbuf1, lang="en")
outbuf2 = proc(inbuf2, lang="es")

# Get some statistics on the detected PII
stats = proc.stats()
```

Note that each execution is monolingual, i.e. each text buffer should be in a
_single_ language.

In adition to the default method, which takes a raw text buffer, the object also
contains a `process()` method that takes a [`DocumentChunk`] object.

This API is the one used by the [`pii-process-jsonl`] script


[its implementation]: ../src/pii_process/api/document.py
[thin wrapper]: ../src/pii_process/api/chunk.py
[policy]: https://github.com/piisa/pii-transform/tree/main/doc/policies.md
[configuration]: https://github.com/piisa/piisa/tree/main/docs/configuration.md
[`DocumentChunk`]: https://github.com/piisa/pii-data/blob/main/doc/chunks.md
[`pii-process-jsonl`]: jsonl.md
