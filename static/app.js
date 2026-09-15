const sections = [
  { name: "clarification", label: "Clarification", short: "CL", role: "Requirement discovery" },
  { name: "requirements", label: "Requirements", short: "RQ", role: "Requirement agent" },
  { name: "plan", label: "Plan", short: "PL", role: "Planner agent" },
  { name: "architecture", label: "Architecture", short: "AR", role: "Architecture agent" },
  { name: "database", label: "Database", short: "DB", role: "Database agent" },
  { name: "novelty", label: "Novelty", short: "NV", role: "Novelty agent" },
  { name: "traceability", label: "Traceability", short: "TR", role: "Traceability agent" },
  { name: "testing", label: "Testing", short: "TS", role: "Testing agent" },
  { name: "review", label: "Review", short: "RV", role: "Reviewer agent" },
  { name: "feedback", label: "Feedback", short: "FB", role: "Feedback loop" },
  { name: "report", label: "Full Report", short: "RP", role: "Combined agent output" }
];

const progressMessages = [
  "Clarifying assumptions and missing details",
  "Structuring functional and quality requirements",
  "Building milestones and sprint plan",
  "Comparing architecture options",
  "Designing tables and relationships",
  "Finding project novelty and risks",
  "Mapping requirements to design and tests",
  "Creating a project-specific test plan",
  "Reviewing the complete engineering report",
  "Turning reviewer notes into improvements"
];

let result = {};
let active = "report";
let customReport = false;
let progressTimer;
let mermaidReady = false;

const $ = id => document.getElementById(id);
const escapeHtml = text => String(text || "")
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

function renderMarkdown(text) {
  const safeText = escapeHtml(text);
  if (window.marked) return marked.parse(safeText, { breaks: true, gfm: true });
  return safeText
    .replace(/^### (.*)$/gm, "<h3>$1</h3>")
    .replace(/^## (.*)$/gm, "<h2>$1</h2>")
    .replace(/^# (.*)$/gm, "<h1>$1</h1>")
    .replace(/^[-*] (.*)$/gm, "<li>$1</li>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

async function renderMermaid() {
  if (!window.mermaid) return;
  const codes = $("preview").querySelectorAll("pre code.language-mermaid");
  if (!codes.length) return;
  if (!mermaidReady) {
    mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "base" });
    mermaidReady = true;
  }
  codes.forEach(code => {
    const chart = document.createElement("div");
    chart.className = "mermaid";
    chart.textContent = code.textContent;
    code.parentElement.replaceWith(chart);
  });
  try {
    await mermaid.run({ nodes: $("preview").querySelectorAll(".mermaid") });
  } catch (error) {
    $("preview").querySelectorAll(".mermaid").forEach(chart => {
      if (!chart.querySelector("svg")) chart.classList.add("diagram-error");
    });
  }
}

function saveActive() {
  if (!$("workspace").classList.contains("hidden")) result[active] = $("editor").value;
}

function composeReport() {
  if (customReport && result.report) return result.report;
  const available = sections.slice(0, -1).filter(section => result[section.name]);
  if (!available.length) return result.report || "";

  const title = "# Architecture Intelligence Report\n\n## Project\n" + $("project").value.trim();
  const body = available.map(section => {
    const headings = { review: "Reviewer Notes", feedback: "Feedback Loop", testing: "Test Plan" };
    return `## ${headings[section.name] || section.label}\n${result[section.name]}`;
  });
  return [title, ...body].join("\n\n");
}

function updateDocument() {
  const text = $("editor").value;
  $("preview").innerHTML = renderMarkdown(text);
  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  $("wordCount").textContent = `${words.toLocaleString()} words`;
  renderMermaid();
}

function showTab(name) {
  saveActive();
  active = name;
  const section = sections.find(item => item.name === name);
  $("editor").value = name === "report" ? composeReport() : (result[name] || "");
  $("sectionTitle").textContent = section.label;
  $("sectionRole").textContent = section.role;
  $("refineForm").classList.toggle("hidden", name === "report");
  document.querySelectorAll(".agent-tab").forEach(button => {
    const selected = button.dataset.name === name;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-selected", selected);
  });
  updateDocument();
}

function drawTabs() {
  const available = sections.filter(section => section.name === "report" || result[section.name]);
  $("tabs").innerHTML = "";
  available.forEach(section => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "agent-tab";
    button.dataset.name = section.name;
    button.setAttribute("role", "tab");
    button.innerHTML = `<span>${section.short}</span><span><strong>${section.label}</strong>` +
      `<small>${section.name === "report" ? "Complete" : "Agent output"}</small></span>`;
    button.onclick = () => showTab(section.name);
    $("tabs").appendChild(button);
  });
  showTab("report");
}

function setView(mode) {
  const editing = mode === "edit";
  $("editor").classList.toggle("hidden", !editing);
  $("preview").classList.toggle("hidden", editing);
  $("editMode").classList.toggle("active", editing);
  $("previewMode").classList.toggle("active", !editing);
  $("editMode").setAttribute("aria-pressed", editing);
  $("previewMode").setAttribute("aria-pressed", !editing);
  if (editing) $("editor").focus();
}

function renderProgress(current) {
  $("agentProgress").innerHTML = sections.slice(0, -1).map((section, index) => {
    const state = index < current ? "done" : index === current ? "active" : "pending";
    const note = state === "done" ? "Completed" : state === "active" ? "Working now" : "Waiting";
    return `<div class="progress-item ${state}"><span class="progress-icon">${section.short}</span>` +
      `<span><strong>${section.label}</strong><small>${note}</small></span><i class="progress-dot"></i></div>`;
  }).join("");
  if (current < progressMessages.length) $("runningTitle").textContent = progressMessages[current];
}

function startProgress() {
  let current = 0;
  renderProgress(current);
  progressTimer = setInterval(() => {
    if (current < progressMessages.length - 1) renderProgress(++current);
  }, 2200);
}

function setLoading(loading) {
  $("generate").disabled = loading;
  $("clear").disabled = loading;
  $("generate").innerHTML = loading
    ? "Generating..." : '<span aria-hidden="true">&#10022;</span> Generate report';
}

function showError(message) {
  $("status").textContent = message;
  $("status").classList.add("visible");
}

function clearError() {
  $("status").textContent = "";
  $("status").classList.remove("visible");
}

function showToast(message) {
  $("toast").textContent = message;
  $("toast").classList.add("show");
  setTimeout(() => $("toast").classList.remove("show"), 2200);
}

function showWorkspace(project, fromHistory = false) {
  $("emptyState").classList.add("hidden");
  $("runningState").classList.add("hidden");
  $("workspace").classList.remove("hidden");
  $("reportTitle").textContent = project || "Architecture Intelligence Report";
  $("reportType").textContent = fromHistory ? "Saved report" : $("projectType").value;
  $("reportDepth").textContent = fromHistory ? "History" : `${$("depth").value} depth`;
  const score = (result.review || result.report || "").match(/(\d+(?:\.\d+)?)\s*\/\s*10/);
  $("reportScore").classList.toggle("hidden", !score);
  if (score) $("reportScore").textContent = `Score ${score[1]}/10`;
  drawTabs();
  setView("preview");
}

async function loadHistory() {
  try {
    const response = await fetch("/history");
    if (!response.ok) throw new Error();
    const history = await response.json();
    $("historyCount").textContent = history.length;
    $("history").innerHTML = history.length ? "" : '<p class="muted">No reports yet.</p>';
    history.slice(-5).reverse().forEach(item => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "history-item";
      const title = escapeHtml(item.project || "Untitled project");
      button.innerHTML = `<span>RP</span><span><strong>${title}</strong><small>Open saved report</small></span>`;
      button.onclick = () => {
        result = { report: item.report || "" };
        active = "report";
        customReport = true;
        $("project").value = item.project || "";
        updateCharacterCount();
        showWorkspace(item.project, true);
      };
      $("history").appendChild(button);
    });
  } catch (error) {
    $("history").innerHTML = '<p class="muted">History is unavailable.</p>';
  }
}

async function analyze(event) {
  event.preventDefault();
  const project = $("project").value.trim();
  if (project.length < 5) return showError("Please describe your project in at least 5 characters.");

  clearError();
  setLoading(true);
  $("emptyState").classList.add("hidden");
  $("workspace").classList.add("hidden");
  $("runningState").classList.remove("hidden");
  startProgress();

  try {
    const response = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project,
        project_type: $("projectType").value,
        depth: $("depth").value,
        context: $("context").value
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "The report could not be generated.");
    result = data;
    active = "report";
    customReport = false;
    clearInterval(progressTimer);
    renderProgress(progressMessages.length);
    showWorkspace(project);
    showToast("All agents completed the report.");
    loadHistory();
  } catch (error) {
    clearInterval(progressTimer);
    $("runningState").classList.add("hidden");
    $("emptyState").classList.remove("hidden");
    showError(error.message);
  } finally {
    setLoading(false);
  }
}

async function refineSection(event) {
  event.preventDefault();
  const instruction = $("refineInput").value.trim();
  if (instruction.length < 3) return showToast("Describe the change you want in this section.");
  saveActive();
  $("refine").disabled = true;
  $("refine").textContent = "Updating...";
  try {
    const response = await fetch("/refine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        project: $("project").value.trim(),
        section: sections.find(item => item.name === active).label,
        current_text: result[active] || "",
        instruction
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "The section could not be updated.");
    result[active] = data.text;
    customReport = false;
    $("refineInput").value = "";
    showTab(active);
    showToast("Section updated.");
  } catch (error) {
    showToast(error.message);
  } finally {
    $("refine").disabled = false;
    $("refine").textContent = "Update";
  }
}

function resetForm() {
  $("projectForm").reset();
  result = {};
  active = "report";
  customReport = false;
  clearError();
  updateCharacterCount();
  $("workspace").classList.add("hidden");
  $("runningState").classList.add("hidden");
  $("emptyState").classList.remove("hidden");
}

function updateCharacterCount() {
  $("charCount").textContent = `${$("project").value.length} / 1000`;
}

function fullReport() {
  saveActive();
  return composeReport();
}

function download(name, data, type) {
  const blob = data instanceof Blob ? data : new Blob([data], { type });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}

function setUser(username) {
  $("userName").textContent = username;
  $("account").classList.remove("hidden");
  $("authScreen").classList.add("hidden");
  $("appShell").classList.remove("hidden");
  loadHistory();
}

async function authenticate(action) {
  const username = $("username").value.trim();
  const password = $("password").value;
  $("authStatus").textContent = "";
  try {
    const response = await fetch(`/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Unable to sign in.");
    setUser(data.username);
  } catch (error) {
    $("authStatus").textContent = error.message;
  }
}

$("projectForm").onsubmit = analyze;
$("refineForm").onsubmit = refineSection;
$("project").oninput = updateCharacterCount;
$("project").onkeydown = event => {
  if ((event.metaKey || event.ctrlKey) && event.key === "Enter") $("projectForm").requestSubmit();
};
$("example").onclick = () => {
  $("project").value = "Build an online food delivery system for customers, restaurants, and delivery partners.";
  $("projectType").value = "Web App";
  updateCharacterCount();
  $("project").focus();
};
$("clear").onclick = resetForm;
$("previewMode").onclick = () => setView("preview");
$("editMode").onclick = () => setView("edit");
$("editor").oninput = () => {
  result[active] = $("editor").value;
  customReport = active === "report";
  if (active !== "report") customReport = false;
  updateDocument();
};
$("copy").onclick = async () => {
  try {
    await navigator.clipboard.writeText(fullReport());
    showToast("Report copied to clipboard.");
  } catch (error) {
    showToast("Copy failed. Use the Edit view to select the report.");
  }
};
$("md").onclick = () => {
  download("architecture-report.md", fullReport(), "text/markdown");
  showToast("Markdown download started.");
};
$("pdf").onclick = async () => {
  $("pdf").disabled = true;
  try {
    const response = await fetch("/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report: fullReport() })
    });
    if (!response.ok) throw new Error();
    download("architecture-report.pdf", await response.blob(), "application/pdf");
    showToast("PDF download started.");
  } catch (error) {
    showToast("The PDF could not be created.");
  } finally {
    $("pdf").disabled = false;
  }
};
$("authForm").onsubmit = event => { event.preventDefault(); authenticate("login"); };
$("register").onclick = () => authenticate("register");
$("logout").onclick = async () => {
  await fetch("/logout", { method: "POST" });
  location.reload();
};

updateCharacterCount();
fetch("/me").then(response => response.json()).then(data => {
  if (data.username) setUser(data.username);
});
