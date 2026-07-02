// --- i18n --------------------------------------------------------------
// Only static UI chrome (labels, explanations) is translated. Document
// text, retrieved chunks, and LLM answers stay as-is -- those are content,
// not interface, and translating them would require a separate Indonesian
// corpus or a live translation call.

const TRANSLATIONS = {
  en: {
    subtitle: "Don't just watch RAG happen — change the knobs and see why it matters.",
    controlsTitle: "Pipeline controls",
    chunkSizeLabel: "Chunk size (words)",
    overlapLabel: "Overlap (words)",
    rebuildButton: "Rebuild Index",
    rebuildingButton: "Rebuilding...",
    topkLabel: "Top-K retrieved",
    thresholdLabel: "Low-confidence threshold",
    controlsExplain: 'Top-K and the threshold apply on the next question you ask. Chunk size and overlap '
      + 'require <strong>Rebuild Index</strong> — chunking happens when documents are ingested, '
      + 'not per-query, just like in a real RAG system.',
    useRagLabel: "Use RAG (retrieve context before answering)",
    compareLabel: "Compare with vs without RAG",
    addDocSummary: "Add your own document to the corpus",
    addDocTip: "Paste in your own text and it gets chunked and indexed immediately, so you can test retrieval on something other than the built-in sample documents.",
    docNamePlaceholder: "Document name (optional)",
    docTextPlaceholder: "Paste some text here, then click Add...",
    addDocButton: "Add to corpus",
    addingButton: "Adding...",
    queryPlaceholder: "Ask a question about the sample docs...",
    askButton: "Ask",
    thinkingButton: "Thinking...",
    hint: 'Try: "What is the company\'s vacation policy?" or "How do I reset my password?" — or something not in the docs at all.',
    stage1Title: "Chunking",
    chunk_intro: "The document corpus was split into overlapping chunks at index time. There are",
    chunk_total_size: "chunks total (chunk size",
    chunk_overlap_frag: ", overlap",
    chunk_end: ").",
    whyMatters: "Why does this matter?",
    stage1WhyList: '<li><strong>Why chunk at all:</strong> embedding models and LLM context windows have limits, and retrieval is more precise over short, focused passages than over whole documents — a 5-page policy embedded as one vector blurs together every topic in it.</li>'
      + '<li><strong>The size tradeoff:</strong> chunks too small lose surrounding context (an answer might need the sentence before or after); chunks too large dilute the embedding\'s "topic signal," so retrieval gets fuzzier and less precise.</li>'
      + '<li><strong>Why overlap:</strong> without it, a fact that happens to fall right at a chunk boundary gets split in half and may not be retrievable in full from either piece.</li>'
      + '<li><strong>No universal right answer</strong> — a good starting point is ~150-400 words for prose, smaller for FAQ-style content, larger when answers need multi-sentence context. Try shrinking the chunk size and rebuilding to feel the tradeoff yourself (see <code>docs/LAB_WORKSHEET.md</code> exercise 4).</li>',
    stage2Title: "Embedding Space & Retrieval",
    stage2Explain: "Every chunk is a point in high-dimensional space, projected here to 2D. Your question "
      + "(★) lands near chunks with similar meaning — those are the ones retrieved (highlighted, ranked below).",
    stage2WhyList: '<li><strong>Why embeddings:</strong> comparing raw text only catches keyword overlap — "vacation days" and "PTO accrual" share no words but mean almost the same thing. Embeddings let us compare <em>meaning</em> instead of exact wording.</li>'
      + "<li><strong>What the score means:</strong> cosine similarity measures the angle between two vectors, not their length — so it's about topical direction, not how much text there is.</li>"
      + "<li><strong>The Top-K tradeoff:</strong> too few risks missing the chunk that actually has the answer; too many dilutes the prompt with irrelevant text and costs more tokens for no benefit. There's no fixed right number — it depends on how much the corpus overlaps in topic.</li>"
      + "<li><strong>A weak top score is a real signal:</strong> it usually means retrieval — not the LLM — is the part of the system that's failing. See <code>docs/LAB_WORKSHEET.md</code> exercise 2.</li>",
    stage3Title: "Augmented Prompt",
    stage3Explain: "This is the literal text sent to Claude when using RAG: the retrieved chunks as context, plus your question.",
    stage3WhyList: "<li><strong>The model only knows what's here</strong> (plus whatever it learned during training). If retrieval pulled in the wrong chunks, no amount of clever prompting in step 4 can recover the missing fact — the failure already happened upstream.</li>"
      + '<li><strong>This is also a trust boundary:</strong> in a real system, anything in retrieved documents is concatenated into the prompt as if it were trusted context. If a document contained adversarial instructions, the model might follow them — this is the basis of "prompt injection" attacks on RAG systems, worth knowing about even though this demo doesn\'t defend against it.</li>'
      + '<li><strong>Prompt size is a budget:</strong> every retrieved chunk costs tokens (and money, and latency) — that\'s part of why Top-K and chunk size aren\'t "bigger is always better."</li>',
    stage4Title: "Answer",
    stage4Explain: "Claude's response. In compare mode, the RAG answer (grounded in your docs) sits next to "
      + "the no-RAG baseline (Claude's general knowledge alone).",
    stage4WhyList: '<li><strong>Grounding reduces hallucination, it doesn\'t eliminate it.</strong> The system prompt explicitly instructs the model to say "I don\'t know" rather than guess when the context doesn\'t contain the answer — try comparing this to the no-RAG baseline on a question outside the corpus.</li>'
      + "<li><strong>A confident-sounding wrong answer is the dangerous failure mode</strong> — not an obvious error. Without retrieval, an LLM will often produce a fluent, plausible, but factually wrong answer about specifics it was never told (see <code>docs/LAB_WORKSHEET.md</code> exercise 3).</li>",
    withRag: "With RAG",
    withoutRag: "Without RAG",
    footer: 'Fork this on GitHub and extend it with your AI coding assistant of choice. See <code>docs/EXTENDING.md</code> and <code>docs/LAB_WORKSHEET.md</code> for ideas.',
    errRebuild: "Could not rebuild the index.",
    errAddDoc: "Could not add the document.",
    errGeneric: "Something went wrong.",
    errUnreachable: "Could not reach the server. Is app.py running?",
    confidenceLead: "⚠️ Low retrieval confidence — the best matching chunk scored",
    confidenceMid: ", below your threshold of",
    confidenceEnd: ". The corpus may not actually contain the answer to this question.",
    queryVectorLabel: "Your question, as it's actually stored:",
    vectorPreviewLead: "Showing",
    vectorPreviewMid: "of",
    vectorPreviewEnd: "numbers — this is literally what gets compared behind the scenes.",
    tooltipAriaLabel: "What does this do?",
    chunkSizeTip: "How many words go into each piece when documents are split up. Bigger chunks keep more context together; smaller chunks let retrieval be more precise. There's no universal right answer -- try changing it and rebuilding to feel the tradeoff.",
    overlapTip: "How many words repeat between consecutive chunks. Without overlap, a fact that falls right on a chunk boundary could get cut in half and become unretrievable from either piece.",
    rebuildTip: "Chunk size and overlap only take effect after you click this. Chunking happens once, when documents are ingested -- not on every question -- just like a real RAG system.",
    topkTip: "How many chunks get handed to the LLM as context for each question. Too few risks missing the answer; too many wastes tokens on irrelevant text.",
    thresholdTip: "If the best-matching chunk scores below this number, you'll see a warning banner. This doesn't change what gets retrieved -- only whether you're warned the answer might be unreliable.",
    useRagTip: "When checked, the system retrieves relevant chunks before answering. Uncheck it to see what Claude says using only its general training -- no access to your documents at all.",
    compareTip: "Runs both the grounded (RAG) answer and the ungrounded baseline side by side for the same question, so you can see the difference directly instead of taking it on faith.",
    introTitle: "What is RAG?",
    introBody: "Retrieval-Augmented Generation (RAG) lets an AI answer questions using your own documents instead of guessing from general training. Below is a real company handbook. Click below to watch one question flow through all four steps -- chunking, embedding, retrieval, and generation -- and see the answer with and without RAG side by side.",
    guidedRunButton: "Run the demo →",
    showControlsLabel: "▸ Show pipeline controls",
    hideControlsLabel: "▾ Hide pipeline controls",
    tryWithoutRagButton: "See what Claude says without your documents →",
    openConfigButton: "⚙ Configure API key",
    errorConfigureButton: "Configure API Key →",
    configModalTitle: "Configure LLM provider",
    configModalExplain: "Pick a provider and paste your API key. This takes effect on your very next question -- no restart needed -- and is saved to .env for next time.",
    configProviderLabel: "Provider",
    configKeyLabel: "API key",
    configKeyPlaceholder: "Paste your key here",
    configModelLabel: "Model (optional)",
    configCancelButton: "Cancel",
    configSaveButton: "Save",
    configKeyAlreadySet: "A key is already configured for this provider ✓",
    configKeyNotSet: "No key configured yet for this provider.",
    configNoKeyNeeded: "This provider doesn't need an API key -- just make sure its local server is running.",
    configSaving: "Saving...",
    configSaved: "Saved! Your next question will use this provider.",
    configSaveFailed: "Could not save this configuration.",
    configMissingKey: "Please paste an API key.",
    configCustomModelOption: "Custom...",
    configModelCustomPlaceholder: "Type the exact model ID",
    configOllamaModelNote: "These are common local models -- pick Custom if you pulled a different one with `ollama pull <name>`.",
  },
  id: {
    subtitle: "Jangan hanya menonton RAG bekerja — ubah pengaturannya dan lihat sendiri kenapa itu penting.",
    controlsTitle: "Kontrol pipeline",
    chunkSizeLabel: "Ukuran chunk (kata)",
    overlapLabel: "Overlap (kata)",
    rebuildButton: "Bangun Ulang Indeks",
    rebuildingButton: "Membangun ulang...",
    topkLabel: "Top-K yang diambil",
    thresholdLabel: "Ambang batas keyakinan rendah",
    controlsExplain: 'Top-K dan ambang batas berlaku untuk pertanyaan berikutnya yang kamu ajukan. Ukuran chunk dan '
      + 'overlap memerlukan <strong>Bangun Ulang Indeks</strong> — proses chunking terjadi saat dokumen diindeks, '
      + 'bukan setiap kali bertanya, sama seperti pada sistem RAG yang sesungguhnya.',
    useRagLabel: "Gunakan RAG (ambil konteks sebelum menjawab)",
    compareLabel: "Bandingkan dengan vs tanpa RAG",
    addDocSummary: "Tambahkan dokumenmu sendiri ke korpus",
    addDocTip: "Tempel teksmu sendiri dan itu akan langsung di-chunk dan diindeks, jadi kamu bisa menguji pencarian pada sesuatu selain dokumen contoh bawaan.",
    docNamePlaceholder: "Nama dokumen (opsional)",
    docTextPlaceholder: "Tempel teks di sini, lalu klik Tambah...",
    addDocButton: "Tambah ke korpus",
    addingButton: "Menambahkan...",
    queryPlaceholder: "Ajukan pertanyaan tentang dokumen contoh...",
    askButton: "Tanya",
    thinkingButton: "Memikirkan...",
    hint: 'Coba: "Bagaimana kebijakan cuti perusahaan?" atau "Bagaimana cara reset password saya?" — atau sesuatu yang sama sekali tidak ada di dokumen.',
    stage1Title: "Chunking",
    chunk_intro: "Korpus dokumen dipecah menjadi potongan (chunk) yang saling tumpang tindih saat pengindeksan. Ada",
    chunk_total_size: "chunk total (ukuran chunk",
    chunk_overlap_frag: ", overlap",
    chunk_end: ").",
    whyMatters: "Kenapa ini penting?",
    stage1WhyList: '<li><strong>Kenapa harus di-chunk:</strong> model embedding dan context window LLM punya batas, dan pencarian (retrieval) lebih akurat pada potongan teks yang pendek dan fokus dibanding dokumen utuh — kebijakan 5 halaman yang di-embed sebagai satu vektor akan mencampur semua topik di dalamnya jadi satu.</li>'
      + '<li><strong>Trade-off ukuran:</strong> chunk yang terlalu kecil kehilangan konteks sekitarnya (jawaban mungkin butuh kalimat sebelum atau sesudahnya); chunk yang terlalu besar mengencerkan "sinyal topik" pada embedding, sehingga pencarian jadi kurang presisi.</li>'
      + '<li><strong>Kenapa ada overlap:</strong> tanpa overlap, sebuah fakta yang kebetulan jatuh tepat di batas chunk bisa terpotong dua dan jadi tidak bisa diambil utuh dari kedua potongan.</li>'
      + '<li><strong>Tidak ada jawaban yang benar secara universal</strong> — titik awal yang baik adalah ~150-400 kata untuk teks naratif, lebih kecil untuk konten gaya FAQ, lebih besar saat jawaban butuh konteks beberapa kalimat. Coba perkecil ukuran chunk lalu bangun ulang untuk merasakan sendiri trade-off-nya (lihat latihan 4 di <code>docs/LAB_WORKSHEET.md</code>).</li>',
    stage2Title: "Ruang Embedding & Pencarian",
    stage2Explain: "Setiap chunk adalah sebuah titik dalam ruang berdimensi tinggi, yang diproyeksikan ke 2D di sini. "
      + "Pertanyaanmu (★) akan berada dekat dengan chunk yang maknanya mirip — itulah yang diambil (disorot, diurutkan di bawah).",
    stage2WhyList: '<li><strong>Kenapa pakai embedding:</strong> membandingkan teks mentah hanya menangkap kecocokan kata kunci — "cuti tahunan" dan "akumulasi PTO" tidak punya kata yang sama tapi maknanya hampir sama. Embedding memungkinkan kita membandingkan <em>makna</em>, bukan kata persis.</li>'
      + "<li><strong>Arti skor:</strong> cosine similarity mengukur sudut antara dua vektor, bukan panjangnya — jadi ini soal arah topik, bukan seberapa banyak teksnya.</li>"
      + "<li><strong>Trade-off Top-K:</strong> terlalu sedikit berisiko melewatkan chunk yang sebenarnya berisi jawaban; terlalu banyak mengencerkan prompt dengan teks tidak relevan dan menambah biaya token tanpa manfaat. Tidak ada angka pasti yang benar — tergantung seberapa mirip topik-topik dalam korpus.</li>"
      + "<li><strong>Skor teratas yang lemah adalah sinyal nyata:</strong> biasanya itu berarti proses pencarian (retrieval) — bukan LLM-nya — yang gagal. Lihat latihan 2 di <code>docs/LAB_WORKSHEET.md</code>.</li>",
    stage3Title: "Prompt Teraugmentasi",
    stage3Explain: "Ini adalah teks persis yang dikirim ke Claude saat menggunakan RAG: chunk yang diambil sebagai konteks, ditambah pertanyaanmu.",
    stage3WhyList: "<li><strong>Model hanya tahu apa yang ada di sini</strong> (ditambah apa pun yang dipelajarinya saat training). Jika pencarian mengambil chunk yang salah, sehebat apa pun prompting di langkah 4 tidak bisa memulihkan fakta yang hilang — kegagalan sudah terjadi lebih dulu.</li>"
      + '<li><strong>Ini juga batas kepercayaan (trust boundary):</strong> dalam sistem nyata, apa pun yang ada di dokumen yang diambil akan digabungkan ke dalam prompt seolah-olah itu konteks yang tepercaya. Jika sebuah dokumen berisi instruksi berbahaya, model bisa saja mengikutinya — inilah dasar serangan "prompt injection" pada sistem RAG, penting untuk diketahui meskipun demo ini belum punya pertahanan terhadapnya.</li>'
      + '<li><strong>Ukuran prompt adalah anggaran (budget):</strong> setiap chunk yang diambil memakan token (dan uang, dan waktu) — itu sebagian alasan kenapa Top-K dan ukuran chunk tidak selalu "makin besar makin baik."</li>',
    stage4Title: "Jawaban",
    stage4Explain: "Respons dari Claude. Dalam mode bandingkan, jawaban RAG (berlandaskan dokumenmu) ditampilkan "
      + "berdampingan dengan jawaban tanpa-RAG (pengetahuan umum Claude saja).",
    stage4WhyList: '<li><strong>Grounding mengurangi halusinasi, bukan menghilangkannya sepenuhnya.</strong> System prompt secara eksplisit menginstruksikan model untuk bilang "saya tidak tahu" alih-alih menebak ketika konteksnya tidak berisi jawaban — coba bandingkan ini dengan jawaban tanpa-RAG untuk pertanyaan di luar korpus.</li>'
      + "<li><strong>Jawaban salah yang terdengar percaya diri adalah mode kegagalan paling berbahaya</strong> — bukan kesalahan yang jelas-jelas terlihat. Tanpa pencarian, LLM sering menghasilkan jawaban yang lancar, masuk akal, tapi salah secara faktual tentang detail yang tidak pernah diberitahukan padanya (lihat latihan 3 di <code>docs/LAB_WORKSHEET.md</code>).</li>",
    withRag: "Dengan RAG",
    withoutRag: "Tanpa RAG",
    footer: 'Fork repositori ini di GitHub dan kembangkan dengan asisten coding AI pilihanmu. Lihat <code>docs/EXTENDING.md</code> dan <code>docs/LAB_WORKSHEET.md</code> untuk ide-ide lebih lanjut.',
    errRebuild: "Indeks gagal dibangun ulang.",
    errAddDoc: "Dokumen gagal ditambahkan.",
    errGeneric: "Terjadi kesalahan.",
    errUnreachable: "Tidak bisa terhubung ke server. Apakah app.py sedang berjalan?",
    confidenceLead: "⚠️ Keyakinan pencarian rendah — skor chunk terbaik adalah",
    confidenceMid: ", di bawah ambang batasmu yaitu",
    confidenceEnd: ". Kemungkinan korpus ini tidak benar-benar berisi jawaban untuk pertanyaan ini.",
    queryVectorLabel: "Pertanyaanmu, sebagaimana benar-benar disimpan:",
    vectorPreviewLead: "Menampilkan",
    vectorPreviewMid: "dari",
    vectorPreviewEnd: "angka — inilah yang sebenarnya dibandingkan di balik layar.",
    tooltipAriaLabel: "Apa fungsi ini?",
    chunkSizeTip: "Berapa banyak kata yang masuk ke setiap potongan saat dokumen dipecah. Chunk yang lebih besar menjaga lebih banyak konteks tetap menyatu; chunk yang lebih kecil membuat pencarian lebih presisi. Tidak ada jawaban yang benar secara universal — coba ubah nilainya lalu bangun ulang untuk merasakan trade-off-nya.",
    overlapTip: "Berapa banyak kata yang diulang di antara chunk yang berurutan. Tanpa overlap, sebuah fakta yang jatuh tepat di batas chunk bisa terpotong dua dan jadi tidak bisa diambil utuh dari kedua potongan.",
    rebuildTip: "Ukuran chunk dan overlap baru berlaku setelah kamu klik tombol ini. Proses chunking terjadi sekali, saat dokumen diindeks — bukan setiap kali ada pertanyaan — sama seperti sistem RAG yang sesungguhnya.",
    topkTip: "Berapa banyak chunk yang diberikan ke LLM sebagai konteks untuk setiap pertanyaan. Terlalu sedikit berisiko melewatkan jawaban; terlalu banyak memboroskan token untuk teks yang tidak relevan.",
    thresholdTip: "Jika chunk dengan skor tertinggi berada di bawah angka ini, kamu akan melihat banner peringatan. Ini tidak mengubah apa yang diambil — hanya mengubah apakah kamu diperingatkan bahwa jawabannya mungkin tidak bisa diandalkan.",
    useRagTip: "Saat dicentang, sistem akan mengambil chunk yang relevan sebelum menjawab. Hilangkan centangnya untuk melihat jawaban Claude hanya dari pengetahuan umumnya — tanpa akses ke dokumenmu sama sekali.",
    compareTip: "Menjalankan jawaban RAG (berlandaskan dokumen) dan jawaban tanpa-RAG (baseline) berdampingan untuk pertanyaan yang sama, jadi kamu bisa melihat langsung perbedaannya, bukan hanya percaya begitu saja.",
    introTitle: "Apa itu RAG?",
    introBody: "Retrieval-Augmented Generation (RAG) memungkinkan AI menjawab pertanyaan menggunakan dokumenmu sendiri, bukan menebak dari pengetahuan umum. Di bawah ini ada buku pedoman perusahaan yang nyata. Klik tombol di bawah untuk melihat satu pertanyaan mengalir melalui keempat tahap — chunking, embedding, retrieval, dan generation — dan lihat jawabannya dengan dan tanpa RAG secara berdampingan.",
    guidedRunButton: "Jalankan demo →",
    showControlsLabel: "▸ Tampilkan kontrol pipeline",
    hideControlsLabel: "▾ Sembunyikan kontrol pipeline",
    tryWithoutRagButton: "Lihat jawaban Claude tanpa dokumenmu →",
    openConfigButton: "⚙ Atur kunci API",
    errorConfigureButton: "Atur Kunci API →",
    configModalTitle: "Atur penyedia LLM",
    configModalExplain: "Pilih penyedia dan tempel kunci API-mu. Ini langsung berlaku untuk pertanyaan berikutnya -- tanpa perlu restart -- dan disimpan ke .env untuk lain kali.",
    configProviderLabel: "Penyedia",
    configKeyLabel: "Kunci API",
    configKeyPlaceholder: "Tempel kuncimu di sini",
    configModelLabel: "Model (opsional)",
    configCancelButton: "Batal",
    configSaveButton: "Simpan",
    configKeyAlreadySet: "Kunci sudah dikonfigurasi untuk penyedia ini ✓",
    configKeyNotSet: "Belum ada kunci untuk penyedia ini.",
    configNoKeyNeeded: "Penyedia ini tidak butuh kunci API -- pastikan saja server lokalnya berjalan.",
    configSaving: "Menyimpan...",
    configSaved: "Tersimpan! Pertanyaan berikutnya akan pakai penyedia ini.",
    configSaveFailed: "Gagal menyimpan konfigurasi ini.",
    configMissingKey: "Silakan tempel kunci API.",
    configCustomModelOption: "Kustom...",
    configModelCustomPlaceholder: "Ketik ID model yang persis",
    configOllamaModelNote: "Ini adalah model lokal yang umum -- pilih Kustom jika kamu menarik model lain dengan `ollama pull <nama>`.",
  },
};

let currentLang = localStorage.getItem("ragLabLang") || "en";

function t(key) {
  return (TRANSLATIONS[currentLang] && TRANSLATIONS[currentLang][key]) ?? TRANSLATIONS.en[key] ?? key;
}

function applyLanguage(lang) {
  currentLang = TRANSLATIONS[lang] ? lang : "en";
  localStorage.setItem("ragLabLang", currentLang);
  document.documentElement.lang = currentLang;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-html]").forEach((el) => {
    el.innerHTML = t(el.dataset.i18nHtml);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-attr-aria-label]").forEach((el) => {
    el.setAttribute("aria-label", t(el.dataset.i18nAttrAriaLabel));
  });
  document.querySelectorAll(".lang-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.lang === currentLang);
  });
  // Re-render whichever tooltip is currently open, if any, in the new language.
  if (tooltipPopup && !tooltipPopup.hidden && tooltipPopup.dataset.openFor) {
    tooltipTextEl.textContent = t(tooltipPopup.dataset.openFor);
  }
}

document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => applyLanguage(btn.dataset.lang));
});

// --- element refs ---------------------------------------------------------
const form = document.getElementById("query-form");
const input = document.getElementById("query-input");
const askButton = document.getElementById("ask-button");
const pipeline = document.getElementById("pipeline");
const errorBox = document.getElementById("error-box");

const chunkSizeInput = document.getElementById("chunk-size-input");
const overlapInput = document.getElementById("overlap-input");
const rebuildButton = document.getElementById("rebuild-button");
const topkInput = document.getElementById("topk-input");
const thresholdInput = document.getElementById("threshold-input");
const useRagCheckbox = document.getElementById("use-rag-checkbox");
const compareCheckbox = document.getElementById("compare-checkbox");

const docNameInput = document.getElementById("doc-name-input");
const docTextInput = document.getElementById("doc-text-input");
const addDocButton = document.getElementById("add-doc-button");

const allChunksEl = document.getElementById("all-chunks");
const chunkCountEl = document.getElementById("chunk-count");
const chunkSizeDisplay = document.getElementById("chunk-size-display");
const overlapDisplay = document.getElementById("overlap-display");
const retrievedChunksEl = document.getElementById("retrieved-chunks");
const promptTextEl = document.getElementById("prompt-text");
const confidenceBanner = document.getElementById("confidence-banner");
const plotEl = document.getElementById("embedding-plot");

const ragCol = document.getElementById("rag-col");
const noRagCol = document.getElementById("no-rag-col");
const ragAnswerEl = document.getElementById("rag-answer-text");
const noRagAnswerEl = document.getElementById("no-rag-answer-text");

const queryVectorPanel = document.getElementById("query-vector-panel");
const queryVectorBarsEl = document.getElementById("query-vector-bars");
const queryVectorNoteEl = document.getElementById("query-vector-note");

const tooltipPopup = document.getElementById("tooltip-popup");
const tooltipTextEl = document.getElementById("tooltip-text");

const errorTextEl = document.getElementById("error-text");
const errorConfigureButton = document.getElementById("error-configure-button");
const openConfigButton = document.getElementById("open-config-button");

const configModalOverlay = document.getElementById("config-modal-overlay");
const configProviderSelect = document.getElementById("config-provider-select");
const configKeyField = document.getElementById("config-key-field");
const configKeyInput = document.getElementById("config-key-input");
const configKeyStatus = document.getElementById("config-key-status");
const configModelSelect = document.getElementById("config-model-select");
const configModelCustomInput = document.getElementById("config-model-custom-input");
const configModelNote = document.getElementById("config-model-note");
const configModalMessage = document.getElementById("config-modal-message");
const configCancelButton = document.getElementById("config-cancel-button");
const configSaveButton = document.getElementById("config-save-button");

const introCard = document.getElementById("intro-card");
const guidedRunButton = document.getElementById("guided-run-button");
const controlsBody = document.getElementById("controls-body");
const toggleControlsButton = document.getElementById("toggle-controls-button");
const tryWithoutRagButton = document.getElementById("try-without-rag-button");

const stageChunking = document.getElementById("stage-chunking");
const stageEmbedding = document.getElementById("stage-embedding");
const stagePrompt = document.getElementById("stage-prompt");
const stageAnswer = document.getElementById("stage-answer");
const STAGE_ELEMENTS = [stageChunking, stageEmbedding, stagePrompt, stageAnswer];

const GUIDED_EXAMPLE_QUERY = "What is the company's vacation policy?";

let allChunks = []; // cached for plotting against the latest retrieval/query point
let hasRunOnce = localStorage.getItem("ragLabHasRun") === "1";
let lastQuery = "";

// --- info tooltips on the pipeline controls ---------------------------------
// Click a "?" badge to see a short, plain-language explanation of that
// control. Badges pulse once (until the first click, ever) to make them
// discoverable without being a permanent distraction.

function closeTooltip() {
  tooltipPopup.hidden = true;
  tooltipPopup.dataset.openFor = "";
}

function openTooltip(badge) {
  tooltipTextEl.textContent = t(badge.dataset.tip);
  tooltipPopup.hidden = false;
  tooltipPopup.dataset.openFor = badge.dataset.tip;

  // Positioned against viewport coordinates (position: fixed in CSS) rather
  // than relying on offsetParent -- simpler and can't break if an ancestor's
  // positioning context ever changes.
  const badgeRect = badge.getBoundingClientRect();
  const maxLeft = window.innerWidth - tooltipPopup.offsetWidth - 8;
  const left = Math.max(8, Math.min(badgeRect.left, maxLeft));
  tooltipPopup.style.top = (badgeRect.bottom + 8) + "px";
  tooltipPopup.style.left = left + "px";
}

document.querySelectorAll(".info-badge").forEach((badge) => {
  badge.addEventListener("click", (event) => {
    event.stopPropagation();
    const alreadyOpenForThis = !tooltipPopup.hidden && tooltipPopup.dataset.openFor === badge.dataset.tip;
    document.querySelectorAll(".info-badge").forEach((b) => b.classList.remove("pulse"));
    localStorage.setItem("ragLabTooltipsSeen", "1");
    if (alreadyOpenForThis) {
      closeTooltip();
    } else {
      openTooltip(badge);
    }
  });
});

if (localStorage.getItem("ragLabTooltipsSeen")) {
  document.querySelectorAll(".info-badge").forEach((b) => b.classList.remove("pulse"));
}

tooltipPopup.addEventListener("click", (event) => event.stopPropagation());
document.addEventListener("click", closeTooltip);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeTooltip();
    closeConfigModal();
  }
});

// --- API key configuration modal --------------------------------------------
// Lets a student pick a provider and paste a key without touching .env or
// restarting the server -- rag/generation.py reads os.environ at call
// time, so the very next query picks up whatever was just saved here.

let allProvidersInfo = {};
let pendingConfigRetry = false; // true when the modal was opened from a real error, to offer a re-run on save
const CUSTOM_MODEL_VALUE = "__custom__";

// Populates the model <select> with that provider's known model IDs plus a
// "Custom..." option. Selecting a known ID avoids the exact bug that
// prompted this feature: a student typing a display name (e.g. "GPT Mini")
// instead of a real API model ID ("gpt-4o-mini") and getting a cryptic
// "invalid model" error from the provider.
function populateModelSelect(provider, currentModel) {
  const info = allProvidersInfo[provider];
  if (!info) return;

  configModelSelect.innerHTML = "";
  info.model_choices.forEach((modelId) => {
    const option = document.createElement("option");
    option.value = modelId;
    option.textContent = modelId;
    configModelSelect.appendChild(option);
  });
  const customOption = document.createElement("option");
  customOption.value = CUSTOM_MODEL_VALUE;
  customOption.textContent = t("configCustomModelOption");
  configModelSelect.appendChild(customOption);

  if (currentModel && info.model_choices.includes(currentModel)) {
    configModelSelect.value = currentModel;
    configModelCustomInput.hidden = true;
    configModelCustomInput.value = "";
  } else if (currentModel) {
    configModelSelect.value = CUSTOM_MODEL_VALUE;
    configModelCustomInput.hidden = false;
    configModelCustomInput.value = currentModel;
  } else {
    configModelSelect.value = info.model_default;
    configModelCustomInput.hidden = true;
    configModelCustomInput.value = "";
  }
  configModelNote.textContent = provider === "ollama" ? t("configOllamaModelNote") : "";
}

configModelSelect.addEventListener("change", () => {
  configModelCustomInput.hidden = configModelSelect.value !== CUSTOM_MODEL_VALUE;
});

function updateConfigFieldsForProvider(provider, keyConfigured, currentModel) {
  const info = allProvidersInfo[provider];
  if (!info) return;
  configKeyField.hidden = !info.key_required;
  populateModelSelect(provider, currentModel);
  if (!info.key_required) {
    configKeyStatus.textContent = t("configNoKeyNeeded");
  } else if (keyConfigured === true) {
    configKeyStatus.textContent = t("configKeyAlreadySet");
  } else if (keyConfigured === false) {
    configKeyStatus.textContent = t("configKeyNotSet");
  } else {
    configKeyStatus.textContent = "";
  }
}

async function openConfigModal(fromError = false) {
  pendingConfigRetry = fromError;
  configModalMessage.textContent = "";
  configKeyInput.value = "";
  configModalOverlay.hidden = false;
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    allProvidersInfo = data.all_providers || {};
    configProviderSelect.value = data.provider;
    updateConfigFieldsForProvider(data.provider, data.key_configured, data.model);
  } catch (err) {
    configModalMessage.textContent = t("errUnreachable");
  }
}

function closeConfigModal() {
  configModalOverlay.hidden = true;
}

openConfigButton.addEventListener("click", () => openConfigModal(false));
errorConfigureButton.addEventListener("click", () => openConfigModal(true));
configCancelButton.addEventListener("click", closeConfigModal);
configModalOverlay.addEventListener("click", (event) => {
  if (event.target === configModalOverlay) closeConfigModal();
});

configProviderSelect.addEventListener("change", () => {
  updateConfigFieldsForProvider(configProviderSelect.value, undefined, undefined);
});

configSaveButton.addEventListener("click", async () => {
  const provider = configProviderSelect.value;
  const info = allProvidersInfo[provider];
  const apiKey = configKeyInput.value.trim();
  const model = configModelSelect.value === CUSTOM_MODEL_VALUE
    ? configModelCustomInput.value.trim()
    : configModelSelect.value;

  if (info && info.key_required && !apiKey) {
    configModalMessage.textContent = t("configMissingKey");
    return;
  }

  configSaveButton.disabled = true;
  configSaveButton.textContent = t("configSaving");
  configModalMessage.textContent = "";

  try {
    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider,
        api_key: apiKey,
        model,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      configModalMessage.textContent = data.error || t("configSaveFailed");
      return;
    }
    configModalMessage.textContent = t("configSaved");
    const shouldRetry = pendingConfigRetry && lastQuery;
    setTimeout(() => {
      closeConfigModal();
      if (shouldRetry) runQuery({ query: lastQuery });
    }, 900);
  } catch (err) {
    configModalMessage.textContent = t("errUnreachable");
  } finally {
    configSaveButton.disabled = false;
    configSaveButton.textContent = t("configSaveButton");
  }
});

// --- helpers ---------------------------------------------------------------

function scoreTier(score) {
  const threshold = parseFloat(thresholdInput.value) || 0.3;
  if (score >= threshold + 0.2) return "good";
  if (score >= threshold) return "ok";
  return "weak";
}

// Renders a small row of signed bars from a slice of a real embedding
// vector -- positive values grow up from a shared zero-line in accent
// color, negative values grow down in "weak" red, so similarly-shaped
// chunks are visually scannable next to the query's own bars. The actual
// numbers are also printed below, since a bar chart alone doesn't answer
// "is that supposed to be numbers?" -- it should look like numbers too.
function renderVectorBars(values) {
  const wrap = document.createElement("div");
  wrap.className = "vec-bars";

  const scale = 0.3; // typical MiniLM component magnitude; values beyond this just cap at full height
  values.forEach((v) => {
    const slot = document.createElement("span");
    slot.className = "vec-bar-slot";
    const fill = document.createElement("span");
    fill.className = "vec-bar-fill " + (v >= 0 ? "vec-bar-pos" : "vec-bar-neg");
    // Height is a % of the whole slot, capped at 50% since a bar can only
    // reach from the center line to one edge (up for positive, down for negative).
    const heightPct = Math.min(Math.abs(v) / scale, 1) * 50;
    fill.style.height = heightPct + "%";
    fill.title = v.toFixed(4);
    slot.appendChild(fill);
    wrap.appendChild(slot);
  });

  const numbers = document.createElement("div");
  numbers.className = "vec-numbers";
  numbers.textContent = values.map((v) => v.toFixed(3)).join("  ");

  const container = document.createElement("div");
  container.appendChild(wrap);
  container.appendChild(numbers);
  return container;
}

function renderChunkItem({ source, index, text, score, vector_preview }) {
  const div = document.createElement("div");
  div.className = "chunk-item";
  const meta = document.createElement("div");
  meta.className = "chunk-meta";
  let scoreHtml = "";
  if (score !== undefined) {
    scoreHtml = `<span class="chunk-score score-${scoreTier(score)}">score: ${score.toFixed(3)}</span>`;
  }
  meta.innerHTML = `<span>${source} #${index}</span>${scoreHtml}`;
  const body = document.createElement("div");
  body.textContent = text;
  div.appendChild(meta);
  div.appendChild(body);
  if (vector_preview) {
    div.appendChild(renderVectorBars(vector_preview));
  }
  return div;
}

function showError(message, needsConfig = false) {
  errorTextEl.textContent = message;
  errorConfigureButton.hidden = !needsConfig;
  errorBox.hidden = false;
}

function hideError() {
  errorBox.hidden = true;
  errorTextEl.textContent = "";
  errorConfigureButton.hidden = true;
}

// --- embedding plot (plain SVG, no charting library) -----------------------

const SOURCE_COLORS = ["#7c9eff", "#6fd394", "#f2b66d", "#e87a9c", "#9d7cff", "#5fd0c9"];

function colorForSource(source) {
  let hash = 0;
  for (let i = 0; i < source.length; i++) hash = (hash * 31 + source.charCodeAt(i)) >>> 0;
  return SOURCE_COLORS[hash % SOURCE_COLORS.length];
}

function renderPlot(chunks, queryPoint, retrievedKeys) {
  plotEl.innerHTML = "";
  if (!chunks.length) return;

  const xs = chunks.map((c) => c.x).concat(queryPoint ? [queryPoint.x] : []);
  const ys = chunks.map((c) => c.y).concat(queryPoint ? [queryPoint.y] : []);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const pad = 30;
  const W = 420, H = 320;

  function sx(x) {
    if (maxX === minX) return W / 2;
    return pad + ((x - minX) / (maxX - minX)) * (W - 2 * pad);
  }
  function sy(y) {
    if (maxY === minY) return H / 2;
    return pad + ((y - minY) / (maxY - minY)) * (H - 2 * pad);
  }

  const ns = "http://www.w3.org/2000/svg";

  chunks.forEach((c) => {
    const key = `${c.source}#${c.index}`;
    const isRetrieved = retrievedKeys.has(key);
    const circle = document.createElementNS(ns, "circle");
    circle.setAttribute("cx", sx(c.x));
    circle.setAttribute("cy", sy(c.y));
    circle.setAttribute("r", isRetrieved ? 7 : 5);
    circle.setAttribute("fill", colorForSource(c.source));
    circle.setAttribute("fill-opacity", isRetrieved ? "1" : "0.45");
    circle.setAttribute("stroke", isRetrieved ? "#fff" : "none");
    circle.setAttribute("stroke-width", "1.5");
    const title = document.createElementNS(ns, "title");
    title.textContent = `${c.source} #${c.index}`;
    circle.appendChild(title);
    plotEl.appendChild(circle);

    if (isRetrieved && queryPoint) {
      const line = document.createElementNS(ns, "line");
      line.setAttribute("x1", sx(queryPoint.x));
      line.setAttribute("y1", sy(queryPoint.y));
      line.setAttribute("x2", sx(c.x));
      line.setAttribute("y2", sy(c.y));
      line.setAttribute("stroke", "#7c9eff");
      line.setAttribute("stroke-width", "1");
      line.setAttribute("stroke-opacity", "0.4");
      line.setAttribute("stroke-dasharray", "3,3");
      plotEl.insertBefore(line, plotEl.firstChild);
    }
  });

  if (queryPoint) {
    const star = document.createElementNS(ns, "text");
    star.setAttribute("x", sx(queryPoint.x));
    star.setAttribute("y", sy(queryPoint.y) + 6);
    star.setAttribute("text-anchor", "middle");
    star.setAttribute("font-size", "20");
    star.setAttribute("fill", "#fff");
    star.textContent = "★";
    plotEl.appendChild(star);
  }
}

// --- chunk list / index management -----------------------------------------

function applyChunksResponse(data) {
  allChunks = data.chunks;
  chunkCountEl.textContent = data.chunk_count;
  chunkSizeDisplay.textContent = data.chunk_size;
  overlapDisplay.textContent = data.overlap;
  chunkSizeInput.value = data.chunk_size;
  overlapInput.value = data.overlap;

  allChunksEl.innerHTML = "";
  data.chunks.forEach((c) => allChunksEl.appendChild(renderChunkItem(c)));
  renderPlot(allChunks, null, new Set());
}

async function loadAllChunks() {
  const res = await fetch("/api/chunks");
  applyChunksResponse(await res.json());
}

rebuildButton.addEventListener("click", async () => {
  rebuildButton.disabled = true;
  rebuildButton.textContent = t("rebuildingButton");
  hideError();
  try {
    const res = await fetch("/api/reindex", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chunk_size: parseInt(chunkSizeInput.value, 10),
        overlap: parseInt(overlapInput.value, 10),
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || t("errRebuild"));
      return;
    }
    applyChunksResponse(data);
  } catch (err) {
    showError(t("errUnreachable"));
  } finally {
    rebuildButton.disabled = false;
    rebuildButton.textContent = t("rebuildButton");
  }
});

addDocButton.addEventListener("click", async () => {
  const text = docTextInput.value.trim();
  if (!text) return;
  addDocButton.disabled = true;
  addDocButton.textContent = t("addingButton");
  hideError();
  try {
    const res = await fetch("/api/documents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: docNameInput.value.trim(), text }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || t("errAddDoc"));
      return;
    }
    applyChunksResponse(data);
    docNameInput.value = "";
    docTextInput.value = "";
  } catch (err) {
    showError(t("errUnreachable"));
  } finally {
    addDocButton.disabled = false;
    addDocButton.textContent = t("addDocButton");
  }
});

// --- guided first run & sequential stage reveal -----------------------------
// The four pipeline stages are hidden by default (see index.html) so that
// on every run -- guided or free exploration -- they reveal one at a time,
// reinforcing that RAG is a pipeline, not a single black-box step.

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function revealStagesSequentially() {
  for (const el of STAGE_ELEMENTS) {
    el.hidden = false;
    if (typeof el.scrollIntoView === "function") {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
    await delay(550);
  }
}

// First successful run (guided or manual) permanently ends onboarding for
// this browser: the intro card disappears and the controls panel becomes
// available, via the same localStorage-gated pattern already used for the
// language preference and tooltip-pulse state.
function markFirstRunComplete() {
  if (hasRunOnce) return;
  hasRunOnce = true;
  localStorage.setItem("ragLabHasRun", "1");
  introCard.hidden = true;
  controlsBody.hidden = false;
  toggleControlsButton.dataset.i18n = "hideControlsLabel";
  toggleControlsButton.textContent = t("hideControlsLabel");
}

toggleControlsButton.addEventListener("click", () => {
  controlsBody.hidden = !controlsBody.hidden;
  const key = controlsBody.hidden ? "showControlsLabel" : "hideControlsLabel";
  toggleControlsButton.dataset.i18n = key;
  toggleControlsButton.textContent = t(key);
});

guidedRunButton.addEventListener("click", () => {
  runQuery({ query: GUIDED_EXAMPLE_QUERY, compare: true });
});

tryWithoutRagButton.addEventListener("click", () => {
  runQuery({ query: lastQuery, compare: true });
});

// --- asking a question -------------------------------------------------------

function renderAnswerColumn(col, textEl, result) {
  if (!result) {
    col.hidden = true;
    return;
  }
  col.hidden = false;
  if (result.error) {
    textEl.textContent = "";
    showError(result.error, result.needs_config);
  } else {
    textEl.textContent = result.answer;
  }
}

// overrides.query / overrides.compare let the guided-run and "try without
// RAG" buttons trigger the same flow as the form, without duplicating it.
async function runQuery(overrides = {}) {
  const query = (overrides.query !== undefined ? overrides.query : input.value).trim();
  if (!query) return;
  input.value = query;
  lastQuery = query;
  const useCompare = overrides.compare !== undefined ? overrides.compare : compareCheckbox.checked;

  hideError();
  askButton.disabled = true;
  askButton.textContent = t("thinkingButton");
  STAGE_ELEMENTS.forEach((el) => { el.hidden = true; });

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query,
        top_k: parseInt(topkInput.value, 10),
        use_rag: useRagCheckbox.checked,
        compare: useCompare,
      }),
    });
    const data = await res.json();

    pipeline.hidden = false;
    markFirstRunComplete();

    const retrieved = data.retrieved_chunks || [];
    retrievedChunksEl.innerHTML = "";
    retrieved.forEach((c) => retrievedChunksEl.appendChild(renderChunkItem(c)));

    const retrievedKeys = new Set(retrieved.map((c) => `${c.source}#${c.index}`));
    renderPlot(allChunks, data.query_point, retrievedKeys);

    if (data.query_vector_preview) {
      queryVectorPanel.hidden = false;
      queryVectorBarsEl.innerHTML = "";
      queryVectorBarsEl.appendChild(renderVectorBars(data.query_vector_preview));
      queryVectorNoteEl.textContent =
        `${t("vectorPreviewLead")} ${data.query_vector_preview.length} ${t("vectorPreviewMid")} ${data.embedding_dim} ${t("vectorPreviewEnd")}`;
    }

    const topScore = retrieved.length ? Math.max(...retrieved.map((c) => c.score)) : 0;
    const threshold = parseFloat(thresholdInput.value) || 0.3;
    if (retrieved.length && topScore < threshold) {
      confidenceBanner.hidden = false;
      confidenceBanner.textContent =
        `${t("confidenceLead")} ${topScore.toFixed(3)}${t("confidenceMid")} ${threshold}${t("confidenceEnd")}`;
    } else {
      confidenceBanner.hidden = true;
    }

    if (!res.ok) {
      showError(data.error || t("errGeneric"));
    } else {
      promptTextEl.textContent = data.rag ? (data.rag.prompt_sent || "") : "";
      renderAnswerColumn(ragCol, ragAnswerEl, data.rag);
      renderAnswerColumn(noRagCol, noRagAnswerEl, data.no_rag);
      // Offer the with/without-RAG contrast whenever this run wasn't already a compare run.
      tryWithoutRagButton.hidden = !(data.rag && !data.no_rag);
    }

    await revealStagesSequentially();
  } catch (err) {
    showError(t("errUnreachable"));
  } finally {
    askButton.disabled = false;
    askButton.textContent = t("askButton");
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  runQuery();
});

// Initial page state: first-time visitors see the intro card with controls
// collapsed; returning visitors (per localStorage) skip straight to the
// sandbox with controls already expanded.
if (hasRunOnce) {
  introCard.hidden = true;
  controlsBody.hidden = false;
  toggleControlsButton.dataset.i18n = "hideControlsLabel";
} else {
  introCard.hidden = false;
  controlsBody.hidden = true;
  toggleControlsButton.dataset.i18n = "showControlsLabel";
}

applyLanguage(currentLang);
loadAllChunks();
