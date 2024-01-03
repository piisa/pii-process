# Command-line scripts

The package provides two full end-to-end console scripts:

 * `pii-process-doc` is a full end-to-end script for single documents:
    - loads a document, from among the formats supported by `pii-preprocess`
	- detects PII instances, according to `pii-extract` and its installed
	  plugins
    - transforms the detected PII instances (according to the indicated policy)
	  and writes out the transformed document
 
 * [`pii-process-jsonl`] is also a full end-to-end script; this one reads
   [JSONL] files and processes each line as a separate text document (possibly in
   different languages), producing a transformed JSONL document
	  

The processing carried by both scripts can be customized, apart from command-line
options, by supplying [configuration files] that change the behavior of specific
PIISA blocks.

[`pii-process-jsonl`]: jsonl.md
[JSONL]: https://jsonlines.org
[configuration files]: https://github.com/piisa/piisa/tree/main/docs/configuration.md
