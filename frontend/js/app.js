/**
 * CogniStudy AI — Frontend Application Logic
 * Reactive state management, validation, API communication, and interactive quiz engine.
 */

// Global App State
const state = {
  currentTab: 'cornell',
  apiKey: localStorage.getItem('cogni_study_api_key') || '',
  activeMode: 'checking', // 'live', 'simulation', or 'checking'
  quizState: {
    items: [],
    userAnswers: {},
    score: 0,
    total: 0
  },
  lastCornellData: null,
  lastPolishedData: null,
  lastExplainData: null
};

// Preset sample texts
const SAMPLES = {
  biology: {
    title: "Biology: Cellular Respiration",
    notes: `Title: Cellular Respiration and ATP Synthase Mechanisms

Lecture Overview:
Cellular respiration is the fundamental biochemical pathway through which eukaryotic cells break down glucose to generate adenosine triphosphate (ATP). The overall chemical equation is:
C6H12O6 + 6O2 -> 6CO2 + 6H2O + ~30-32 ATP.

Key Stages:
1. Glycolysis:
   - Occurs in the cytoplasm (cytosol). Anaerobic process (does not require O2).
   - One glucose molecule (6 carbons) is phosphorylated and cleaved into 2 molecules of pyruvate (3 carbons each).
   - Net energy yield: 2 ATP (substrate-level phosphorylation) and 2 NADH.
   - Rate-limiting enzyme: Phosphofructokinase-1 (PFK-1), allosterically inhibited by high ATP and citrate, activated by AMP.

2. Pyruvate Oxidation (Link Reaction):
   - Pyruvate is actively transported into the mitochondrial matrix.
   - Pyruvate dehydrogenase complex catalyzes decarboxylation: pyruvate -> Acetyl-CoA + CO2 + NADH.

3. Krebs Cycle (Citric Acid Cycle / TCA Cycle):
   - Located in the mitochondrial matrix.
   - Acetyl-CoA (2C) combines with oxaloacetate (4C) to form citrate (6C).
   - Per glucose molecule: yields 6 NADH, 2 FADH2, 2 GTP/ATP, and 4 CO2.

4. Oxidative Phosphorylation & Electron Transport Chain (ETC):
   - Located along the inner mitochondrial membrane (cristae).
   - Complexes I, II, III, and IV pump protons (H+) from the matrix into the intermembrane space, creating an electrochemical proton-motive force.
   - Oxygen (O2) acts as the terminal electron acceptor, reduced to H2O via Complex IV.
   - ATP Synthase (F0F1 complex): Protons flow down their electrochemical gradient through the F0 rotor subunit, driving the rotary catalysis of F1 to synthesize ATP from ADP and Pi (chemiosmosis).
   - Inhibitors: Cyanide and CO inhibit Complex IV. DNP uncouples proton gradient from ATP synthesis, dissipating energy as heat.`,
    concept: "Chemiosmosis & Proton-Motive Force",
    domain: "Biochemistry",
    examQuestion: "Explain how the electrochemical proton gradient drives ATP synthesis across the inner mitochondrial membrane.",
    draftAnswer: "The electron transport chain pumps protons into the space between the membranes. This creates a gradient where there are more protons outside than inside. The protons then move back into the matrix through ATP synthase, and this spinning motion makes ATP from ADP and phosphate."
  },
  cs: {
    title: "CS: Operating Systems & Concurrency",
    notes: `Title: Operating Systems: Concurrency, Deadlocks, and Memory Management

1. Processes vs. Threads:
   - A process is an executing program instance with its own private virtual address space (code, data, heap, stack), file descriptors, and security attributes.
   - A thread is the smallest unit of CPU scheduling within a process. Threads in the same process share the heap, data, and code segments, but possess distinct program counters (PC), registers, and stack pointers.
   - Context Switching Overhead: Thread context switching is significantly faster than process context switching because the Memory Management Unit (MMU) does not need to invalidate the Translation Lookaside Buffer (TLB).

2. Critical Section Problem & Synchronization:
   - Race Conditions arise when multiple threads access and mutate shared mutable state without synchronization.
   - A valid solution must satisfy: Mutual Exclusion, Progress, and Bounded Waiting.
   - Primitives: Mutexes, Counting Semaphores (P/wait and V/signal), Condition Variables.

3. Deadlocks:
   - Coffman's Four Conditions (all must hold concurrently):
     1) Mutual Exclusion: Non-shareable resource.
     2) Hold and Wait: Process holds resources while requesting more.
     3) No Preemption: Resources cannot be forcibly seized.
     4) Circular Wait: Closed loop of processes waiting on each other.
   - Prevention/Avoidance: Banker's Algorithm ensures the system remains in a 'Safe State'. Resource ordering hierarchy breaks circular wait.

4. Virtual Memory & Paging:
   - MMU translates virtual addresses to physical DRAM using hierarchical page tables.
   - Page Faults trigger an OS trap when the Present bit is 0, swapping pages from disk storage.
   - Thrashing occurs when a process lacks sufficient working set frames, causing the CPU to spend more time servicing page faults than executing instructions.`,
    concept: "Coffman Deadlock Conditions",
    domain: "Computer Science",
    examQuestion: "What is thrashing in virtual memory systems, and how can the operating system mitigate it?",
    draftAnswer: "Thrashing happens when the computer runs out of RAM and has to constantly read and write pages to the hard drive. Because disk is slow, the CPU stays idle waiting for pages and performance crashes. The OS can fix it by killing some programs or using the working set model."
  },
  econ: {
    title: "Economics: Inflation & Monetary Policy",
    notes: `Title: Macroeconomics: Inflation Dynamics, Monetary Policy, and the Phillips Curve

1. Definition and Measurement:
   - Inflation: Sustained increase in aggregate price levels eroding currency purchasing power.
   - Primary Indexes: Consumer Price Index (CPI, retail consumption basket), Personal Consumption Expenditures (PCE, Fed's preferred measure, dynamic chained index), GDP Deflator.

2. Causal Theories:
   - Demand-Pull Inflation: Aggregate demand outpaces aggregate supply at full capacity ('too many dollars chasing too few goods').
   - Cost-Push Inflation: Initiated by negative aggregate supply shocks (e.g. oil embargoes) resulting in Stagflation (stagnant growth + inflation).
   - Quantity Theory of Money: M * V = P * Y. Milton Friedman's postulate: In the long run, sustained inflation is always a monetary phenomenon driven by excess money supply expansion.

3. Phillips Curve & Expectations:
   - Short-Run: Hypothesized inverse trade-off between wage inflation and unemployment.
   - Expectations-Augmented (Friedman & Phelps): Vertical at Natural Rate of Unemployment (NAIRU) in long run.
   - Rational Expectations: Anticipated expansionary policy raises inflation expectations (pi_e) without reducing long-run unemployment.

4. Monetary Transmission:
   - Central bank raises policy rate -> increases borrowing costs -> dampens capital investment (I) and consumption (C) -> contracts aggregate demand back to 2% target.`,
    concept: "Quantity Theory of Money (M*V = P*Y)",
    domain: "Economics",
    examQuestion: "Explain the difference between Demand-Pull and Cost-Push inflation and discuss why Stagflation is particularly difficult for central banks to manage.",
    draftAnswer: "Demand pull inflation is when people want to buy too many things and businesses raise prices. Cost push is when supply costs go up, like oil prices. Stagflation is bad because inflation is high and unemployment is also high, so if the central bank raises interest rates to fix inflation, unemployment gets even worse."
  }
};

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
  initIcons();
  initTabs();
  initInputCounters();
  initSampleNotesDropdown();
  initApiKeyModal();
  checkBackendHealth();
  attachActionHandlers();
});

function initIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// ---------------------------------------------------------------------------
// Tabs Navigation
// ---------------------------------------------------------------------------

function initTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      switchTab(targetTab);
    });
  });
}

function switchTab(tabId) {
  state.currentTab = tabId;
  
  document.querySelectorAll('.tab-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
  });

  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.toggle('active', pane.id === `pane-${tabId}`);
  });

  initIcons();
}

// ---------------------------------------------------------------------------
// Word & Character Counters
// ---------------------------------------------------------------------------

function initInputCounters() {
  const setupCounter = (inputId, counterId) => {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    if (!input || !counter) return;

    const update = () => {
      const text = input.value.trim();
      const words = text ? text.split(/\s+/).length : 0;
      const chars = input.value.length;
      counter.textContent = `${words} word${words === 1 ? '' : 's'} · ${chars} char${chars === 1 ? '' : 's'}`;
    };

    input.addEventListener('input', update);
    update();
  };

  setupCounter('cornellInput', 'cornellWordCount');
  setupCounter('quizInput', 'quizWordCount');
  setupCounter('polishDraft', 'polishWordCount');
}

// ---------------------------------------------------------------------------
// Sample Data Quick-Loader
// ---------------------------------------------------------------------------

function initSampleNotesDropdown() {
  const btn = document.getElementById('sampleNotesDropdownBtn');
  const menu = document.getElementById('sampleNotesMenu');

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    menu.classList.remove('show');
  });

  menu.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', () => {
      const sampleKey = item.getAttribute('data-sample');
      loadSample(sampleKey);
      menu.classList.remove('show');
    });
  });
}

function loadSample(key) {
  const data = SAMPLES[key];
  if (!data) return;

  // Populate active tab inputs
  if (state.currentTab === 'cornell') {
    const input = document.getElementById('cornellInput');
    input.value = data.notes;
    input.dispatchEvent(new Event('input'));
    showToast(`Loaded ${data.title} into Cornell Synthesizer`, 'success');
  } else if (state.currentTab === 'quiz') {
    const input = document.getElementById('quizInput');
    input.value = data.notes;
    input.dispatchEvent(new Event('input'));
    showToast(`Loaded ${data.title} into Quiz Generator`, 'success');
  } else if (state.currentTab === 'polish') {
    document.getElementById('polishQuestion').value = data.examQuestion;
    const draftInput = document.getElementById('polishDraft');
    draftInput.value = data.draftAnswer;
    draftInput.dispatchEvent(new Event('input'));
    showToast(`Loaded question and draft answer for ${data.title}`, 'success');
  } else if (state.currentTab === 'explain') {
    document.getElementById('explainConcept').value = data.concept;
    document.getElementById('explainDomain').value = data.domain;
    showToast(`Loaded concept '${data.concept}' into Feynman Explainer`, 'success');
  }
}

// ---------------------------------------------------------------------------
// API Key Management & Backend Health
// ---------------------------------------------------------------------------

async function checkBackendHealth() {
  const modePill = document.getElementById('modePill');
  const modeText = document.getElementById('modeText');
  const dot = modePill.querySelector('.status-dot');

  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    
    if (data.api_key_configured || state.apiKey) {
      state.activeMode = 'live';
      modeText.textContent = 'Live LLM (Gemini)';
      dot.className = 'status-dot dot-active';
      document.getElementById('modalKeyStatusText').textContent = 'Live Google Gemini API key configured.';
    } else {
      state.activeMode = 'simulation';
      modeText.textContent = 'Demo Simulation Engine';
      dot.className = 'status-dot dot-sim';
      document.getElementById('modalKeyStatusText').textContent = 'No key set. Running in Intelligent Offline Simulation Mode.';
    }
  } catch (err) {
    state.activeMode = 'simulation';
    modeText.textContent = 'Offline Engine (Active)';
    dot.className = 'status-dot dot-sim';
  }
}

function initApiKeyModal() {
  const modal = document.getElementById('apiKeyModal');
  const openBtn = document.getElementById('openApiKeyModalBtn');
  const closeBtn = document.getElementById('closeApiKeyModalBtn');
  const saveBtn = document.getElementById('saveApiKeyBtn');
  const clearBtn = document.getElementById('clearApiKeyBtn');
  const input = document.getElementById('modalApiKeyInput');

  if (state.apiKey) {
    input.value = state.apiKey;
  }

  openBtn.addEventListener('click', () => {
    modal.classList.remove('hidden');
    initIcons();
  });

  closeBtn.addEventListener('click', () => modal.classList.add('hidden'));

  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.add('hidden');
  });

  saveBtn.addEventListener('click', async () => {
    const key = input.value.trim();
    if (key.length < 10) {
      showToast('Key must be at least 10 characters long.', 'error');
      return;
    }

    try {
      const res = await fetch('/api/config/key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();
      if (data.success) {
        state.apiKey = key;
        localStorage.setItem('cogni_study_api_key', key);
        showToast('Google Gemini API Key saved successfully!', 'success');
        modal.classList.add('hidden');
        checkBackendHealth();
      } else {
        showToast(data.error || 'Failed to update key.', 'error');
      }
    } catch (err) {
      state.apiKey = key;
      localStorage.setItem('cogni_study_api_key', key);
      showToast('Saved locally in browser session.', 'success');
      modal.classList.add('hidden');
      checkBackendHealth();
    }
  });

  clearBtn.addEventListener('click', () => {
    state.apiKey = '';
    localStorage.removeItem('cogni_study_api_key');
    input.value = '';
    showToast('Switched to Intelligent Offline Simulation Engine.', 'info');
    modal.classList.add('hidden');
    checkBackendHealth();
  });
}

// ---------------------------------------------------------------------------
// Error Banners & Toast Notifications
// ---------------------------------------------------------------------------

function showBanner(message) {
  const banner = document.getElementById('globalBanner');
  const msg = document.getElementById('bannerMessage');
  msg.textContent = message;
  banner.classList.remove('hidden');
}

document.getElementById('closeBannerBtn').addEventListener('click', () => {
  document.getElementById('globalBanner').classList.add('hidden');
});

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let iconName = 'info';
  if (type === 'success') iconName = 'check-circle-2';
  if (type === 'error') iconName = 'alert-octagon';

  toast.innerHTML = `<i data-lucide="${iconName}"></i> <span>${message}</span>`;
  container.appendChild(toast);
  initIcons();

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.25s ease';
    setTimeout(() => toast.remove(), 250);
  }, 3500);
}

function showValidationError(errorBoxId, message) {
  const box = document.getElementById(errorBoxId);
  box.textContent = message;
  box.classList.remove('hidden');
}

function clearValidationError(errorBoxId) {
  const box = document.getElementById(errorBoxId);
  box.textContent = '';
  box.classList.add('hidden');
}

// ---------------------------------------------------------------------------
// Action Handlers (API Calls)
// ---------------------------------------------------------------------------

function attachActionHandlers() {
  // Clear buttons
  document.getElementById('clearCornellBtn').addEventListener('click', () => {
    document.getElementById('cornellInput').value = '';
    document.getElementById('cornellInput').dispatchEvent(new Event('input'));
  });

  document.getElementById('clearQuizBtn').addEventListener('click', () => {
    document.getElementById('quizInput').value = '';
    document.getElementById('quizInput').dispatchEvent(new Event('input'));
  });

  document.getElementById('clearPolishBtn').addEventListener('click', () => {
    document.getElementById('polishQuestion').value = '';
    document.getElementById('polishDraft').value = '';
    document.getElementById('polishDraft').dispatchEvent(new Event('input'));
  });

  // Feature 1: Cornell Notes Synthesizer
  document.getElementById('generateCornellBtn').addEventListener('click', handleCornellGenerate);
  document.getElementById('copyCornellBtn').addEventListener('click', handleCornellCopy);
  document.getElementById('downloadCornellBtn').addEventListener('click', handleCornellDownload);

  // Feature 2: Quiz Generator
  document.getElementById('generateQuizBtn').addEventListener('click', handleQuizGenerate);
  document.getElementById('resetQuizBtn').addEventListener('click', resetQuizRunner);
  document.getElementById('retakeBottomBtn').addEventListener('click', resetQuizRunner);

  // Feature 3: Answer Polisher
  document.getElementById('generatePolishBtn').addEventListener('click', handlePolishGenerate);
  document.getElementById('copyPolishedBtn').addEventListener('click', handlePolishCopy);

  // Feature 4: Feynman Explainer
  document.getElementById('generateExplainBtn').addEventListener('click', handleExplainGenerate);
  document.getElementById('copyExplainBtn').addEventListener('click', handleExplainCopy);
}

// ===========================================================================
// FEATURE 1: CORNELL SYNTHESIZER
// ===========================================================================

async function handleCornellGenerate() {
  const input = document.getElementById('cornellInput').value.trim();
  const style = document.getElementById('cornellStyle').value;
  const focus = document.getElementById('cornellFocus').value.trim() || null;

  clearValidationError('cornellValidationError');

  // Defensive validation
  if (input.length < 15) {
    showValidationError('cornellValidationError', 'Please enter study notes with at least 15 characters to synthesize.');
    return;
  }

  // Toggle loading state
  document.getElementById('cornellEmptyState').classList.add('hidden');
  document.getElementById('cornellResultView').classList.add('hidden');
  document.getElementById('cornellLoadingState').classList.remove('hidden');

  try {
    const res = await fetch('/api/summarize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: input,
        style: style,
        focus_topic: focus,
        api_key: state.apiKey || null
      })
    });

    const responseData = await res.json();
    document.getElementById('cornellLoadingState').classList.add('hidden');

    if (!responseData.success) {
      showValidationError('cornellValidationError', responseData.error || 'Failed to synthesize notes.');
      document.getElementById('cornellEmptyState').classList.remove('hidden');
      return;
    }

    if (responseData.metadata && responseData.metadata.notice) {
      showBanner(responseData.metadata.notice);
    }

    renderCornellOutput(responseData.data);
    state.lastCornellData = responseData.data;
    showToast('Cornell Notes generated successfully!', 'success');

  } catch (err) {
    document.getElementById('cornellLoadingState').classList.add('hidden');
    showValidationError('cornellValidationError', `Connection error: ${err.message}`);
    document.getElementById('cornellEmptyState').classList.remove('hidden');
  }
}

function renderCornellOutput(data) {
  document.getElementById('cornellTitle').textContent = data.title || 'Cornell Synthesis';
  document.getElementById('cornellStyleBadge').textContent = (data.style || 'cornell').toUpperCase();

  // Cues list
  const cuesContainer = document.getElementById('cornellCuesList');
  cuesContainer.innerHTML = '';
  (data.cues_and_keywords || []).forEach(cue => {
    const li = document.createElement('li');
    li.textContent = cue;
    cuesContainer.appendChild(li);
  });

  // Notes content with Marked.js
  const notesContainer = document.getElementById('cornellNotesContent');
  if (window.marked) {
    notesContainer.innerHTML = window.marked.parse(data.notes_summary || '');
  } else {
    notesContainer.textContent = data.notes_summary || '';
  }

  // Core Takeaways
  const takeawaysContainer = document.getElementById('cornellTakeawaysList');
  takeawaysContainer.innerHTML = '';
  (data.core_takeaways || []).forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    takeawaysContainer.appendChild(li);
  });

  // Questions & Actions
  const questionsContainer = document.getElementById('cornellQuestionsList');
  questionsContainer.innerHTML = '';
  (data.study_questions || []).forEach(q => {
    const li = document.createElement('li');
    li.textContent = q;
    questionsContainer.appendChild(li);
  });

  const actionsContainer = document.getElementById('cornellActionsList');
  actionsContainer.innerHTML = '';
  (data.action_items || []).forEach(a => {
    const li = document.createElement('li');
    li.textContent = a;
    actionsContainer.appendChild(li);
  });

  document.getElementById('cornellResultView').classList.remove('hidden');
  initIcons();
}

function handleCornellCopy() {
  if (!state.lastCornellData) return;
  const d = state.lastCornellData;
  const md = `# ${d.title}\n\n## Cues & Recall Keywords\n${(d.cues_and_keywords || []).map(c => `- ${c}`).join('\n')}\n\n## Notes Summary\n${d.notes_summary}\n\n## Core Takeaways\n${(d.core_takeaways || []).map(t => `- ${t}`).join('\n')}\n\n## Study Questions\n${(d.study_questions || []).map(q => `- ${q}`).join('\n')}\n\n## Action Items\n${(d.action_items || []).map(a => `- ${a}`).join('\n')}`;
  
  navigator.clipboard.writeText(md).then(() => {
    showToast('Cornell Notes copied to clipboard in Markdown format!', 'success');
  });
}

function handleCornellDownload() {
  if (!state.lastCornellData) return;
  const d = state.lastCornellData;
  const md = `# ${d.title}\n\n## Cues & Recall Keywords\n${(d.cues_and_keywords || []).map(c => `- ${c}`).join('\n')}\n\n## Notes Summary\n${d.notes_summary}\n\n## Core Takeaways\n${(d.core_takeaways || []).map(t => `- ${t}`).join('\n')}\n\n## Study Questions\n${(d.study_questions || []).map(q => `- ${q}`).join('\n')}\n\n## Action Items\n${(d.action_items || []).map(a => `- ${a}`).join('\n')}`;
  
  const blob = new Blob([md], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${(d.title || 'cornell_notes').toLowerCase().replace(/[^a-z0-9]+/g, '_')}.md`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('Downloaded study notes as Markdown file!', 'success');
}

// ===========================================================================
// FEATURE 2: ACTIVE RECALL INTERACTIVE QUIZ
// ===========================================================================

async function handleQuizGenerate() {
  const input = document.getElementById('quizInput').value.trim();
  const numQ = parseInt(document.getElementById('quizCount').value, 10);
  const difficulty = document.getElementById('quizDifficulty').value;
  const qType = document.getElementById('quizType').value;

  clearValidationError('quizValidationError');

  if (input.length < 15) {
    showValidationError('quizValidationError', 'Please enter study notes with at least 15 characters to generate quiz items.');
    return;
  }

  document.getElementById('quizEmptyState').classList.add('hidden');
  document.getElementById('quizRunnerView').classList.add('hidden');
  document.getElementById('quizLoadingState').classList.remove('hidden');

  try {
    const res = await fetch('/api/quiz', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: input,
        num_questions: numQ,
        difficulty: difficulty,
        question_type: qType,
        api_key: state.apiKey || null
      })
    });

    const responseData = await res.json();
    document.getElementById('quizLoadingState').classList.add('hidden');

    if (!responseData.success) {
      showValidationError('quizValidationError', responseData.error || 'Failed to generate quiz.');
      document.getElementById('quizEmptyState').classList.remove('hidden');
      return;
    }

    if (responseData.metadata && responseData.metadata.notice) {
      showBanner(responseData.metadata.notice);
    }

    renderQuizRunner(responseData.data);
    showToast('Active Recall Quiz ready for practice!', 'success');

  } catch (err) {
    document.getElementById('quizLoadingState').classList.add('hidden');
    showValidationError('quizValidationError', `Connection error: ${err.message}`);
    document.getElementById('quizEmptyState').classList.remove('hidden');
  }
}

function renderQuizRunner(data) {
  state.quizState = {
    items: data.questions || [],
    userAnswers: {},
    score: 0,
    total: (data.questions || []).length
  };

  document.getElementById('quizTitle').textContent = data.title || 'Active Recall Assessment';
  document.getElementById('quizDifficultyBadge').textContent = (data.difficulty || 'Medium').toUpperCase();
  document.getElementById('quizQuestionsCountBadge').textContent = `${state.quizState.total} Questions`;

  // Reset live score badge
  const scoreBadge = document.getElementById('quizLiveScoreBadge');
  scoreBadge.classList.remove('hidden');
  document.getElementById('quizScoreCount').textContent = '0';
  document.getElementById('quizTotalCount').textContent = state.quizState.total;

  const stack = document.getElementById('quizQuestionsList');
  stack.innerHTML = '';
  document.getElementById('quizCompleteCard').classList.add('hidden');

  state.quizState.items.forEach((item, index) => {
    const card = createQuestionCard(item, index + 1);
    stack.appendChild(card);
  });

  document.getElementById('quizRunnerView').classList.remove('hidden');
  initIcons();
}

function createQuestionCard(item, questionNumber) {
  const card = document.createElement('div');
  card.className = 'question-card';
  card.id = `q-card-${item.id}`;

  const isMCQ = item.type === 'mcq' && Array.isArray(item.options) && item.options.length > 0;

  let contentHtml = `
    <div class="question-meta">
      <span>Question ${questionNumber} of ${state.quizState.total}</span>
      <span>${isMCQ ? 'Multiple Choice' : 'Active Recall Flashcard'}</span>
    </div>
    <div class="question-text">${item.question}</div>
  `;

  if (isMCQ) {
    contentHtml += `<div class="mcq-options-grid" id="options-${item.id}">`;
    item.options.forEach((opt, optIdx) => {
      contentHtml += `
        <button class="option-btn" data-qid="${item.id}" data-opt="${encodeURIComponent(opt)}">
          ${opt}
        </button>
      `;
    });
    contentHtml += `</div>`;
  } else {
    // Flashcard format
    contentHtml += `
      <button class="btn btn-sm btn-outline" id="reveal-fc-${item.id}">
        <i data-lucide="eye"></i> Reveal Flashcard Answer
      </button>
      <div class="flashcard-answer-box hidden" id="fc-box-${item.id}">
        <h5>Target Answer:</h5>
        <p>${item.correct_answer}</p>
      </div>
    `;
  }

  // Hint toggle
  if (item.hint) {
    contentHtml += `
      <div>
        <button class="hint-toggle-btn" id="hint-btn-${item.id}">
          <i data-lucide="help-circle"></i> Need a hint?
        </button>
        <div class="hint-box hidden" id="hint-box-${item.id}">
          💡 ${item.hint}
        </div>
      </div>
    `;
  }

  // Explanation container (revealed after answer)
  contentHtml += `
    <div class="explanation-box hidden" id="explain-box-${item.id}">
      <strong>Pedagogical Explanation:</strong> ${item.explanation}
    </div>
  `;

  card.innerHTML = contentHtml;

  // Event Listeners for MCQ
  if (isMCQ) {
    card.querySelectorAll('.option-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        handleMcqOptionClick(item, decodeURIComponent(btn.getAttribute('data-opt')), card);
      });
    });
  } else {
    const revealBtn = card.querySelector(`#reveal-fc-${item.id}`);
    const fcBox = card.querySelector(`#fc-box-${item.id}`);
    const expBox = card.querySelector(`#explain-box-${item.id}`);
    revealBtn.addEventListener('click', () => {
      fcBox.classList.remove('hidden');
      expBox.classList.remove('hidden');
      revealBtn.disabled = true;
      revealBtn.innerHTML = '<i data-lucide="check"></i> Revealed';
      initIcons();
      recordAnswer(item.id, true);
    });
  }

  // Hint listener
  if (item.hint) {
    const hintBtn = card.querySelector(`#hint-btn-${item.id}`);
    const hintBox = card.querySelector(`#hint-box-${item.id}`);
    hintBtn.addEventListener('click', () => {
      hintBox.classList.toggle('hidden');
    });
  }

  return card;
}

function handleMcqOptionClick(item, selectedOption, card) {
  if (state.quizState.userAnswers[item.id] !== undefined) return; // already answered

  const optionsContainer = card.querySelector(`#options-${item.id}`);
  const explanationBox = card.querySelector(`#explain-box-${item.id}`);
  const allBtns = optionsContainer.querySelectorAll('.option-btn');

  const isCorrect = selectedOption.trim().toLowerCase() === item.correct_answer.trim().toLowerCase() ||
                    selectedOption.trim().startsWith(item.correct_answer.trim().substring(0, 2));

  allBtns.forEach(btn => {
    btn.disabled = true;
    const optVal = decodeURIComponent(btn.getAttribute('data-opt')).trim();
    if (optVal.toLowerCase() === item.correct_answer.trim().toLowerCase() ||
        optVal.startsWith(item.correct_answer.trim().substring(0, 2))) {
      btn.classList.add('selected-correct');
    }
  });

  if (isCorrect) {
    card.classList.add('answered-correct');
    showToast('Correct! Great active recall.', 'success');
  } else {
    card.classList.add('answered-wrong');
    // Highlight wrong selection
    allBtns.forEach(btn => {
      if (decodeURIComponent(btn.getAttribute('data-opt')).trim() === selectedOption.trim()) {
        btn.classList.add('selected-wrong');
      }
    });
    showToast('Not quite. Review the explanation.', 'info');
  }

  explanationBox.classList.remove('hidden');
  recordAnswer(item.id, isCorrect);
}

function recordAnswer(itemId, isCorrect) {
  state.quizState.userAnswers[itemId] = isCorrect;
  if (isCorrect) {
    state.quizState.score += 1;
  }

  document.getElementById('quizScoreCount').textContent = state.quizState.score;

  // Check if all answered
  const answeredCount = Object.keys(state.quizState.userAnswers).length;
  if (answeredCount === state.quizState.total) {
    const completeCard = document.getElementById('quizCompleteCard');
    const msg = document.getElementById('quizFinalMessage');
    const text = document.getElementById('quizFinalScoreText');

    const pct = Math.round((state.quizState.score / state.quizState.total) * 100);
    if (pct === 100) {
      msg.textContent = '🎉 Perfect Mastery!';
    } else if (pct >= 70) {
      msg.textContent = '👏 Great Active Recall!';
    } else {
      msg.textContent = '📚 Study Revision Recommended';
    }

    text.textContent = `You scored ${state.quizState.score} out of ${state.quizState.total} (${pct}%).`;
    completeCard.classList.remove('hidden');
    initIcons();
  }
}

function resetQuizRunner() {
  if (state.quizState.items.length === 0) return;
  renderQuizRunner({
    title: document.getElementById('quizTitle').textContent,
    difficulty: document.getElementById('quizDifficultyBadge').textContent,
    questions: state.quizState.items
  });
}

// ===========================================================================
// FEATURE 3: ANSWER POLISHER & RUBRIC GRADER
// ===========================================================================

async function handlePolishGenerate() {
  const question = document.getElementById('polishQuestion').value.trim();
  const draft = document.getElementById('polishDraft').value.trim();
  const level = document.getElementById('polishLevel').value;

  clearValidationError('polishValidationError');

  if (question.length < 5) {
    showValidationError('polishValidationError', 'Please enter the exam or assignment question (at least 5 characters).');
    return;
  }
  if (draft.length < 10) {
    showValidationError('polishValidationError', 'Please provide a draft answer of at least 10 characters to evaluate.');
    return;
  }

  document.getElementById('polishEmptyState').classList.add('hidden');
  document.getElementById('polishResultView').classList.add('hidden');
  document.getElementById('polishLoadingState').classList.remove('hidden');

  try {
    const res = await fetch('/api/polish', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question,
        student_draft: draft,
        target_level: level,
        api_key: state.apiKey || null
      })
    });

    const responseData = await res.json();
    document.getElementById('polishLoadingState').classList.add('hidden');

    if (!responseData.success) {
      showValidationError('polishValidationError', responseData.error || 'Evaluation failed.');
      document.getElementById('polishEmptyState').classList.remove('hidden');
      return;
    }

    if (responseData.metadata && responseData.metadata.notice) {
      showBanner(responseData.metadata.notice);
    }

    renderPolishOutput(responseData.data);
    state.lastPolishedData = responseData.data;
    showToast('Answer evaluated and polished!', 'success');

  } catch (err) {
    document.getElementById('polishLoadingState').classList.add('hidden');
    showValidationError('polishValidationError', `Connection error: ${err.message}`);
    document.getElementById('polishEmptyState').classList.remove('hidden');
  }
}

function renderPolishOutput(data) {
  document.getElementById('polishScoreNum').textContent = data.original_score;
  
  const rubric = data.rubric_evaluation || {};
  document.getElementById('rubricAccuracy').textContent = rubric.conceptual_accuracy || 'Evaluated.';
  document.getElementById('rubricStructure').textContent = rubric.structure_flow || 'Evaluated.';
  document.getElementById('rubricTone').textContent = rubric.academic_tone || 'Evaluated.';
  document.getElementById('rubricEvidence').textContent = rubric.evidence_reasoning || 'Evaluated.';

  // Strengths & Weaknesses
  const strengthsList = document.getElementById('polishStrengthsList');
  strengthsList.innerHTML = '';
  (data.strengths || []).forEach(s => {
    const li = document.createElement('li');
    li.textContent = s;
    strengthsList.appendChild(li);
  });

  const weaknessesList = document.getElementById('polishWeaknessesList');
  weaknessesList.innerHTML = '';
  (data.weaknesses || []).forEach(w => {
    const li = document.createElement('li');
    li.textContent = w;
    weaknessesList.appendChild(li);
  });

  // Polished Model
  document.getElementById('polishModelText').textContent = data.polished_version || '';

  // Improvements
  const improvementsList = document.getElementById('polishImprovementsList');
  improvementsList.innerHTML = '';
  (data.key_improvements_made || []).forEach(imp => {
    const li = document.createElement('li');
    li.textContent = imp;
    improvementsList.appendChild(li);
  });

  document.getElementById('polishResultView').classList.remove('hidden');
  initIcons();
}

function handlePolishCopy() {
  if (!state.lastPolishedData) return;
  navigator.clipboard.writeText(state.lastPolishedData.polished_version).then(() => {
    showToast('Polished model answer copied to clipboard!', 'success');
  });
}

// ===========================================================================
// FEATURE 4: FEYNMAN CONCEPT EXPLAINER
// ===========================================================================

async function handleExplainGenerate() {
  const concept = document.getElementById('explainConcept').value.trim();
  const domain = document.getElementById('explainDomain').value.trim() || null;
  const level = document.querySelector('input[name="cognitiveLevel"]:checked').value;

  clearValidationError('explainValidationError');

  if (concept.length < 2) {
    showValidationError('explainValidationError', 'Please enter a concept name (at least 2 characters).');
    return;
  }

  document.getElementById('explainEmptyState').classList.add('hidden');
  document.getElementById('explainResultView').classList.add('hidden');
  document.getElementById('explainLoadingState').classList.remove('hidden');

  try {
    const res = await fetch('/api/explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        concept: concept,
        cognitive_level: level,
        subject_domain: domain,
        api_key: state.apiKey || null
      })
    });

    const responseData = await res.json();
    document.getElementById('explainLoadingState').classList.add('hidden');

    if (!responseData.success) {
      showValidationError('explainValidationError', responseData.error || 'Explanation failed.');
      document.getElementById('explainEmptyState').classList.remove('hidden');
      return;
    }

    if (responseData.metadata && responseData.metadata.notice) {
      showBanner(responseData.metadata.notice);
    }

    renderExplainOutput(responseData.data);
    state.lastExplainData = responseData.data;
    showToast(`Explained '${concept}' with Feynman technique!`, 'success');

  } catch (err) {
    document.getElementById('explainLoadingState').classList.add('hidden');
    showValidationError('explainValidationError', `Connection error: ${err.message}`);
    document.getElementById('explainEmptyState').classList.remove('hidden');
  }
}

function renderExplainOutput(data) {
  document.getElementById('explainConceptTitle').textContent = data.concept;
  document.getElementById('explainLevelBadge').textContent = (data.level || '').toUpperCase();
  document.getElementById('explainAnalogyText').textContent = data.intuitive_analogy || '';

  const coreContent = document.getElementById('explainCoreContent');
  if (window.marked) {
    coreContent.innerHTML = window.marked.parse(data.core_explanation || '');
  } else {
    coreContent.textContent = data.core_explanation || '';
  }

  const miscList = document.getElementById('explainMisconceptionsList');
  miscList.innerHTML = '';
  (data.common_misconceptions || []).forEach(m => {
    const li = document.createElement('li');
    li.textContent = m;
    miscList.appendChild(li);
  });

  document.getElementById('explainMnemonicText').textContent = data.memory_hook_or_mnemonic || '';
  document.getElementById('explainChallengeText').textContent = data.self_test_challenge || '';

  document.getElementById('explainResultView').classList.remove('hidden');
  initIcons();
}

function handleExplainCopy() {
  if (!state.lastExplainData) return;
  const d = state.lastExplainData;
  const text = `# Concept Mastery: ${d.concept}\n\n## Mental Model & Analogy\n${d.intuitive_analogy}\n\n## Core Explanation\n${d.core_explanation}\n\n## Common Misconceptions\n${(d.common_misconceptions || []).map(m => `- ${m}`).join('\n')}\n\n## Memory Hook / Mnemonic\n${d.memory_hook_or_mnemonic}\n\n## Self-Test Challenge\n${d.self_test_challenge}`;
  
  navigator.clipboard.writeText(text).then(() => {
    showToast('Explanation copied to clipboard in Markdown format!', 'success');
  });
}
