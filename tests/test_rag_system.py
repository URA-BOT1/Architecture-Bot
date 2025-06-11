import importlib
import sys
import types
from dataclasses import dataclass

import pytest

@dataclass
class Document:
    page_content: str
    metadata: dict

class DummySplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=0, separators=None):
        self.chunk_size = chunk_size
    def split_text(self, text):
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

class DummyEmbeddings:
    def __init__(self, *a, **k):
        pass

class DummyRetriever:
    def __init__(self, docs):
        self.docs = docs
    def get_relevant_documents(self, query):
        return self.docs

class DummyChroma:
    def __init__(self, persist_directory=None, embedding_function=None):
        self.docs = []
    def add_documents(self, docs):
        self.docs.extend(docs)
    def persist(self):
        pass
    def as_retriever(self, search_type='similarity', search_kwargs=None):
        return DummyRetriever(self.docs)

class DummyRetrievalQA:
    @classmethod
    def from_chain_type(cls, **kwargs):
        return 'qa_chain'

def import_rag(monkeypatch):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    lc_mod = types.ModuleType('langchain')
    ts_mod = types.ModuleType('langchain.text_splitter')
    ts_mod.RecursiveCharacterTextSplitter = DummySplitter
    emb_mod = types.ModuleType('langchain_community.embeddings')
    emb_mod.HuggingFaceEmbeddings = DummyEmbeddings
    vs_mod = types.ModuleType('langchain_community.vectorstores')
    vs_mod.Chroma = DummyChroma
    schema_mod = types.ModuleType('langchain.schema')
    schema_mod.Document = Document
    chains_mod = types.ModuleType('langchain.chains')
    chains_mod.RetrievalQA = DummyRetrievalQA
    retr_mod = types.ModuleType('langchain.retrievers')
    retr_mod.ContextualCompressionRetriever = object
    dc_mod = types.ModuleType('langchain.retrievers.document_compressors')
    dc_mod.LLMChainFilter = object
    pdf_mod = types.ModuleType('pdfplumber')
    pdf_mod.open = lambda *a, **k: types.SimpleNamespace(__enter__=lambda s:s, __exit__=lambda s,a,b,c: None, pages=[])
    pypdf_mod = types.ModuleType('PyPDF2')
    pypdf_mod.PdfReader = lambda f: types.SimpleNamespace(pages=[])
    monkeypatch.setitem(sys.modules, 'langchain', lc_mod)
    monkeypatch.setitem(sys.modules, 'langchain.text_splitter', ts_mod)
    monkeypatch.setitem(sys.modules, 'langchain_community.embeddings', emb_mod)
    monkeypatch.setitem(sys.modules, 'langchain_community.vectorstores', vs_mod)
    monkeypatch.setitem(sys.modules, 'langchain.schema', schema_mod)
    monkeypatch.setitem(sys.modules, 'langchain.chains', chains_mod)
    monkeypatch.setitem(sys.modules, 'langchain.retrievers', retr_mod)
    monkeypatch.setitem(sys.modules, 'langchain.retrievers.document_compressors', dc_mod)
    monkeypatch.setitem(sys.modules, 'pdfplumber', pdf_mod)
    monkeypatch.setitem(sys.modules, 'PyPDF2', pypdf_mod)
    return importlib.import_module('backend.app.rag')

@pytest.fixture
def rag(tmp_path, monkeypatch):
    rag_module = import_rag(monkeypatch)
    docs_dir = tmp_path / 'docs'
    (docs_dir / 'plu').mkdir(parents=True)
    (docs_dir / 'plu' / 'doc.txt').write_text('urbanisme regles')
    r = rag_module.RAGSystem(str(docs_dir), persist_directory=str(tmp_path/'db'))
    r.initialize()
    return r

def test_index_documents_and_search(rag):
    rag.index_documents()
    assert len(rag.vectorstore.docs) > 0
    docs = rag.search('urbanisme')
    assert len(docs) > 0

def test_get_file_hash(tmp_path, monkeypatch):
    rag_module = import_rag(monkeypatch)
    f = tmp_path / 'f.txt'
    f.write_text('a')
    r = rag_module.RAGSystem(str(tmp_path))
    h1 = r._get_file_hash(f)
    f.write_text('b')
    h2 = r._get_file_hash(f)
    assert h1 != h2
