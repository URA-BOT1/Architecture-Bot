import importlib
import sys
import types
import pytest


def import_pdf_reader(monkeypatch, page_texts, ocr_texts=None):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    class DummyPage:
        def __init__(self, text):
            self._text = text
        def get_text(self):
            return self._text
    class DummyDoc:
        def __init__(self, texts):
            self.pages = [DummyPage(t) for t in texts]
        def __iter__(self):
            return iter(self.pages)
    fitz_mod = types.ModuleType("fitz")
    fitz_mod.open = lambda path: DummyDoc(page_texts)
    pdf2_mod = types.ModuleType("pdf2image")
    pdf2_mod.convert_from_path = lambda path, dpi=300: [object() for _ in range(len(ocr_texts or []))]
    pytess_mod = types.ModuleType("pytesseract")
    counter = {"i": 0}
    def img_to_str(img, lang="fra"):
        text = (ocr_texts or [])[counter["i"]]
        counter["i"] += 1
        return text
    pytess_mod.image_to_string = img_to_str
    monkeypatch.setitem(sys.modules, "fitz", fitz_mod)
    monkeypatch.setitem(sys.modules, "pdf2image", pdf2_mod)
    monkeypatch.setitem(sys.modules, "pytesseract", pytess_mod)
    # also mock dependencies imported via ingestion.__init__
    docx_mod = types.ModuleType("docx")
    docx_mod.Document = lambda p: None
    pd_mod = types.ModuleType("pandas")
    pd_mod.read_excel = lambda p: types.SimpleNamespace(to_csv=lambda index=False: "")
    monkeypatch.setitem(sys.modules, "docx", docx_mod)
    monkeypatch.setitem(sys.modules, "pandas", pd_mod)
    sys.modules.pop('src.ingestion.pdf_reader', None)
    return importlib.import_module('src.ingestion.pdf_reader')


def import_docx_reader(monkeypatch, paragraphs):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    docx_mod = types.ModuleType("docx")
    class DummyDoc:
        def __init__(self, path):
            self.paragraphs = [types.SimpleNamespace(text=t) for t in paragraphs]
    docx_mod.Document = DummyDoc
    monkeypatch.setitem(sys.modules, "docx", docx_mod)
    sys.modules.pop('src.ingestion.docx_reader', None)
    return importlib.import_module('src.ingestion.docx_reader')


def import_excel_reader(monkeypatch, csv_output):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    pd_mod = types.ModuleType("pandas")
    class DummyDF:
        def to_csv(self, index=False):
            return csv_output
    pd_mod.read_excel = lambda path: DummyDF()
    monkeypatch.setitem(sys.modules, "pandas", pd_mod)
    sys.modules.pop('src.ingestion.excel_reader', None)
    return importlib.import_module('src.ingestion.excel_reader')


def import_embedder(monkeypatch):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    st_mod = types.ModuleType("sentence_transformers")
    class DummyModel:
        def __init__(self, name):
            self.name = name
        def encode(self, texts, show_progress_bar=False):
            return [t.upper() for t in texts]
    st_mod.SentenceTransformer = DummyModel
    monkeypatch.setitem(sys.modules, 'sentence_transformers', st_mod)
    sys.modules.pop('src.embeddings.embedder', None)
    return importlib.import_module('src.embeddings.embedder')


def import_chroma_manager(monkeypatch):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    class DummyCollection:
        def __init__(self):
            self.added = []
        def add(self, ids, documents, embeddings, metadatas):
            for tup in zip(ids, documents, embeddings, metadatas):
                self.added.append(tup)
        def query(self, query_embeddings, n_results=5):
            return {"ids": [[t[0] for t in self.added][:n_results]]}
    class DummyClient:
        def __init__(self, settings):
            self.settings = settings
            self.persist_called = False
        def get_or_create_collection(self, name):
            self.collection = DummyCollection()
            return self.collection
        def persist(self):
            self.persist_called = True
    chroma_mod = types.ModuleType("chromadb")
    chroma_mod.Client = lambda settings: DummyClient(settings)
    config_mod = types.ModuleType("chromadb.config")
    config_mod.Settings = lambda chroma_db_impl, persist_directory: {
        "impl": chroma_db_impl,
        "dir": persist_directory,
    }
    monkeypatch.setitem(sys.modules, "chromadb", chroma_mod)
    monkeypatch.setitem(sys.modules, "chromadb.config", config_mod)
    sys.modules.pop('src.vectorstore.chroma_manager', None)
    return importlib.import_module('src.vectorstore.chroma_manager')


def test_read_pdf_extract(monkeypatch):
    mod = import_pdf_reader(monkeypatch, ["a", "b"])
    assert mod.read_pdf("f.pdf") == "a\nb"


def test_read_pdf_ocr(monkeypatch):
    mod = import_pdf_reader(monkeypatch, ["", ""], ["o1", "o2"])
    assert mod.read_pdf("f.pdf") == "o1\no2"


def test_read_docx(monkeypatch):
    mod = import_docx_reader(monkeypatch, ["p1", "p2"])
    assert mod.read_docx("f.docx") == "p1\np2"


def test_read_excel(monkeypatch):
    mod = import_excel_reader(monkeypatch, "col\n1\n2")
    assert mod.read_excel("f.xlsx") == "col\n1\n2"


def test_embedder(monkeypatch):
    mod = import_embedder(monkeypatch)
    emb = mod.Embedder("model")
    assert emb.model.name == "model"
    assert emb.encode(["x"]) == ["X"]


def test_chroma_manager(monkeypatch):
    mod = import_chroma_manager(monkeypatch)
    cm = mod.ChromaManager("db")
    cm.add(["1"], ["t"], [[0.1]], [{"m":1}])
    assert cm.client.persist_called
    res = cm.search([0.1], k=1)
    assert res["ids"] == [["1"]]
