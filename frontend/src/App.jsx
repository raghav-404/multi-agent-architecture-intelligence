import { useEffect, useMemo, useRef, useState } from "react";
import DOMPurify from "dompurify";
import { marked } from "marked";
import {
  AlignLeft, Archive, ArrowRight, Bot, Check, ChevronDown, Clipboard,
  Database, Download, FileText, FlaskConical, LayoutDashboard, LoaderCircle,
  LogOut, Menu, Network, Pencil, Plus, Search, ShieldCheck, Sparkles,
  TestTube2, TriangleAlert, UserRound, X
} from "lucide-react";

const SECTIONS = [
  { name: "clarification", label: "Clarification", role: "Requirement discovery", icon: Search },
  { name: "requirements", label: "Requirements", role: "Requirement agent", icon: AlignLeft },
  { name: "conflicts", label: "Conflicts", role: "Deterministic rule engine", icon: TriangleAlert },
  { name: "plan", label: "Project plan", role: "Planning agent", icon: LayoutDashboard },
  { name: "architecture", label: "Architecture", role: "Architecture agent", icon: Network },
  { name: "evaluation", label: "Evaluation", role: "Deterministic Python engine", icon: FlaskConical },
  { name: "database", label: "Database", role: "Database agent", icon: Database },
  { name: "novelty", label: "Novelty", role: "Novelty agent", icon: Sparkles },
  { name: "traceability", label: "Traceability", role: "Traceability agent", icon: ShieldCheck },
  { name: "testing", label: "Testing", role: "Testing agent", icon: TestTube2 },
  { name: "consistency", label: "Consistency", role: "Cross-agent validator", icon: ShieldCheck },
  { name: "review", label: "Review", role: "Reviewer agent", icon: Check },
  { name: "feedback", label: "Feedback", role: "Feedback loop", icon: Bot },
  { name: "report", label: "Full report", role: "Combined agent output", icon: FileText }
];

const PROGRESS = [
  "Clarifying assumptions", "Structuring requirements", "Checking requirement conflicts", "Building the project plan",
  "Comparing architecture options", "Scoring architecture options", "Designing the data model", "Finding novelty and risks",
  "Building traceability", "Creating the test plan", "Validating artifact consistency", "Reviewing the report", "Preparing feedback"
];

marked.setOptions({ gfm: true, breaks: true });
let mermaidReady;

function getMermaid() {
  if (!mermaidReady) {
    mermaidReady = import("mermaid").then(({ default: mermaid }) => {
      mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "base" });
      return mermaid;
    });
  }
  return mermaidReady;
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail || "Something went wrong.");
  return data;
}

function composeReport(result, project) {
  if (!Object.keys(result).some(key => key !== "report" && result[key])) return result.report || "";
  const headings = { review: "Reviewer Notes", feedback: "Feedback Loop", testing: "Test Plan" };
  const body = SECTIONS.slice(0, -1)
    .filter(section => result[section.name])
    .map(section => `## ${headings[section.name] || section.label}\n${result[section.name]}`);
  return [`# Architecture Intelligence Report\n\n## Project\n${project}`, ...body].join("\n\n");
}

function Markdown({ text }) {
  const ref = useRef(null);
  const html = useMemo(() => DOMPurify.sanitize(marked.parse(text || "")), [text]);

  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    const diagrams = [...root.querySelectorAll("pre code.language-mermaid")].map(code => {
      const chart = document.createElement("div");
      chart.className = "mermaid";
      chart.textContent = code.textContent;
      code.parentElement.replaceWith(chart);
      return chart;
    });
    if (diagrams.length) getMermaid()
      .then(mermaid => mermaid.run({ nodes: diagrams }))
      .catch(() => diagrams.forEach(chart => chart.classList.add("diagram-error")));
  }, [html]);

  return <article ref={ref} className="report-content" dangerouslySetInnerHTML={{ __html: html }} />;
}

function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const data = await api(`/${mode}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      onAuthenticated(data.username);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-brand">
        <div className="brand-lockup large"><span>M</span><div><strong>MARIS</strong><small>Architecture Intelligence</small></div></div>
        <div className="auth-visual" aria-hidden="true">
          <div><Search /><span>Clarify</span></div><i />
          <div><Network /><span>Design</span></div><i />
          <div><ShieldCheck /><span>Review</span></div>
        </div>
        <p>Turn a software idea into a structured engineering report.</p>
      </section>
      <section className="auth-panel">
        <form className="auth-form" onSubmit={submit}>
          <div className="auth-heading">
            <span className="icon-tile"><UserRound size={20} /></span>
            <div><h1>{mode === "login" ? "Welcome back" : "Create your workspace"}</h1><p>Use your MARIS account to continue.</p></div>
          </div>
          <div className="auth-tabs" role="tablist">
            <button type="button" className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Sign in</button>
            <button type="button" className={mode === "register" ? "active" : ""} onClick={() => setMode("register")}>Create account</button>
          </div>
          <label>Username<input value={username} onChange={e => setUsername(e.target.value)} autoComplete="username" placeholder="raghav_404" required /></label>
          <label>Password<input value={password} onChange={e => setPassword(e.target.value)} type="password" autoComplete={mode === "login" ? "current-password" : "new-password"} placeholder="At least 6 characters" required /></label>
          {error && <div className="inline-error" role="alert">{error}</div>}
          <button className="button primary wide" disabled={busy}>
            {busy ? <LoaderCircle className="spin" size={17} /> : <ArrowRight size={17} />}
            {mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>
      </section>
    </main>
  );
}

function Sidebar({ open, onClose, history, onHistory, onNew, hasReport }) {
  return (
    <>
      <div className={`sidebar-scrim ${open ? "show" : ""}`} onClick={onClose} />
      <aside className={`app-sidebar ${open ? "open" : ""}`}>
        <div className="sidebar-mobile-head"><strong>Workspace</strong><button className="icon-button" onClick={onClose} aria-label="Close navigation"><X size={18} /></button></div>
        <nav className="primary-nav">
          <button className={!hasReport ? "active" : ""} onClick={onNew}><LayoutDashboard size={17} />Workspace</button>
          <button onClick={onNew}><Plus size={17} />New analysis</button>
        </nav>
        <div className="nav-heading"><span>Recent reports</span><span>{history.length}</span></div>
        <div className="history-list">
          {history.length === 0 && <div className="history-empty"><Archive size={18} /><span>No reports yet</span></div>}
          {history.slice(-8).reverse().map((item, index) => (
            <button key={`${item.project}-${index}`} onClick={() => onHistory(item)}>
              <span className="history-icon"><FileText size={15} /></span>
              <span><strong>{item.project}</strong><small>Saved report</small></span>
            </button>
          ))}
        </div>
        <div className="sidebar-foot"><span className="status-dot" />All systems ready</div>
      </aside>
    </>
  );
}

function AgentPipeline({ running, stage }) {
  return (
    <section className="pipeline-panel">
      <div className="panel-title"><div><p className="overline">LangGraph workflow</p><h2>Agent pipeline</h2></div><span>{running ? `${Math.min(stage + 1, PROGRESS.length)}/${PROGRESS.length}` : "Sequential"}</span></div>
      <div className="pipeline-list">
        {SECTIONS.slice(0, -1).map((agent, index) => {
          const Icon = agent.icon;
          const state = running ? (index < stage ? "done" : index === stage ? "active" : "waiting") : "ready";
          return <div className={`pipeline-row ${state}`} key={agent.name}>
            <span className="agent-icon"><Icon size={16} /></span>
            <span><strong>{agent.label}</strong><small>{state === "done" ? "Completed" : state === "active" ? "Working now" : agent.role}</small></span>
            <span className="pipeline-state">{state === "done" ? <Check size={14} /> : index + 1}</span>
          </div>;
        })}
      </div>
    </section>
  );
}

function ProjectComposer({ form, setForm, onGenerate, running, stage, error }) {
  const update = (key, value) => setForm(current => ({ ...current, [key]: value }));
  return (
    <div className="dashboard-grid">
      <section className="composer-panel">
        <div className="page-heading"><p className="overline">New analysis</p><h1>What are you building?</h1><p>Start with the product idea and add the constraints that matter.</p></div>
        <form onSubmit={onGenerate}>
          <label className="field-label" htmlFor="project">Project brief</label>
          <div className="textarea-wrap">
            <textarea id="project" value={form.project} onChange={e => update("project", e.target.value)} maxLength={1000} rows={8} placeholder="Build an online food delivery platform for customers, restaurants, and delivery partners..." disabled={running} />
            <span>{form.project.length}/1000</span>
          </div>
          <div className="form-grid">
            <label className="field-label">Project type
              <span className="select-wrap"><select value={form.project_type} onChange={e => update("project_type", e.target.value)} disabled={running}><option>General</option><option>Web App</option><option>Mobile App</option><option>AI App</option><option>E-commerce</option></select><ChevronDown size={15} /></span>
            </label>
            <fieldset><legend className="field-label">Report depth</legend><div className="segmented">{["Short", "Medium", "Detailed"].map(value => <button type="button" className={form.depth === value ? "active" : ""} onClick={() => update("depth", value)} key={value} disabled={running}>{value}</button>)}</div></fieldset>
          </div>
          <details className="context-input">
            <summary>Rubric or constraints <span>Optional</span></summary>
            <textarea value={form.context} onChange={e => update("context", e.target.value)} rows={4} placeholder="Paste evaluation criteria, technical constraints, or professor feedback..." disabled={running} />
          </details>
          {error && <div className="inline-error" role="alert">{error}</div>}
          <div className="composer-actions">
            <button className="button primary" disabled={running}>{running ? <LoaderCircle className="spin" size={17} /> : <Sparkles size={17} />}{running ? PROGRESS[Math.min(stage, 9)] : "Generate architecture report"}</button>
            {!form.project && <button type="button" className="text-action" onClick={() => setForm({ project: "Build an online food delivery system for customers, restaurants, and delivery partners.", project_type: "Web App", depth: "Medium", context: "" })}>Use example</button>}
          </div>
        </form>
      </section>
      <AgentPipeline running={running} stage={stage} />
    </div>
  );
}

function ReportWorkspace({ project, metadata, result, setResult, onToast }) {
  const [active, setActive] = useState("report");
  const [draft, setDraft] = useState(() => composeReport(result, project));
  const [editing, setEditing] = useState(false);
  const [refinement, setRefinement] = useState("");
  const [refining, setRefining] = useState(false);

  const available = SECTIONS.filter(section => section.name === "report" || result[section.name]);
  const section = SECTIONS.find(item => item.name === active);
  const words = draft.trim() ? draft.trim().split(/\s+/).length : 0;
  const score = (result.review || result.report || "").match(/(\d+(?:\.\d+)?)\s*\/\s*10/);

  function saveCurrent() {
    const next = { ...result, [active]: draft };
    setResult(next);
    return next;
  }

  function selectSection(name) {
    const next = saveCurrent();
    setActive(name);
    setDraft(name === "report" ? composeReport(next, project) : next[name] || "");
    setEditing(false);
    setRefinement("");
  }

  function fullReport() {
    const next = saveCurrent();
    return active === "report" ? draft : composeReport(next, project);
  }

  function download(name, data, type) {
    const blob = data instanceof Blob ? data : new Blob([data], { type });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = name;
    link.click();
    URL.revokeObjectURL(link.href);
  }

  async function copyReport() {
    await navigator.clipboard.writeText(fullReport());
    onToast("Report copied to clipboard");
  }

  async function downloadPdf() {
    try {
      const response = await fetch("/pdf", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ report: fullReport() }) });
      if (!response.ok) throw new Error();
      download("architecture-report.pdf", await response.blob(), "application/pdf");
    } catch {
      onToast("PDF generation failed");
    }
  }

  async function refine(event) {
    event.preventDefault();
    if (refinement.trim().length < 3) return;
    setRefining(true);
    try {
      const data = await api("/refine", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project, section: section.label, current_text: draft, instruction: refinement }) });
      setDraft(data.text);
      setResult(current => ({ ...current, [active]: data.text }));
      setRefinement("");
      onToast(`${section.label} updated`);
    } catch (err) {
      onToast(err.message);
    } finally {
      setRefining(false);
    }
  }

  return (
    <div className="report-workspace">
      <header className="report-header">
        <div><p className="overline">Architecture report</p><h1>{project}</h1><div className="metadata"><span>{metadata.type}</span><span>{metadata.depth} depth</span>{score && <span className="score">Score {score[1]}/10</span>}</div></div>
        <div className="report-actions">
          <button className="button secondary" onClick={copyReport} title="Copy report"><Clipboard size={16} />Copy</button>
          <button className="button secondary" onClick={() => download("architecture-report.md", fullReport(), "text/markdown")} title="Download Markdown"><Download size={16} />Markdown</button>
          <button className="button primary" onClick={downloadPdf} title="Download PDF"><Download size={16} />PDF</button>
        </div>
      </header>
      <div className="report-layout">
        <nav className="section-nav" aria-label="Report sections">
          <p>Report sections</p>
          {available.map(item => { const Icon = item.icon; return <button className={active === item.name ? "active" : ""} onClick={() => selectSection(item.name)} key={item.name}><Icon size={16} /><span>{item.label}</span>{active === item.name && <ArrowRight size={14} />}</button>; })}
        </nav>
        <section className="document-panel">
          <div className="document-head">
            <div><strong>{section.label}</strong><span>{section.role}</span></div>
            <div className="document-tools"><span>{words.toLocaleString()} words</span>{active !== "report" && <div className="segmented compact"><button className={!editing ? "active" : ""} onClick={() => setEditing(false)}><FileText size={14} />Preview</button><button className={editing ? "active" : ""} onClick={() => setEditing(true)}><Pencil size={14} />Edit</button></div>}</div>
          </div>
          {active !== "report" && <form className="refine-form" onSubmit={refine}><Sparkles size={16} /><input value={refinement} onChange={e => setRefinement(e.target.value)} maxLength={600} placeholder={`Ask the ${section.label.toLowerCase()} agent to revise this section...`} /><button className="button secondary" disabled={refining}>{refining ? <LoaderCircle className="spin" size={15} /> : <ArrowRight size={15} />}Update</button></form>}
          {editing ? <textarea className="report-editor" value={draft} onChange={e => { setDraft(e.target.value); setResult(current => ({ ...current, [active]: e.target.value })); }} aria-label={`Edit ${section.label}`} /> : <Markdown text={draft} />}
        </section>
      </div>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState(undefined);
  const [history, setHistory] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [form, setForm] = useState({ project: "", project_type: "General", depth: "Medium", context: "" });
  const [result, setResult] = useState(null);
  const [metadata, setMetadata] = useState({ type: "General", depth: "Medium" });
  const [running, setRunning] = useState(false);
  const [stage, setStage] = useState(0);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");
  const [workspaceVersion, setWorkspaceVersion] = useState(0);

  useEffect(() => { api("/me").then(data => setUser(data.username || null)).catch(() => setUser(null)); }, []);
  useEffect(() => {
    if (!user) return;
    api("/history").then(setHistory).catch(() => setHistory([]));
  }, [user]);
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => setStage(value => Math.min(value + 1, PROGRESS.length - 1)), 2200);
    return () => clearInterval(timer);
  }, [running]);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 2400);
    return () => clearTimeout(timer);
  }, [toast]);

  async function generate(event) {
    event.preventDefault();
    if (form.project.trim().length < 5) return setError("Describe the project in at least 5 characters.");
    setError(""); setRunning(true); setStage(0);
    try {
      const data = await api("/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      setResult(data);
      setWorkspaceVersion(value => value + 1);
      setMetadata({ type: form.project_type, depth: form.depth });
      setToast("Architecture report completed");
      api("/history").then(setHistory).catch(() => {});
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  }

  function newAnalysis() {
    setResult(null); setError(""); setSidebarOpen(false);
  }

  function openHistory(item) {
    setForm(current => ({ ...current, project: item.project }));
    setResult({ report: item.report });
    setWorkspaceVersion(value => value + 1);
    setMetadata({ type: "Saved report", depth: "History" });
    setSidebarOpen(false);
  }

  async function logout() {
    await fetch("/logout", { method: "POST" });
    setUser(null); setResult(null); setHistory([]);
  }

  if (user === undefined) return <div className="app-loading"><div className="brand-mark">M</div><LoaderCircle className="spin" /></div>;
  if (!user) return <AuthScreen onAuthenticated={setUser} />;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-left"><button className="icon-button mobile-menu" onClick={() => setSidebarOpen(true)} aria-label="Open navigation"><Menu size={19} /></button><div className="brand-lockup"><span>M</span><div><strong>MARIS</strong><small>Architecture Intelligence</small></div></div></div>
        <div className="topbar-right"><span className="phase"><i />Phase 2</span><span className="user-chip"><UserRound size={15} />{user}</span><button className="icon-button" onClick={logout} title="Log out" aria-label="Log out"><LogOut size={17} /></button></div>
      </header>
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} history={history} onHistory={openHistory} onNew={newAnalysis} hasReport={Boolean(result)} />
      <main className="app-main">
        {result ? <ReportWorkspace key={workspaceVersion} project={form.project} metadata={metadata} result={result} setResult={setResult} onToast={setToast} /> : <ProjectComposer form={form} setForm={setForm} onGenerate={generate} running={running} stage={stage} error={error} />}
      </main>
      <div className={`toast ${toast ? "show" : ""}`}><Check size={15} />{toast}</div>
    </div>
  );
}
