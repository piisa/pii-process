"""
Test the PiiTextProcessor class
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from pii_data.types.piicollection.loader import PiiCollectionLoader

import pii_process.api.document as mod



DATADIR = Path(__file__).parents[2] / "data" / "doc"


def patch_pii_extract(monkeypatch, piic=None):
    """
    Patch the pii-extract-base API used by process_document
    """
    processor = Mock(return_value=piic)
    processor_cls = Mock(return_value=processor)
    monkeypatch.setattr(mod, "PiiProcessor", processor_cls)

    #collection_mock = Mock(return_value=piic)
    #monkeypatch.setattr(mod, "PiiCollectionBuilder", collection_mock)


# -----------------------------------------------------------------------


def test20_process_document(monkeypatch):
    """
    Test processing a document
    """
    piic = PiiCollectionLoader()
    piic.load_json(DATADIR / "example-pii.json")
    patch_pii_extract(monkeypatch, piic)


    try:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f1:

            n = mod.process_document(DATADIR / "example-src.txt", f1.name,
                                     lang="en",
                                     default_policy="annotate")
            assert n == 2

        with open(f1.name, encoding="utf-8") as f:
            got = f.read()
        print("GOT", got)

        with open(DATADIR / "example-trf.txt", encoding="utf-8") as f:
            exp = f.read()

        assert exp == got

    finally:
        Path(f1.name).unlink()
