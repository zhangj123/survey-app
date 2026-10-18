(function () {
  const overlay = document.getElementById("scan-overlay");
  if (!overlay) return;
  const dialog = overlay.querySelector(".scan-dialog");
  const title = document.getElementById("scan-title");
  const hint = document.getElementById("scan-hint");
  const status = document.getElementById("scan-status");
  const img = document.getElementById("scan-qr-img");
  const closeBtn = document.getElementById("scan-close");
  const csrf = document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
  let timer = null;
  let claimUrl = "";

  const copy = {
    wechat: { title: "微信扫码登录", hint: "请使用微信扫一扫", brand: "微信" },
    qq: { title: "QQ 扫码登录", hint: "请使用 QQ 扫一扫", brand: "QQ" },
  };

  function stop() {
    if (timer) {
      clearInterval(timer);
      timer = null;
    }
  }

  function close() {
    stop();
    overlay.hidden = true;
  }

  async function poll(statusUrl) {
    const response = await fetch(statusUrl, { headers: { Accept: "application/json" } });
    const data = await response.json();
    if (data.status === "confirmed") {
      status.textContent = "扫码成功，正在登录…";
      const claimed = await fetch(claimUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrf },
      });
      const payload = await claimed.json();
      if (claimed.ok && payload.redirect) {
        window.location.href = payload.redirect;
      } else {
        status.textContent = payload.error || "登录失败，请刷新二维码";
      }
      stop();
    } else if (data.status === "expired" || data.status === "claimed") {
      status.textContent = "二维码已失效，请关闭后重试";
      stop();
    }
  }

  async function openScan(provider) {
    const meta = copy[provider];
    if (!meta) return;
    dialog.classList.toggle("is-wechat", provider === "wechat");
    dialog.classList.toggle("is-qq", provider === "qq");
    title.textContent = meta.title;
    hint.textContent = meta.hint;
    document.getElementById("scan-brand").textContent = meta.brand;
    status.textContent = "等待扫码…";
    overlay.hidden = false;
    const created = await fetch(`/login/qr/${provider}/`, {
      method: "POST",
      headers: { "X-CSRFToken": csrf, Accept: "application/json" },
    });
    const data = await created.json();
    if (!created.ok) {
      status.textContent = data.error || "暂时无法生成二维码";
      return;
    }
    img.src = data.qr_url;
    claimUrl = data.claim_url;
    stop();
    timer = setInterval(() => poll(data.status_url).catch(() => {}), 1500);
  }

  document.querySelectorAll("[data-scan]").forEach((button) => {
    button.addEventListener("click", () => openScan(button.dataset.scan));
  });
  closeBtn.addEventListener("click", close);
  overlay.addEventListener("click", (event) => {
    if (event.target === overlay) close();
  });
})();
