# 做法步骤排版规范

> 参考手账风「做法」长图（Plan B：步骤 **叙事插画**）。与 [`illustration-style-bible.md`](illustration-style-bible.md)、[`line-art-guide.md`](line-art-guide.md) 配合。

## 参考图要点

| 元素 | 规范 |
|------|------|
| **区块标题** | 黑色不规则标签「**做法**」 |
| **步骤结构** | **左图右文**；图文垂直居中；图随文字长度伸缩 |
| **步骤序号** | 行首 **①②③** 圈号 |
| **步骤文字** | 马善政/站酷快乐体 + **淡黄荧光笔底纹**（`#FFF2CC`~`#FFE082`） |
| **手绘插图** | **叙事插画** `stepIllustrationUrl`（腌制/煮粥/翻炒等独立场景） |
| **小贴士** | 底部黄框 + 小猫「**唠唠叨叨**」 |

**禁止**：容器 SVG + 缩小食材 icon 叠加（v1.5 compose 方案，已废弃）。

## 插图规格

| 文字长度 | CSS 类 | 插图高度 |
|----------|--------|----------|
| ≤42 字 | `step-card--short` | 135px |
| 43–85 字 | `step-card--medium` | 150px |
| >85 字 | `step-card--long` | 180px |

## 步骤叙事映射

关键词 → `assets/illustrations/steps/{sceneId}.svg`，由 `illustration_resolver.STEP_ILLUSTRATION_RULES` 按优先级匹配。

| sceneId | 关键词示例 |
|---------|------------|
| `board_marinate` | 腌、用酱油 |
| `board_cut` | 切、切丁、手撕 |
| `prep_wash` | 洗净、浸泡 |
| `pot_porridge_simmer` | 粥、七分熟、糯米 |
| `pot_season_finish` | 加盐、调味即可 |
| `wok_stir_fry` | 炒、翻炒 |
| `wok_pan_fry` | 煎、烙 |
| `pot_boil_simmer` | 炖、煲、再煮 |
| `blender_pour` | 搅拌、打沙、料理机 |
| `freezer_chill` | 冷冻、冷藏 |
| `default_prep` | 兜底 |

完整 15 个场景见 [`illustration-style-bible.md`](illustration-style-bible.md)。

## 网页实现对照

| 规范 | 实现 |
|------|------|
| 「做法」标题 | `.steps-banner` |
| 左图右文 | `.step-card` grid |
| 叙事插图 | `.step-composite-art` ← `stepIllustrationUrl` / `stepArtUrl` |
| 圈号 + 荧光笔底 | `.step-text` + `.step-index` |
| 唠唠叨叨 | `.step-tip-box` ← `qualityNotes` / `disclaimer` |
| 预加载 | `mountResultWithArtReady()` |

## API 字段

```json
{
  "steps": [{
    "index": 1,
    "text": "…",
    "sceneId": "board_marinate",
    "stepIllustrationUrl": "/skill-assets/assets/illustrations/steps/board_marinate.svg",
    "stepArtUrl": "/skill-assets/assets/illustrations/steps/board_marinate.svg",
    "scene": "board",
    "sceneUrl": "/icons/step-scenes/board.svg",
    "ingredientArts": []
  }]
}
```

优先渲染 `stepIllustrationUrl`（或 `stepArtUrl`）PNG。无图显示「步骤插画待生成」。**无 SVG 回退**。

## 对话输出（无网页）

```
① [腌制场景叙事插画]
   鸡胸肉洗净，撕成丝状，用酱油腌制5分钟…
② [砂锅煮粥场景]
   大米和糯米混合煮粥…
💡 唠唠叨叨：……
```

## 维护

变更步骤 UI：同步 `web/app.js`、`web/styles.css`、本文件、`output-template.md`、`SKILL.md` § Step 5。  
新增步骤叙事：在 `assets/illustrations/steps/` 加 SVG + 更新 `STEP_ILLUSTRATION_RULES` + [`extension-checklist.md`](extension-checklist.md) §D。
