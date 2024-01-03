"""
PII end-to-end processing for JSONL files.
We asssume each line in the file is a single-chunk document.
Each document can be in a different language.
"""

import argparse
import sys
import json

from typing import List, Dict, Iterable

from pii_data.helper.exception import InvalidDocument
from pii_data.helper.io import openfile, base_extension, load_yaml
from pii_data.types.doc import DocumentChunk
from pii_extract.api.file import piic_format
from pii_transform.helper.substitution import POLICIES
from pii_transform.helper.misc import get_element, set_element

from ..api import MultiPiiTextProcessor
from .. import VERSION


def read_jsonl(name: str, verbose: bool = False) -> Iterable[Dict]:
    """
    Read a JSONL file and return it line by line
    """
    with openfile(name, encoding="utf-8") as fin:
        for n, line in enumerate(fin, start=1):

            if verbose:
                print(f"# Document: {n}")
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise InvalidDocument("Error while reading '{}', line {}: {}",
                                      name, n, e) from e


def read_yaml(name: str, verbose: bool = False) -> Iterable[Dict]:
    """
    Read a YAML file assumed to contain a list of dicts, and return it
    item by item
    """
    for n, doc in enumerate(load_yaml(name), start=1):
        if verbose:
            print(f"# Document: {n}")
            yield doc


def process(args: argparse.Namespace):

    #logging.basicConfig(level="INFO")

    if args.verbose:
        print("# Initializing processor for:", ",".join(args.lang))
    proc = MultiPiiTextProcessor(lang=args.lang, config=args.config,
                                 keep_piic=bool(args.save_pii),
                                 default_policy=args.default_policy,
                                 decide=not args.skip_decision,
                                 verbose=args.verbose, show_tasks=args.show_tasks)

    if args.verbose:
        print("# Reading data from:", args.infile)
        print("# Writing data to:", args.outfile)

    # Determine the function to open the source file
    src_func = read_yaml if base_extension(args.infile) in (".yml", ".yaml") else read_jsonl
    src = src_func(args.infile, verbose=args.verbose)

    # Open source file
    with openfile(args.outfile, "w", encoding="utf-8") as fout:

        # Read each document and process it
        for n, doc in enumerate(src, start=1):

            # Find the document language
            doc_lang = get_element(doc, args.field_lang)
            if doc_lang and doc_lang not in args.lang and args.raise_invalid_lang:
                raise InvalidDocument("unavailable language '{}' found in document {}", doc_lang, n)

            # Determine language to use
            lang = doc_lang or args.lang
            if isinstance(lang, list) and len(lang) == 1:
                lang = lang[0]

            # Process
            if not lang or not isinstance(lang, str):
                # We cannot process this document, either raise or copy verbatim
                if args.raise_invalid_lang:
                    raise InvalidDocument("no language specified in document {}", n)
            else:
                # Fetch the text
                text_in = get_element(doc, args.field_text)
                if text_in is None:
                    raise InvalidDocument("no text field {} for document {}",
                                          args.field_text, n)

                # Create a DocumentChunk
                docid = get_element(doc, "id") or str(n)
                ctx = {"lang": lang, "document": {"id": docid}}
                chunk = DocumentChunk("1", text_in, ctx)

                # Process it
                chunk, _ = proc.process(chunk)
                # Substitute the text in the output
                set_element(doc, args.field_text, chunk.data)

            # Save transformed document
            json.dump(doc, fout, indent=None, ensure_ascii=False)
            print(file=fout)

    # Output statistics
    if args.verbose or args.save_stats:
        stats = proc.stats()
        if args.verbose:
            print("\n# Statistics:")
            json.dump(stats, sys.stdout, indent=2)
        if args.save_stats:
            with open(args.save_stats, "w") as f:
                json.dump(stats, f, indent=2)

    # Output the collection of PII instances
    if args.save_pii:
        if args.verbose:
            print("\n# Dumping detected PII to:", args.save_pii)
        fmt = piic_format(args.save_pii, default="json")
        with openfile(args.save_pii, "w", encoding="utf-8") as f:
            proc.piic().dump(f, format=fmt)


# --------------------------------------------------------------------------


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Preprocess, detect & transform PII on JSONL documents (version {VERSION})")

    g0 = parser.add_argument_group("Input/output paths")
    g0.add_argument("infile", help="JSONL source file")
    g0.add_argument("outfile", help="JSONL destination file")
    g0.add_argument("--save-pii", "--out-piic", metavar="OUTFILE",
                    help="output all detected PII instances")
    g0.add_argument("--save-stats", metavar="OUTFILE",
                    help="output statistics to a JSON file")

    g1 = parser.add_argument_group("Language & data specification")
    g1.add_argument("--lang", nargs='+', default=["en"],
                    help="processing languages (default: %(default)s)")
    g1.add_argument("--field-lang", nargs="+", default=("lang", "language"),
                    help="document field defining the language (default: %(default)s)")
    g1.add_argument("--field-text", default=("text",), nargs="+",
                    help="document field containing the text data (default: %(default)s)")


    g1 = parser.add_argument_group("Process configurations")
    g1.add_argument("--config", nargs="+",
                    help="configuration file(s) to load")
    g1.add_argument("--default-policy", choices=POLICIES,
                    help="Default transformation policy")
    g1.add_argument("--skip-decision", action="store_true",
                    help="Skip the decision step")

    g1 = parser.add_argument_group("Options")
    g1.add_argument("--verbose", "-v", type=int, default=1,
                    help="Print progress messages (0-2, default: %(default)d)")
    g1.add_argument("--show-tasks", action='store_true',
                    help="Print out the list of built tasks")
    g1.add_argument("--raise-invalid-lang", action='store_true',
                    help="Raise an exception on problems with the document language")
    g1.add_argument("--reraise", action='store_true',
                    help="Re-raise on exceptions")

    return parser.parse_args(args)



def main(args: List[str] = None):
    if args is None:
        args = sys.argv[1:]
    args = parse_args(args)
    try:
        process(args)
    except Exception as e:
        if args.reraise:
            raise
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
