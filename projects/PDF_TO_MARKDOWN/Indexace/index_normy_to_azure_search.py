import os
import sys
import markdown
import re
from pathlib import Path

# ✅ Opravené importy pro LangChain 1.x
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings  # Místo SentenceTransformerEmbeddings


from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Optional embeddings
USE_EMBEDDINGS = False
try:
    from openai import AzureOpenAI
    import tiktoken
except Exception:
    AzureOpenAI = None
    tiktoken = None


# -----------------------------
# Config
# -----------------------------
load_dotenv()

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "normy-md-index")
NORMY_ROOT = os.getenv("NORMY_ROOT")

USE_EMBEDDINGS = (os.getenv("USE_EMBEDDINGS", "false").strip().lower() == "true") and AzureOpenAI is not None
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBED_DEPLOYMENT")
AOAI_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
VECTOR_DIMENSIONS = int(os.getenv("VECTOR_DIMENSIONS", "1536"))


# -----------------------------
# Utilities
# -----------------------------
def stable_id(*parts: str) -> str:
    raw = "||".join([p or "" for p in parts]).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def read_json(path: Path) -> Any:
    return json.loads(read_text(path))

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.strip().lower()
    s = "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )
    s = re.sub(r"\s+", " ", s)
    s = s.replace("–", "-").replace("—", "-")
    return s.strip()

def title_key(title: str) -> str:
    t = normalize_text(title)
    t = re.sub(r"^[0-9]+(\.[0-9]+)*\s*", "", t)  # strip "3.1 "
    return t.strip()

def batch(iterable, n=500):
    buf = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= n:
            yield buf
            buf = []
    if buf:
        yield buf


# -----------------------------
# Detect CSN metadata from MD (fallback)
# -----------------------------
def guess_csn_kod(md_text: str) -> Optional[str]:
    m = re.search(r"\bČSN(?:\s+EN|\s+ISO|\s+EN\s+ISO|\s+EN\s+IEC|\s+IEC)?\s+[0-9]{2}\s*[0-9]{3,4}(?:-[0-9]+)?(?:\+[A-Z0-9]+)?\b", md_text)
    return m.group(0).strip() if m else None

def guess_ics(md_text: str) -> Optional[str]:
    m = re.search(r"\bICS\s+([0-9]{2}\.[0-9]{3}\.[0-9]{2})\b", md_text)
    return m.group(1) if m else None

def guess_vydani(md_text: str) -> Optional[str]:
    m = re.search(r"\b(Leden|Únor|Březen|Duben|Květen|Červen|Červenec|Srpen|Září|Říjen|Listopad|Prosinec)\s+([0-9]{4})\b", md_text)
    return f"{m.group(1)} {m.group(2)}" if m else None


# -----------------------------
# Meta.json parsing
# -----------------------------
def extract_toc_items(meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(meta, dict):
        if "table_of_contents" in meta and isinstance(meta["table_of_contents"], list):
            return meta["table_of_contents"]
        for k in ("toc", "headings", "outline"):
            if k in meta and isinstance(meta[k], list):
                return meta[k]
    return []

def build_meta_lookup(toc_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    lookup: Dict[str, List[Dict[str, Any]]] = {}
    for it in toc_items:
        title = str(it.get("title", "")).strip()
        if not title:
            continue
        key = title_key(title)
        lookup.setdefault(key, []).append(it)
    return lookup

def match_meta_item(md_heading: str, meta_lookup: Dict[str, List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
    k = title_key(md_heading)
    if k in meta_lookup:
        return meta_lookup[k][0]
    for key, items in meta_lookup.items():
        if key and (key in k or k in key):
            return items[0]
    return None


# -----------------------------
# Chunking + typing
# -----------------------------
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
ARTICLE_RE = re.compile(r"^([0-9]+(\.[0-9]+)*)\b")  # "3.1"
APPENDIX_RE = re.compile(r"^priloha\s+([a-z0-9]+)\b", re.I)
NORMATIVE_HINT_RE = re.compile(r"\(normativni\)|\bnormativni\b", re.I)
INFORMATIVE_HINT_RE = re.compile(r"\(informativni\)|\binformativni\b", re.I)

def split_md_by_headings(md_text: str) -> List[Tuple[str, str]]:
    lines = md_text.splitlines()
    out: List[Tuple[str, str]] = []
    cur_title = "ROOT"
    buf: List[str] = []
    for line in lines:
        m = HEADING_RE.match(line.strip())
        if m:
            if buf:
                out.append((cur_title, "\n".join(buf).strip()))
            cur_title = m.group(2).strip()
            buf = [line]
        else:
            buf.append(line)
    if buf:
        out.append((cur_title, "\n".join(buf).strip()))
    return out

def classify_section(title: str) -> Tuple[str, bool, Optional[str]]:
    raw = title.strip()
    norm = normalize_text(raw)

    if APPENDIX_RE.search(norm) or norm.startswith("priloha"):
        if NORMATIVE_HINT_RE.search(norm):
            return ("priloha_normativni", True, None)
        if INFORMATIVE_HINT_RE.search(norm):
            return ("priloha_informativni", False, None)
        return ("priloha_neurcena", True, None)

    am = ARTICLE_RE.match(raw)
    if am:
        return ("clanek", True, am.group(1))

    if "terminy a definice" in norm:
        return ("sekce_definice", True, None)
    if "citovane normativni dokumenty" in norm:
        return ("sekce_citace", True, None)
    if "predmet normy" in norm:
        return ("sekce_predmet", True, None)
    if "predmluva" in norm:
        return ("sekce_predmluva", False, None)
    if norm.startswith("obsah"):
        return ("sekce_obsah", False, None)

    return ("unknown", True, None)

def token_chunk(text: str, max_tokens: int = 700, overlap: int = 80) -> List[str]:
    if tiktoken is None:
        step = 3000
        return [text[i:i+step] for i in range(0, len(text), step)]
    enc = tiktoken.get_encoding("cl100k_base")
    toks = enc.encode(text)
    out = []
    i = 0
    while i < len(toks):
        j = min(i + max_tokens, len(toks))
        out.append(enc.decode(toks[i:j]))
        i = j - overlap
        if i < 0:
            i = 0
        if j == len(toks):
            break
    return out

def normalize_chunk(anchor: str, chunk_text: str) -> List[Tuple[str, str]]:
    if len(chunk_text) < 6000:
        return [(anchor, chunk_text)]
    sub = token_chunk(chunk_text)
    return [(f"{anchor}#{k+1}", s) for k, s in enumerate(sub)]


# -----------------------------
# Embeddings
# -----------------------------
def get_embedder():
    if not USE_EMBEDDINGS:
        return None
    if not (AOAI_ENDPOINT and AOAI_KEY and AOAI_DEPLOYMENT):
        return None
    return AzureOpenAI(
        azure_endpoint=AOAI_ENDPOINT,
        api_key=AOAI_KEY,
        api_version=AOAI_VERSION
    )

def embed_text(client: AzureOpenAI, text: str) -> List[float]:
    clean = re.sub(r"\s+", " ", text).strip()
    resp = client.embeddings.create(model=AOAI_DEPLOYMENT, input=clean)
    vec = resp.data[0].embedding
    if len(vec) != VECTOR_DIMENSIONS:
        raise ValueError(f"Embedding dimensions {len(vec)} != expected {VECTOR_DIMENSIONS}")
    return vec


# -----------------------------
# Build documents for Azure AI Search
# -----------------------------
def build_documents(md_path: Path) -> List[Dict[str, Any]]:
    md_text = read_text(md_path)

    meta_path = md_path.with_name(md_path.stem + "_meta.json")
    meta = read_json(meta_path) if meta_path.exists() else {}
    toc_items = extract_toc_items(meta) if isinstance(meta, dict) else []
    meta_lookup = build_meta_lookup(toc_items)

    csn_kod = guess_csn_kod(md_text) or str(meta.get("csnKod", "")).strip() or ""
    ics = guess_ics(md_text) or str(meta.get("ics", "")).strip() or ""
    vydani = guess_vydani(md_text) or str(meta.get("vydani", "")).strip() or ""

    sections = split_md_by_headings(md_text)

    docs = []
    chunk_order = 0

    for heading, section_text in sections:
        chunk_order += 1

        typCasti, jeNormativni, cast_number = classify_section(heading)
        meta_item = match_meta_item(heading, meta_lookup)

        page_id = meta_item.get("page_id") if isinstance(meta_item, dict) else None
        heading_level = meta_item.get("heading_level") if isinstance(meta_item, dict) else None
        meta_title = meta_item.get("title") if isinstance(meta_item, dict) else None

        cast_val = cast_number or heading.strip()
        nazevCasti = heading.strip()

        for cast2, text2 in normalize_chunk(cast_val, section_text):
            doc_id = stable_id(str(md_path), cast2, str(chunk_order))
            docs.append({
                "id": doc_id,
                "content": text2,

                "csnKod": csn_kod,
                "csnNazev": str(meta.get("csnNazev", "")).strip(),
                "ics": ics,
                "vydani": vydani,
                "typDokumentu": "norma_md",

                "cast": cast2,
                "nazevCasti": nazevCasti,
                "typCasti": typCasti,
                "jeNormativni": bool(jeNormativni),

                "nahrazuje": str(meta.get("nahrazuje", "")).strip(),

                "zdrojSoubor": md_path.name,
                "zdrojCesta": str(md_path),

                "chunkId": f"{md_path.stem}::{cast2}",
                "chunkOrder": int(chunk_order),

                # extra diagnostic metadata (optional)
                "meta_pageId": page_id if page_id is not None else -1,
                "meta_headingLevel": heading_level if heading_level is not None else -1,
                "meta_title": meta_title or ""
            })

    return docs


# -----------------------------
# Upload
# -----------------------------
def upload_docs(search_client: SearchClient, docs: List[Dict[str, Any]]):
    for b in batch(docs, n=500):
        result = search_client.upload_documents(documents=b)
        failed = [r for r in result if not r.succeeded]
        if failed:
            print(f"[UPLOAD] Failed: {len(failed)} (showing up to 5)")
            for f in failed[:5]:
                print("  -", f.key, f.error_message)
        else:
            print(f"[UPLOAD] OK: {len(b)}")
        time.sleep(0.1)

def main():
    if not (SEARCH_ENDPOINT and SEARCH_KEY and INDEX_NAME and NORMY_ROOT):
        raise RuntimeError("Missing env vars: AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_ADMIN_KEY, AZURE_SEARCH_INDEX_NAME, NORMY_ROOT")

    root = Path(NORMY_ROOT)
    if not root.exists():
        raise RuntimeError(f"NORMY_ROOT not found: {root}")

    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=AzureKeyCredential(SEARCH_KEY)
    )

    embedder = get_embedder()
    if USE_EMBEDDINGS and embedder is None:
        print("[INFO] USE_EMBEDDINGS=true but Azure OpenAI config missing -> ingest without vectors.")
    if not USE_EMBEDDINGS:
        print("[INFO] Ingest without vectors (fulltext only).")

    md_files = sorted(root.rglob("*.md"))
    print(f"[INFO] Found {len(md_files)} md files under {root}")

    total_docs = 0
    buffer_docs: List[Dict[str, Any]] = []

    for md_path in md_files:
        # ignoruj pomocné prompty apod. (uprav dle potřeby)
        if md_path.name.lower().startswith("prompt_"):
            continue

        docs = build_documents(md_path)

        if embedder is not None:
            for d in docs:
                d["contentVector"] = embed_text(embedder, d["content"])

        buffer_docs.extend(docs)
        total_docs += len(docs)

        if len(buffer_docs) >= 5000:
            upload_docs(search_client, buffer_docs)
            buffer_docs = []

    if buffer_docs:
        upload_docs(search_client, buffer_docs)

    print(f"[DONE] Uploaded documents: {total_docs}")


if __name__ == "__main__":
    main()
