(function () {
  const form = document.getElementById("survey-form");
  if (!form) return;

  const cards = Array.from(form.querySelectorAll(".q-card"));
  const progressText = document.getElementById("progress-text");
  const progressFill = document.getElementById("progress-fill");

  function isAnswered(card) {
    const type = card.dataset.type;
    const input = card.querySelector("[name]");
    if (!input) return false;
    const name = input.name;
    if (type === "multiple") {
      return form.querySelectorAll(`[name="${name}"]:checked`).length > 0;
    }
    if (type === "single" || type === "rating") {
      return Boolean(form.querySelector(`[name="${name}"]:checked`));
    }
    return Boolean((form.elements[name]?.value || "").trim());
  }

  function updateProgress() {
    const answered = cards.filter(isAnswered).length;
    if (progressText) progressText.textContent = `${answered} / ${cards.length}`;
    if (progressFill) {
      const pct = cards.length ? Math.round((answered / cards.length) * 100) : 0;
      progressFill.style.width = `${pct}%`;
    }
  }

  function clearError(card) {
    card.classList.remove("has-error");
    const err = card.querySelector(".q-error");
    if (err) err.classList.add("is-hidden");
  }

  function showError(card) {
    card.classList.add("has-error");
    const err = card.querySelector(".q-error");
    if (err) err.classList.remove("is-hidden");
  }

  form.addEventListener("input", function (event) {
    const card = event.target.closest(".q-card");
    if (card && isAnswered(card)) clearError(card);
    updateProgress();
  });
  form.addEventListener("change", updateProgress);

  form.addEventListener("submit", function (event) {
    let firstInvalid = null;
    cards.forEach(function (card) {
      if (card.dataset.required === "1" && !isAnswered(card)) {
        showError(card);
        if (!firstInvalid) firstInvalid = card;
      } else {
        clearError(card);
      }
    });
    if (firstInvalid) {
      event.preventDefault();
      firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });

  updateProgress();
})();
