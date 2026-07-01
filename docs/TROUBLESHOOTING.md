# Troubleshooting

Run `python3 check_setup.py` first — it catches most of the issues below
automatically, with a fix suggestion for each one. This doc goes into more
detail for when that's not enough.

## `ModuleNotFoundError: No module named 'flask'` (or `dotenv`, `anthropic`, etc.)

Your virtual environment either doesn't exist yet, or exists but isn't
activated in the terminal you're using.

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Note that `source .venv/bin/activate` only affects your *current* terminal
session/tab. If you open a new terminal tab, you need to activate it
again there too — this trips people up constantly. Your prompt should
show `(.venv)` at the start when it's active.

## `python: command not found`

Some systems only have `python3`, not a plain `python` alias. Always use
`python3 app.py`, `python3 -m venv .venv`, etc. in this project.

## `Address already in use` / port 5000 conflicts

Something else is already listening on port 5000. On macOS, this is very
often the **AirPlay Receiver** (System Settings → General → AirDrop &
Handoff → turn off "AirPlay Receiver"). Otherwise, find and stop whatever
else is using the port, or edit the last line of `app.py` to use a
different port (e.g. `app.run(debug=True, port=5050)`).

## "Could not reach the server. Is app.py running?" in the browser

This message means the browser's request to the backend failed
completely — not a RAG error, a network-level one. Check, in order:
1. Is `python3 app.py` actually still running in a terminal? (Did it crash, or did you close that tab?)
2. Is a *different* process already bound to port 5000 (see above), so your intended server never actually started?
3. Did the server crash mid-request? Check the terminal running `app.py` for a Python traceback.

## `anthropic.AuthenticationError: 401 invalid x-api-key`

Your `.env` has a key, but Anthropic is rejecting it. Check:
- You replaced `your-api-key-here` in `.env` with a real key, not left the placeholder.
- The key starts with `sk-ant-`.
- No extra quotes, spaces, or a trailing newline got pasted in around the key.
- The key is still active (not revoked/expired) at [console.anthropic.com](https://console.anthropic.com).

Run `python3 check_setup.py --live` to test the key with one real, cheap
API call and get a definitive yes/no answer.

## The language toggle (EN/ID) doesn't do anything when clicked

If you've pulled recent changes to this repo, hard-refresh your browser
to clear the cached JS/CSS: **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R**
(Windows/Linux). Browsers aggressively cache static files, so an old
`app.js` can keep running even after the file on disk has changed.

## `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`

This means the installed `anthropic` package version is incompatible with
the installed `httpx` version (a newer `httpx` removed the `proxies`
argument that older `anthropic` versions still pass). This repo's
`requirements.txt` already pins compatible versions — if you see this,
your installed packages have drifted from what's pinned:

```bash
pip install -r requirements.txt --upgrade
```

## Everything seems installed, but the first request takes a long time

The first time `embed_texts()` runs, it downloads the `all-MiniLM-L6-v2`
embedding model (~80MB) and caches it locally. This only happens once —
subsequent runs are fast. If you're demoing live in class, consider
running one query *before* class starts so the model is already cached.

## I get a valid answer, but it seems to ignore my documents

Check the **Embedding Space & Retrieval** panel (stage 2) — if the
low-confidence banner is showing, retrieval didn't find a good match for
your question in the corpus. This is usually not a bug: either your
question isn't actually answerable from the sample docs, or (if you added
your own document) it didn't get chunked/indexed the way you expected.
Try lowering Top-K or rebuilding the index with a different chunk size
(see `docs/LAB_WORKSHEET.md` exercise 4).

## Still stuck?

Open an issue with:
- The exact command you ran and its full output/traceback.
- Output of `python3 check_setup.py`.
- Your OS and Python version (`python3 --version`).
