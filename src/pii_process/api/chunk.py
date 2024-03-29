"""
Processor for raw text buffers.
All buffers must be in the same language.
"""

from typing import List, Tuple, Dict

from pii_data.helper.config import TYPE_CONFIG_LIST, load_config
from pii_data.types import PiiCollection
from pii_data.types.doc import DocumentChunk
from pii_extract.api.processor import PiiProcessor, PiiCollectionBuilder
from pii_extract.gather.collection import TYPE_TASKENUM
from pii_decide.api import PiiDecider
from pii_transform.api import PiiTransformer


class PiiTextProcessor:
    """
    A simple class that performs end2end PII processing on a raw text buffer,
    or on a single DocumentChunk
    """

    def __init__(self, *, lang: str = "en", default_policy: str = None,
                 config: TYPE_CONFIG_LIST = None, country: List[str] = None,
                 tasks: TYPE_TASKENUM = None, decide: bool = True,
                 debug: bool = False):
        """
         :param lang: language that all text buffers will be in
         :param default_policy: default transformation policy to use
         :param config: configuration(s) to load, in addition to the defaults
         :param country: country(es) to restrict task for
         :param tasks: restrict to an specific set of detection tasks
         :param decide: perform PII decision
         :param debug: activate debug output
        """
        self._cid = 0
        self.config = load_config(config or [])
        self.lang = lang
        self.policy = default_policy
        self.det = PiiProcessor(config=self.config, languages=lang, debug=debug)
        self.det.build_tasks(lang=lang, country=country, pii=tasks)
        self.dec = PiiDecider(config=config, debug=debug) if decide else None
        self.trf = PiiTransformer(default_policy=default_policy,
                                  config=self.config, debug=debug)


    def __repr__(self) -> str:
        return f"<PiiTextProcessor [{self.policy}]>"


    def process(self, chunk: DocumentChunk) -> Tuple[DocumentChunk, PiiCollection]:
        """
        Process a document chunk: detect PII and transform the PII instances
        found in the chunk, according to the defined policy
          :return: a tuple (output-chunk, collection-of-detected-pii)
        """
        piic = PiiCollectionBuilder(lang=self.lang)
        # Detect
        self.det.detect_chunk(chunk, piic)
        # Decide
        if self.dec:
            piic = self.dec.decide_chunk(piic, chunk)
        # Transform
        chunk = self.trf.transform_chunk(chunk, piic)
        return chunk, piic


    def __call__(self, text: str) -> str:
        """
        Process a raw text buffer: detect PII and transform the PII instances
        found, according to the defined policy
          :return: the transformed text buffer
        """
        self._cid += 1
        input_chunk = DocumentChunk(id=self._cid, data=text,
                                    context={"lang": self.lang})
        output_chunk, _ = self.process(input_chunk)
        return output_chunk.data


    def stats(self) -> Dict:
        """
        Returns statistics on the detected PII instances
        """
        return self._proc.get_stats()
