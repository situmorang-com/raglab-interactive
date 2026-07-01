# Lab Worksheet: Understanding RAG by Breaking It

A set of short, in-class exercises that use the interactive controls in the
app. The goal of each one is to make a prediction *before* clicking, then
compare it to what actually happens — that's where the understanding comes
from, not from watching a correct answer appear.

Suggested order: do these roughly in sequence, in pairs or individually,
10-20 minutes total depending on discussion time.

## 1. Predict, then reveal (Retrieval)

Before asking a question, write down which sample document you *think*
will be retrieved. Then ask it and check the **Embedding Space &
Retrieval** panel.

- Ask: *"How many vacation days do I get?"* — predict the source file, then check.
- Ask something that could plausibly match two documents (e.g. *"What expenses get reimbursed?"* could touch both `expense_reimbursement.txt` and `remote_work.txt`'s equipment stipend). Which one wins? Why?

**Discussion**: retrieval ranks by *semantic similarity*, not keyword overlap. Find a question where the "obviously right" document does *not* win.

## 2. Break retrieval on purpose

Ask a question that has **nothing to do with any of the 5 sample docs**
(e.g. *"What's the weather like today?"* or *"Explain quantum computing"*).

- Watch the low-confidence banner. What score did the top chunk get?
- Does Claude still answer, or does it say it doesn't know?

**Discussion**: this is the single most common real-world RAG failure — not
the LLM "being wrong," but retrieval pulling in irrelevant context and the
LLM doing its best with bad material. Lower the confidence threshold slider
until the banner disappears — does that make the *answer* any more correct?
(It shouldn't — the threshold only changes what you're warned about, not
what's true.)

## 3. With vs. without RAG

Check **Compare with vs without RAG**, then ask a question that's specific
to your sample docs but *plausible-sounding* even without them, e.g.
*"How many vacation days do new employees get?"*

- Compare the two answers side by side.
- Which one is more confident-sounding? Which one is actually correct?

**Discussion**: an LLM without retrieval will often produce a fluent,
plausible-sounding, *wrong* answer (because typical companies do have
vacation policies, just not *this* one). This is the core argument for RAG:
grounding doesn't just add information, it prevents confident fabrication.

## 4. Chunk size tradeoffs

Set chunk size very small (e.g. 30 words, overlap 5) and click **Rebuild
Index**. Ask a question that needs two sentences of context to answer fully
(e.g. *"What happens to unused vacation days?"* — needs both the rollover
rule and the forfeiture rule).

- Does the retrieved chunk contain the full answer, or is it cut off?
- Now set chunk size very large (e.g. 1500) and rebuild. What changes about precision — are irrelevant sentences getting pulled in along with the relevant ones?

**Discussion**: there's no universally "correct" chunk size — it's a
tradeoff between *completeness* (bigger chunks keep more context together)
and *precision* (smaller chunks let retrieval be more selective).

## 5. Find the smallest Top-K that still works

Pick a question with a clear single-document answer. Set Top-K to 1 and
ask it. Then try Top-K 2, 3, 5.

- At what point does adding more retrieved chunks stop changing or improving the answer?
- Does a *very* high Top-K ever make the answer worse (by diluting the prompt with irrelevant chunks)?

## 6. Bring your own document

Use the **Add your own document** panel to paste in a short paragraph
about something not covered by the sample docs (a course syllabus excerpt,
a recipe, anything ~100-300 words).

- Ask a question about it immediately. Does retrieval find it?
- Where does it land in the embedding plot relative to the existing HR documents — close or far? Why might that be?

---

### For instructors

These exercises map directly onto the gaps a student needs to close to
understand RAG end-to-end: *why retrieval can fail* (#2), *why grounding
matters* (#3), *chunking tradeoffs* (#4), *how much context is enough*
(#5), and *that the corpus is just data you control* (#6). Consider having
students write a 2-3 sentence answer to each "Discussion" prompt as a
deliverable.
