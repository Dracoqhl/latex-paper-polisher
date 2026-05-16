const payload = JSON.parse(document.getElementById("workbench-payload").textContent);

function buildDecision(decision) {
  const reviewNotes = document.getElementById("review-notes").value;
  const finalText = decision === "accept"
    ? payload.suggested_text
    : decision === "revise"
      ? document.getElementById("final-text").value
      : "";
  return {
    schema_version: 1,
    mode: "main_agent_review_decision",
    paragraph_id: payload.paragraph_id,
    source_file: payload.source_file,
    section: payload.section,
    decision,
    review_notes: reviewNotes,
    original_text: payload.original_text,
    suggested_text: payload.suggested_text,
    final_text: finalText,
    ready_for_writeback: decision === "accept" || decision === "revise",
    metadata: {
      source_payload_metadata: payload.metadata || {}
    }
  };
}

function showDecision(decision) {
  document.getElementById("decision-json").textContent = JSON.stringify(buildDecision(decision), null, 2);
}

function downloadDecisionJson() {
  const text = document.getElementById("decision-json").textContent;
  const blob = new Blob([text], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${payload.paragraph_id || "review"}-decision.json`;
  link.click();
  URL.revokeObjectURL(url);
}

document.getElementById("accept-decision").addEventListener("click", () => showDecision("accept"));
document.getElementById("revise-decision").addEventListener("click", () => showDecision("revise"));
document.getElementById("reject-decision").addEventListener("click", () => showDecision("reject"));
document.getElementById("download-decision").addEventListener("click", downloadDecisionJson);
