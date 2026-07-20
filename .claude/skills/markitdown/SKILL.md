---
name: markitdown
description: Convert PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx/.xls), images (with OCR), audio (with transcription), HTML, CSV/JSON/XML, ZIP archives, EPubs, and YouTube URLs into clean Markdown text using Microsoft's MarkItDown tool. Use this skill whenever the user wants to "convert a document to markdown", "extract text from a PDF/Word/Excel/PowerPoint file", "turn this file into markdown", asks what a document says, needs a document prepared for LLM ingestion/RAG, or hands over a file path/attachment in one of the supported formats and wants its content as text — even if they don't say "markdown" explicitly.
---

# MarkItDown

MarkItDown is a Microsoft open-source Python tool that converts many document formats into
Markdown while preserving structure (headings, tables, lists, links) so the content stays
readable and token-efficient for an LLM.

## When to reach for this skill

Reach for it whenever the task is "get the text/content out of file X" and X is a PDF, Word,
PowerPoint, Excel, image, audio file, HTML page, CSV/JSON/XML, ZIP archive, EPub, or a YouTube
URL. Prefer it over ad-hoc parsing (e.g. hand-rolled PDF text extraction) since it already
handles structure, tables, and format edge cases.

## Setup

Check first whether `markitdown` is importable before doing anything else — installing on every
invocation wastes time:

```bash
python3 -c "import markitdown" 2>/dev/null && echo installed || echo missing
```

If missing, install it. Use the `[all]` extra for full format coverage (PDF, docx, pptx, xlsx,
audio transcription, YouTube transcripts, etc.) unless the environment has a reason to keep the
install narrow (e.g. only ever converting Office files — then `markitdown[docx,pptx,xlsx]` is
lighter):

```bash
pip install 'markitdown[all]'
```

If the sandbox has no network access and installation fails, tell the user rather than falling
back to a hand-written parser that will miss structure MarkItDown would have preserved.

## Converting a file

The bundled `scripts/convert.py` wraps MarkItDown's Python API and is the preferred entry
point — it prints the resulting Markdown to stdout and exits non-zero with a clear message on
failure, which is easier to chain in a pipeline than parsing raw CLI output:

```bash
python3 .claude/skills/markitdown/scripts/convert.py path/to/file.pdf > output.md
```

Equivalent bare CLI form, useful for a one-off conversion the user just wants to eyeball:

```bash
markitdown path/to/file.pdf -o output.md
```

For a URL (including YouTube), pass it the same way — MarkItDown fetches it directly:

```bash
python3 .claude/skills/markitdown/scripts/convert.py "https://example.com/page.html"
```

## Working with the result

- Read the produced Markdown back with the Read tool before summarizing or quoting it — don't
  assume the conversion succeeded just because the command exited 0 for very large files.
- Tables, headings, and lists in the source generally survive as proper Markdown syntax; sanity
  check a sample of the output against the original when precision matters (e.g. financial
  tables), since layout-heavy PDFs can still lose some structure.
- Images are OCR'd for embedded text; if the user also wants a *description* of an image (not
  just literal text), pass an LLM client through the Python API instead of the CLI:

```python
from markitdown import MarkItDown
from openai import OpenAI

client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")
result = md.convert("photo.jpg")
print(result.text_content)
```

  (Swap in whatever LLM client the project already uses — MarkItDown just needs an object
  exposing the client's `chat.completions.create`-style interface.)

## Batch conversion

For multiple files, loop over them rather than writing a bespoke batch tool — `scripts/convert.py`
already handles one file cleanly, so shell out per file:

```bash
for f in docs/*.pdf; do
  python3 .claude/skills/markitdown/scripts/convert.py "$f" > "${f%.pdf}.md"
done
```

## Troubleshooting

- **Missing optional dependency error** (e.g. for a specific format): install the matching
  extra, such as `pip install 'markitdown[pdf]'`, rather than the whole `[all]` bundle if the
  environment should stay minimal.
- **Password-protected or corrupted files**: MarkItDown will raise — surface the error to the
  user instead of silently producing empty output.
- **Audio transcription** requires the `audio-transcription` extra and, depending on backend,
  network access or a local model; check the error message for which is missing.
