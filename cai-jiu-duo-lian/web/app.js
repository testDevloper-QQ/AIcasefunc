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

function renderRecipeCard(recipe, title, isPrimary) {
  const ingList = (recipe.ingredients || [])
    .map((i) => `<li>${escapeHtml(i.name)} ${escapeHtml(i.amount || "")}</li>`)
    .join("");
  const steps = (recipe.steps || [])
    .map((s, idx) => {
      const text = typeof s === "string" ? s : s.text || "";
      const icon = typeof s === "object" && s.icon ? s.icon : `/icons/steps/prep.svg`;
      return `<li class="step-item">
        <img class="step-icon" src="${escapeHtml(icon)}" alt="" />
        <span>${escapeHtml(text)}</span>
      </li>`;
    })
    .join("");
  const img = recipe.lineArtUrl
    ? `<img class="recipe-art" src="${escapeHtml(recipe.lineArtUrl)}" alt="" />`
    : "";

  return `
    <article class="recipe-card ${isPrimary ? "primary" : "alt"}">
      <div class="recipe-header">
        ${img}
        <div>
          <h3>${escapeHtml(recipe.name)}</h3>
          <p class="recipe-meta">
            📖 《${escapeHtml(recipe.source?.book || "")}》
            · ⏱ ${escapeHtml(recipe.cookTime || "")}
            · 💰 ${escapeHtml(recipe.cost || "")}
            · 🔥 ${escapeHtml(recipe.method || "")}
          </p>
          <p class="recipe-servings">${escapeHtml(String(recipe.servings || ""))} 人份</p>
        </div>
      </div>
      <div class="recipe-body">
        <h4>食材清单</h4>
        <ul>${ingList}</ul>
        <h4>做法步骤</h4>
        <ol>${steps}</ol>
        ${recipe.disclaimer ? `<p class="disclaimer">${escapeHtml(recipe.disclaimer)}</p>` : ""}
      </div>
    </article>
  `;
}

function renderResult(data) {
  const why = data.why ? `<p class="result-why">${escapeHtml(data.why)}</p>` : "";
  const primary = renderRecipeCard(data.primary, "推荐", true);
  const alts = (data.alternates || [])
    .map((r) => renderRecipeCard(r, "备选", false))
    .join("");
  const source = data.skill?.source
    ? `<p class="result-source">Skill 来源：${escapeHtml(data.skill.source)}</p>`
    : "";
  return `${why}${primary}${alts ? `<h3 class="alt-title">也可以试试</h3>${alts}` : ""}${source}`;
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
      outputEl.innerHTML = `<p class="error-block">出错了：${escapeHtml(ex.message)}<br><small>请确认已通过 <code>python scripts/web_server.py</code> 启动服务，而非直接打开 html 文件。</small></p>`;
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
