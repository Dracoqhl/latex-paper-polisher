const sectionPackage = JSON.parse(document.getElementById("section-polish-package").textContent);
let currentIndex = 0;
const finalTexts = {};
const discussions = {};

function currentItem() {
  return sectionPackage.items[currentIndex];
}

function listItems(elementId, values) {
  const element = document.getElementById(elementId);
  element.innerHTML = "";
  if (!values || values.length === 0) {
    const item = document.createElement("li");
    item.textContent = "None.";
    element.appendChild(item);
    return;
  }
  values.forEach((value) => {
    const item = document.createElement("li");
    item.textContent = value;
    element.appendChild(item);
  });
}

function saveCurrentState() {
  const item = currentItem();
  finalTexts[item.item_id] = document.getElementById("final-text").value;
  discussions[item.item_id] = document.getElementById("agent-discussion").value;
}

function renderWholeSection() {
  const originalText = sectionPackage.items.map((item) => item.original_text).join("\n\n");
  const suggestedText = sectionPackage.items.map((item) => item.suggested_text || item.original_text).join("\n\n");
  document.getElementById("section-original-text").textContent = originalText;
  document.getElementById("section-suggested-text").textContent = suggestedText;
}

function loadCurrentItem() {
  const item = currentItem();
  document.getElementById("item-counter").textContent = `${currentIndex + 1} / ${sectionPackage.items.length}`;
  document.getElementById("source-location").textContent = `${item.source_file}:${item.line_range[0]}-${item.line_range[1]}`;
  document.getElementById("current-original-text").textContent = item.original_text;
  listItems("revision-notes", item.revision_notes);
  listItems("risks", item.risks);
  listItems("questions", item.questions);
  document.getElementById("final-text").value = finalTexts[item.item_id] ?? item.editable_text ?? item.original_text;
  document.getElementById("agent-discussion").value = discussions[item.item_id] ?? "";
}

function copyText(elementId) {
  const text = document.getElementById(elementId).textContent;
  navigator.clipboard.writeText(text);
}

function goTo(delta) {
  saveCurrentState();
  currentIndex = Math.max(0, Math.min(sectionPackage.items.length - 1, currentIndex + delta));
  loadCurrentItem();
}

function buildFinalEdits() {
  saveCurrentState();
  return {
    schema_version: 1,
    mode: "section_final_edits",
    section_id: sectionPackage.section_id,
    section_title: sectionPackage.section_title,
    items: sectionPackage.items.map((item) => ({
      item_id: item.item_id,
      source_file: item.source_file,
      line_range: item.line_range,
      original_text: item.original_text,
      final_text: finalTexts[item.item_id] ?? item.editable_text ?? item.original_text
    }))
  };
}

function downloadSectionFinalEdits() {
  const edits = buildFinalEdits();
  const text = JSON.stringify(edits, null, 2);
  document.getElementById("section-final-edits").textContent = text;
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `section-final-edits-${sectionPackage.section_id}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

document.getElementById("copy-section-original").addEventListener("click", () => copyText("section-original-text"));
document.getElementById("copy-section-suggested").addEventListener("click", () => copyText("section-suggested-text"));
document.getElementById("previous-item").addEventListener("click", () => goTo(-1));
document.getElementById("next-item").addEventListener("click", () => goTo(1));
document.getElementById("submit-section").addEventListener("click", downloadSectionFinalEdits);
renderWholeSection();
loadCurrentItem();
