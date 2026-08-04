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

function renderMetaBadge(icon, label, value) {
  return `<span class="meta-badge"><img src="${icon}" alt="" class="meta-icon" /><span class="meta-label">${escapeHtml(label)}</span><span class="meta-value">${escapeHtml(value)}</span></span>`;
}

function renderIngredientGrid(ingredients) {
  return (ingredients || [])
    .map((i) => {
      const art = i.artUrl
        ? `<img class="ing-art" src="${escapeHtml(i.artUrl)}" alt="" />`
        : `<span class="ing-art ing-art-fallback"></span>`;
      return `<div class="ing-tile">${art}<span class="ing-name">${escapeHtml(i.name)}</span><span class="ing-amt">${escapeHtml(i.amount || "")}</span></div>`;
    })
    .join("");
}

function renderStepItem(s, idx) {
  const text = typeof s === "string" ? s : s.text || "";
  const sceneUrl = (typeof s === "object" && s.sceneUrl) || "/icons/step-scenes/bowl.svg";
  const arts = (typeof s === "object" && s.ingredientArts) || [];
  const stepNo = (typeof s === "object" && s.index) || idx + 1;
  const artHtml = arts
    .map((url) => `<img class="step-ing-art" src="${escapeHtml(url)}" alt="" />`)
    .join("");
  return `<li class="step-card">
    <div class="step-scene-wrap">
      <img class="step-scene-bg" src="${escapeHtml(sceneUrl)}" alt="" />
      <div class="step-scene-ingredients">${artHtml}</div>
      <span class="step-num">${stepNo}</span>
    </div>
    <p class="step-text">${escapeHtml(text)}</p>
  </li>`;
}

function renderHeroArts(recipe) {
  const arts = recipe.heroArts && recipe.heroArts.length ? recipe.heroArts : [];
  const single = recipe.heroImageUrl || recipe.lineArtUrl;
  const urls = arts.length ? arts : single ? [single] : [];
  if (!urls.length) {
    return `<div class="recipe-hero-art-placeholder">手绘出餐示意</div>`;
  }
  if (urls.length === 1) {
    return `<img class="recipe-hero-art" src="${escapeHtml(urls[0])}" alt="${escapeHtml(recipe.name)}" />`;
  }
  return `<div class="recipe-hero-art-grid">${urls
    .map((url) => `<img class="recipe-hero-art-item" src="${escapeHtml(url)}" alt="" />`)
    .join("")}</div>`;
}

function renderRecipeCard(recipe, isPrimary) {
  const steps = (recipe.steps || []).map((s, idx) => renderStepItem(s, idx)).join("");
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
        <h4><img src="icons/sections/ingredients.svg" alt="" class="section-icon" /> 食材清单</h4>
        <div class="ing-grid">${renderIngredientGrid(recipe.ingredients)}</div>
      </div>
      <div class="recipe-body">
        <h4><img src="icons/steps/cook.svg" alt="" class="section-icon" /> 做法步骤</h4>
        <ol class="step-list">${steps}</ol>
        ${recipe.disclaimer ? `<p class="disclaimer">${escapeHtml(recipe.disclaimer)}</p>` : ""}
      </div>
    </article>
  `;
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
    submitBtn.textContent = "正在推荐…";
    outputEl.innerHTML = '<p class="loading">正在调用 Skill 为你选菜…</p>';
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
      outputEl.innerHTML = renderResult(data);
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
