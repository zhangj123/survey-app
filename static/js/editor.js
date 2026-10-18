(function () {
  const dataNode = document.getElementById("editor-data");
  if (!dataNode) return;
  const state = JSON.parse(dataNode.textContent);
  const csrf =
    document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
    document.cookie.match(/csrftoken=([^;]+)/)?.[1] ||
    "";
  const titleInput = document.getElementById("survey-title");
  const descInput = document.getElementById("survey-desc");
  const minutesInput = document.getElementById("survey-minutes");
  const list = document.getElementById("question-list");
  const typeGrid = document.getElementById("type-grid");
  const publishBtn = document.getElementById("publish-btn");
  const saveStatus = document.getElementById("save-status");
  const base = `/surveys/${state.id}`;
  let saveTimer = null;
  let dragId = null;

  function headers() {
    return {
      "Content-Type": "application/json",
      "X-CSRFToken": csrf,
    };
  }

  function setStatus(text, isError) {
    saveStatus.textContent = text;
    saveStatus.classList.toggle("is-error", Boolean(isError));
  }

  async function request(url, options) {
    setStatus("保存中…");
    const response = await fetch(url, options);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = payload.error || "保存失败";
      setStatus(message, true);
      throw new Error(message);
    }
    setStatus("已保存");
    return payload;
  }

  function applySurvey(payload) {
    if (!payload.survey) return;
    Object.assign(state, payload.survey);
    render();
  }

  function debounceMeta() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => saveMeta({}), 400);
  }

  async function saveMeta(extra) {
    const body = {
      title: titleInput.value,
      description: descInput.value,
      estimated_minutes: Number(minutesInput.value || 3),
      ...extra,
    };
    const payload = await request(`${base}/editor/meta/`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify(body),
    });
    if (payload.survey) {
      state.title = payload.survey.title;
      state.description = payload.survey.description;
      state.estimated_minutes = payload.survey.estimated_minutes;
      state.is_published = payload.survey.is_published;
      updatePublishBtn();
    }
  }

  async function addQuestion(qtype) {
    const payload = await request(`${base}/editor/questions/`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ qtype }),
    });
    state.questions.push(payload.question);
    render();
  }

  async function saveQuestion(question, extra) {
    const payload = await request(`${base}/editor/questions/${question.id}/`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({
        title: question.title,
        hint: question.hint,
        required: question.required,
        options: question.options,
        scale_max: question.scale_max,
        qtype: question.qtype,
        ...extra,
      }),
    });
    const index = state.questions.findIndex((item) => item.id === question.id);
    if (index >= 0) {
      const prev = state.questions[index];
      state.questions[index] = payload.question;
      if (prev.qtype !== payload.question.qtype) render();
    }
  }

  async function deleteQuestion(id) {
    if (!confirm("确定删除这道题？")) return;
    const payload = await request(`${base}/editor/questions/${id}/`, {
      method: "DELETE",
      headers: headers(),
    });
    applySurvey(payload);
  }

  async function reorder() {
    const ids = state.questions.map((item) => item.id);
    const payload = await request(`${base}/editor/questions/reorder/`, {
      method: "POST",
      headers: headers(),
      body: JSON.stringify({ ids }),
    });
    applySurvey(payload);
  }

  function updatePublishBtn() {
    publishBtn.textContent = state.is_published ? "取消发布" : "发布问卷";
    publishBtn.classList.toggle("btn-ghost", state.is_published);
    publishBtn.classList.toggle("btn-primary", !state.is_published);
  }

  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([key, value]) => {
      if (key === "class") node.className = value;
      else if (key.startsWith("on") && typeof value === "function") node.addEventListener(key.slice(2).toLowerCase(), value);
      else if (key === "checked" || key === "draggable") node[key] = value;
      else if (value != null) node.setAttribute(key, value);
    });
    (children || []).forEach((child) => {
      if (child == null || child === false) return;
      node.append(child.nodeType ? child : document.createTextNode(child));
    });
    return node;
  }

  function renderTypeGrid() {
    typeGrid.replaceChildren();
    state.types.forEach((type) => {
      typeGrid.append(
        el("button", {
          type: "button",
          class: "type-chip",
          onClick: () => addQuestion(type.value).catch(() => {}),
        }, [type.label])
      );
    });
  }

  function renderQuestion(question, index) {
    const card = el("section", {
      class: "editor-q",
      draggable: true,
      "data-id": question.id,
      onDragstart: () => { dragId = question.id; },
      onDragover: (event) => event.preventDefault(),
      onDrop: () => {
        if (dragId == null || dragId === question.id) return;
        const from = state.questions.findIndex((item) => item.id === dragId);
        const to = state.questions.findIndex((item) => item.id === question.id);
        const [moved] = state.questions.splice(from, 1);
        state.questions.splice(to, 0, moved);
        dragId = null;
        reorder().catch(() => {});
      },
    });

    const titleField = el("input", {
      class: "q-title-input",
      value: question.title,
      maxlength: "300",
      placeholder: "请输入题目",
    });
    titleField.value = question.title;
    titleField.addEventListener("change", () => {
      question.title = titleField.value;
      saveQuestion(question).catch(() => {});
    });

    const hintField = el("input", {
      class: "q-hint-input",
      value: question.hint,
      maxlength: "200",
      placeholder: "题目说明（选填）",
    });
    hintField.value = question.hint || "";
    hintField.addEventListener("change", () => {
      question.hint = hintField.value;
      saveQuestion(question).catch(() => {});
    });

    const typeSelect = el("select", { class: "q-type-select" });
    state.types.forEach((type) => {
      const option = el("option", { value: type.value }, [type.label]);
      if (type.value === question.qtype) option.selected = true;
      typeSelect.append(option);
    });
    typeSelect.addEventListener("change", () => {
      saveQuestion(question, { qtype: typeSelect.value }).catch(() => {});
    });

    const required = el("input", { type: "checkbox", checked: question.required });
    required.checked = question.required;
    required.addEventListener("change", () => {
      question.required = required.checked;
      saveQuestion(question).catch(() => {});
    });

    card.append(
      el("div", { class: "editor-q-head" }, [
        el("span", { class: "drag-handle" }, ["↕ " + (index + 1)]),
        typeSelect,
        el("label", { class: "req-toggle" }, [required, " 必填"]),
        el("button", {
          type: "button",
          class: "btn btn-ghost danger",
          onClick: () => deleteQuestion(question.id).catch(() => {}),
        }, ["删除"]),
      ]),
      titleField,
      hintField
    );

    if (question.has_options) {
      const optionsBox = el("div", { class: "option-editor" });
      question.options.forEach((opt, optIndex) => {
        const input = el("input", { value: opt, maxlength: "80", placeholder: "选项" });
        input.value = opt;
        input.addEventListener("change", () => {
          question.options[optIndex] = input.value;
          saveQuestion(question).catch(() => {});
        });
        optionsBox.append(
          el("div", { class: "option-row" }, [
            input,
            el("button", {
              type: "button",
              class: "btn btn-ghost danger",
              onClick: () => {
                question.options.splice(optIndex, 1);
                saveQuestion(question).catch(() => {});
              },
            }, ["×"]),
          ])
        );
      });
      optionsBox.append(
        el("button", {
          type: "button",
          class: "btn btn-ghost",
          onClick: () => {
            question.options.push("选项" + (question.options.length + 1));
            saveQuestion(question).catch(() => {});
          },
        }, ["添加选项"])
      );
      card.append(optionsBox);
    }

    if (question.has_scale) {
      const scale = el("input", { type: "number", min: "2", max: "10", class: "scale-input" });
      scale.value = question.scale_max;
      scale.addEventListener("change", () => {
        question.scale_max = Number(scale.value);
        saveQuestion(question).catch(() => {});
      });
      card.append(el("label", { class: "scale-field" }, ["评分上限 ", scale]));
    }

    return card;
  }

  function render() {
    titleInput.value = state.title;
    descInput.value = state.description;
    minutesInput.value = state.estimated_minutes;
    list.replaceChildren(...state.questions.map((question, index) => renderQuestion(question, index)));
    updatePublishBtn();
  }

  titleInput.addEventListener("input", debounceMeta);
  descInput.addEventListener("input", debounceMeta);
  minutesInput.addEventListener("change", () => saveMeta({}).catch(() => {}));
  publishBtn.addEventListener("click", () => {
    const next = !state.is_published;
    const message = next ? "发布后其他人就能在「填写」里看到这份问卷。" : "取消发布后，其他人将无法继续打开填写页。";
    if (!confirm(message)) return;
    saveMeta({ is_published: next }).catch(() => {});
  });

  renderTypeGrid();
  render();
})();
