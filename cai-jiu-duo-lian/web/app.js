const SCENES = [
  { id: "bento", label: "便当" },
  { id: "light-meal", label: "轻食" },
  { id: "seasonal", label: "时令" },
  { id: "regional", label: "地方味" },
  { id: "health", label: "调理" },
  { id: "happy", label: "快乐餐" },
];

const SCENE_LABELS = Object.fromEntries(SCENES.map((s) => [s.id, s.label]));

function validateForm(ingredients, customIngredients) {
  if (!ingredients.length && !customIngredients.length) return "请至少选择或输入一种食材";
  return "";
}

function parseCustomInput(raw) {
  return raw
    .split(/[,，、/\s]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

function updateSummary(selectedScene, selectedIngredients, customIngredients) {
  const el = document.getElementById("selection-summary");
  if (!el) return;
  const parts = [];
  if (selectedScene) {
    parts.push(`偏好：${SCENE_LABELS[selectedScene] || selectedScene}`);
  }
  const all = [...selectedIngredients, ...customIngredients];
  if (all.length) {
    parts.push(`食材：${all.join("、")}`);
  }
  if (!selectedScene) {
    parts.push("默认：快乐餐");
  }
  el.textContent = parts.length ? parts.join("  ·  ") : "还没选呢～先挑想吃的类型或食材吧";
  el.classList.toggle("has-selection", parts.length > 0);
}

function escapeHtml(text) {
  const d = document.createElement("div");
  d.textContent = text;
  return d.innerHTML;
}

/** Plan B: only AI/host raster assets under assets/illustrations/ */
function isRasterIllustration(url) {
  if (!url || typeof url !== "string") return false;
  if (!url.includes("/assets/illustrations/")) return false;
  return /\.(png|webp|jpe?g)(\?|$)/i.test(url);
}

function renderMetaBadge(icon, label, value) {
  return `<span class="meta-badge"><img src="${icon}" alt="" class="meta-icon" /><span class="meta-label">${escapeHtml(label)}</span><span class="meta-value">${escapeHtml(value)}</span></span>`;
}

function renderIngredientGrid(ingredients) {
  return (ingredients || [])
    .map((i) => {
      const artUrl = isRasterIllustration(i.artUrl) ? i.artUrl : "";
      const art = artUrl
        ? `<img class="ing-art" src="${escapeHtml(artUrl)}" alt="" loading="eager" decoding="async" />`
        : `<span class="ing-art ing-art-pending" title="食材插画待生成">待出图</span>`;
      return `<div class="ing-tile">${art}<span class="ing-name">${escapeHtml(i.name)}</span><span class="ing-amt">${escapeHtml(i.amount || "")}</span></div>`;
    })
    .join("");
}

function bindIngredientArtErrors(root) {
  if (!root) return;
  root.querySelectorAll("img.ing-art").forEach((img) => {
    if (img.dataset.ingBound) return;
    img.dataset.ingBound = "1";
    img.addEventListener(
      "error",
      () => {
        const span = document.createElement("span");
        span.className = "ing-art ing-art-pending";
        span.title = "食材插画待生成";
        span.textContent = "待出图";
        img.replaceWith(span);
      },
      { once: true }
    );
  });
}

const CIRCLED_NUMBERS = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"];

function stepCardClass(text) {
  const len = (text || "").length;
  if (len > 85) return "step-card--long";
  if (len > 42) return "step-card--medium";
  return "step-card--short";
}

function renderStepItem(s, idx) {
  const text = typeof s === "string" ? s : s.text || "";
  const rawUrl =
    (typeof s === "object" && (s.stepIllustrationUrl || s.stepArtUrl)) || "";
  const compositeUrl = isRasterIllustration(rawUrl) ? rawUrl : "";
  const stepNo = (typeof s === "object" && s.index) || idx + 1;
  const circled = CIRCLED_NUMBERS[stepNo - 1] || `${stepNo}.`;
  const sizeClass = stepCardClass(text);
  let sceneHtml;
  if (compositeUrl) {
    sceneHtml = `<img class="step-composite-art" src="${escapeHtml(compositeUrl)}" alt="" loading="eager" />`;
  } else {
    sceneHtml = `<div class="step-art-pending" aria-hidden="true">步骤插画待生成</div>`;
  }
  return `<li class="step-card ${sizeClass}">
    <div class="step-scene-wrap" aria-hidden="true">${sceneHtml}</div>
    <div class="step-copy">
      <p class="step-text"><span class="step-index">${circled}</span>${escapeHtml(text)}</p>
    </div>
  </li>`;
}

function isCookingStep(text) {
  const t = (text || "").trim();
  if (!t) return false;
  if (/^(?:即可|趁热|慢慢)?(?:品尝|享用|食用)[。．.!！]?$/.test(t)) return false;
  if (/^装盘享用[。．.!！]?$/.test(t)) return false;
  if (/^[\*\s.]+$/.test(t)) return false;
  if (/卡路里|千卡|总脂肪|饱和脂肪|反式脂肪|膳食纤维|总碳水化合物/.test(t)) return false;
  if (/维生素\s*[A-CＡ-Ｃ]|钠\s*[-—]?\s*毫克|钾\s*[-—]?\s*毫克/.test(t)) return false;
  if ((/维生素|钙|铁/.test(t) && /%/.test(t)) || (t.includes("毫克") && t.split("毫克").length > 2)) return false;
  return true;
}

function filterCookingSteps(steps) {
  const out = [];
  (steps || []).forEach((s) => {
    const text = typeof s === "string" ? s : s.text || "";
    if (!isCookingStep(text)) return;
    out.push(typeof s === "object" ? { ...s } : { text: s });
  });
  return out.map((s, idx) => ({ ...s, index: idx + 1 }));
}

function renderStepTips(_recipe) {
  return "";
}

function renderHeroArts(recipe) {
  const composite = recipe.heroIllustrationUrl;
  if (composite) {
    return `<img class="recipe-hero-art" src="${escapeHtml(composite)}" alt="${escapeHtml(recipe.name)}" />`;
  }
  return `<div class="recipe-hero-art-placeholder recipe-hero-art-pending">插画待生成<br><small>在 Cursor 中让 Agent 执行 illustration_jobs_cli 出图</small></div>`;
}

function renderRecipeCard(recipe, isPrimary) {
  const steps = filterCookingSteps(recipe.steps || [])
    .map((s, idx) => renderStepItem(s, idx))
    .join("");
  const servings = recipe.servings ? `${recipe.servings} 人份` : "未指定";
  const timeText = recipe.cookTimeDisplay || recipe.cookTime || "";

  const meta = [
    renderMetaBadge("icons/sections/scene.svg", "出处", `《${recipe.source?.book || ""}》`),
    renderMetaBadge("icons/sections/servings.svg", "份量", servings),
    renderMetaBadge("icons/sections/taste.svg", "时长", timeText),
    renderMetaBadge("icons/groups/staple.svg", "方式", recipe.method || "—"),
    renderMetaBadge("icons/sections/notes.svg", "花费", recipe.cost || "—"),
  ].join("");

  return `
    <article class="recipe-card ${isPrimary ? "primary" : "alt"}">
      <div class="recipe-hero">
        <div class="recipe-hero-copy">
          <p class="recipe-kicker">${isPrimary ? "今日推荐" : "也可以试试"}</p>
          <h3 class="recipe-title"><span class="recipe-title-text">${escapeHtml(recipe.name)}</span></h3>
          <div class="recipe-meta-grid">${meta}</div>
        </div>
        <div class="recipe-hero-art-frame">
          ${renderHeroArts(recipe)}
          <span class="hero-caption">手绘出餐示意</span>
        </div>
      </div>
      <div class="ingredient-showcase">
        <div class="ingredients-banner">食材<span class="ing-servings">（${escapeHtml(servings)}）</span></div>
        <div class="ing-grid">${renderIngredientGrid(recipe.ingredients)}</div>
        <p class="ing-footer">再忙也要好好吃饭</p>
      </div>
      <div class="recipe-body">
        <div class="steps-banner">做法</div>
        <ol class="step-list">${steps}</ol>
        ${renderStepTips(recipe)}
      </div>
    </article>
  `;
}

function collectImageUrls(root) {
  if (!root) return [];
  return [...new Set([...root.querySelectorAll("img[src]")].map((img) => img.getAttribute("src")).filter(Boolean))];
}

function preloadOne(url, timeoutMs = 12000) {
  return new Promise((resolve) => {
    const img = new Image();
    let done = false;
    const finish = (ok) => {
      if (done) return;
      done = true;
      resolve({ url, ok });
    };
    const timer = setTimeout(() => finish(false), timeoutMs);
    img.onload = () => {
      clearTimeout(timer);
      if (img.decode) {
        img.decode().then(() => finish(true)).catch(() => finish(true));
      } else {
        finish(true);
      }
    };
    img.onerror = () => {
      clearTimeout(timer);
      finish(false);
    };
    img.src = url;
  });
}

async function preloadImages(urls) {
  const results = await Promise.all(urls.map((url) => preloadOne(url)));
  const failed = results.filter((r) => !r.ok).map((r) => r.url);
  if (failed.length) {
    await Promise.all(failed.map((url) => preloadOne(url, 8000)));
  }
  return results;
}

async function mountResultWithArtReady(outputEl, html) {
  outputEl.innerHTML = `<div class="result-shell result-art-loading">${html}</div>`;
  const shell = outputEl.querySelector(".result-shell");
  bindIngredientArtErrors(shell);
  const urls = collectImageUrls(shell);
  if (urls.length) {
    await preloadImages(urls);
  }
  shell.classList.remove("result-art-loading");
  shell.classList.add("result-art-ready");
}

function renderResult(data) {
  const why = data.why ? `<p class="result-why">${escapeHtml(data.why)}</p>` : "";
  const primary = renderRecipeCard(data.primary, true);
  const alts = (data.alternates || []).map((r) => renderRecipeCard(r, false)).join("");
  const source = data.skill?.source
    ? `<p class="result-source">Skill 来源：${escapeHtml(data.skill.source)}</p>`
    : "";
  return `${why}${primary}${alts ? `<h3 class="alt-title">更多选择</h3>${alts}` : ""}${source}`;
}

document.addEventListener("DOMContentLoaded", () => {
  let selectedScene = null;
  const selectedIngredients = new Set();
  const customIngredients = new Set();
  const outputEl = document.getElementById("output");
  const submitBtn = document.querySelector("button.primary");
  const customInput = document.getElementById("custom-ingredient");
  const customChipsEl = document.getElementById("custom-ingredient-chips");

  function renderCustomChips() {
    customChipsEl.innerHTML = [...customIngredients]
      .map(
        (name) =>
          `<button type="button" class="chip selected custom" data-custom="${escapeHtml(name)}">${escapeHtml(name)} ×</button>`
      )
      .join("");
    customChipsEl.querySelectorAll("[data-custom]").forEach((btn) => {
      btn.addEventListener("click", () => {
        customIngredients.delete(btn.dataset.custom);
        renderCustomChips();
        updateSummary(selectedScene, selectedIngredients, customIngredients);
      });
    });
  }

  function addCustomIngredients(raw) {
    parseCustomInput(raw).forEach((name) => customIngredients.add(name));
    customInput.value = "";
    renderCustomChips();
    document.getElementById("ingredient-error").textContent = "";
    updateSummary(selectedScene, selectedIngredients, customIngredients);
  }

  document.getElementById("add-custom-ingredient").addEventListener("click", () => {
    addCustomIngredients(customInput.value);
  });

  customInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addCustomIngredients(customInput.value);
    }
  });

  document.querySelectorAll(".scene-card").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.scene;
      if (selectedScene === id) {
        selectedScene = null;
        btn.classList.remove("selected");
      } else {
        selectedScene = id;
        document.querySelectorAll(".scene-card").forEach((c) => c.classList.remove("selected"));
        btn.classList.add("selected");
      }
      updateSummary(selectedScene, selectedIngredients, customIngredients);
    });
  });

  document.querySelectorAll(".chip[data-ingredient]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const name = btn.dataset.ingredient;
      if (selectedIngredients.has(name)) {
        selectedIngredients.delete(name);
        btn.classList.remove("selected");
      } else {
        selectedIngredients.add(name);
        btn.classList.add("selected");
      }
      document.getElementById("ingredient-error").textContent = "";
      updateSummary(selectedScene, selectedIngredients, customIngredients);
    });
  });

  document.getElementById("recipe-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const ingredients = [...selectedIngredients];
    const custom = [...customIngredients];
    const err = validateForm(ingredients, custom);
    if (err) {
      document.getElementById("ingredient-error").textContent = err;
      outputEl.classList.remove("visible");
      return;
    }

    const payload = {
      scene: selectedScene,
      ingredients,
      customIngredients: custom,
      taste: document.getElementById("taste").value.trim(),
      servings: document.getElementById("servings").value,
      freeText: document.getElementById("free-text").value.trim(),
    };

    submitBtn.disabled = true;
    submitBtn.textContent = "正在搜索菜谱并加载手绘插画…";
    outputEl.innerHTML = '<p class="loading">正在搜索高频家常菜谱，并预加载手绘插画…</p>';
    outputEl.classList.add("visible");

    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || `请求失败 (${res.status})`);
      }
      outputEl.innerHTML = '<p class="loading">手绘插画加载中，请稍候…</p>';
      await mountResultWithArtReady(outputEl, renderResult(data));
      outputEl.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (ex) {
      outputEl.innerHTML = `<p class="error-block">出错了：${escapeHtml(ex.message)}<br><small>请运行 <code>python scripts/ensure_web_server.py</code> 确保 Web 服务已启动，而非直接打开 html 文件。</small></p>`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = '<img src="icons/sections/submit.svg" alt="" class="btn-icon" /> 开始推荐';
    }
  });

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  }

  updateSummary(selectedScene, selectedIngredients, customIngredients);
});
