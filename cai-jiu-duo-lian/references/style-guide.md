# 风格指南

## 语气

- 像会做饭的朋友，有书卷气
- 先给结论，再简短解释「为什么选这道」
- 一句话场景理由：「今日想清爽，适合从《哇！沙拉的教科书》里挑一道」

## 禁止

- 网红腔：「绝绝子」「家人们」「灵魂暴击」
- 捏造菜品、营养/medical 断言
- 一人食推 2 人量（反之亦然）
- 网页界面使用 emoji 作功能图标（改用线稿/插画）
- Hero「空盘 + 食材 icon 拼贴」、步骤「容器 + 缩小 icon 叠加」（已废弃，见 Plan B）

## 网页配色

- 主色：#FFF8E7（暖黄背景）
- 强调色：#E8A838（按钮/选中）
- 文字：#4A4035
- 线稿描边：#5C4F42

## 网页视觉

- **标题**：站酷快乐体（ZCOOL KuaiLe），手写趣味、俏皮可爱，可轻微倾斜
- **插画**：暖黄手账 + 数字水彩叙事感；参考 [`illustration-style-bible.md`](illustration-style-bible.md)
- **手绘配图完整规范**：见 [`line-art-guide.md`](line-art-guide.md)（Hero 成品、步骤叙事、食材单项，**不可省略**）
- **场景卡片**：6 类饮食偏好线稿（`web/icons/scenes/`）
- **表单文案**：「今天想吃什么？」为可选偏好；「冰箱里有什么？」食材至少选 1 个

## 推荐卡片（Hero）

手账风主卡片，自上而下：

1. **大标题**：菜名，站酷快乐体，可轻微倾斜
2. **信息徽章**：出处 · 时长 · 方式 · 份量 · 花费（小标签横排）
3. **成品叙事插画**：`heroIllustrationUrl`（整道菜 / 品类模板）；标注「手绘出餐示意」
4. **食材网格**（见 [`ingredient-art-guide.md`](ingredient-art-guide.md)）：
   - 黑色「**食材**（N 人份）」标签 + 虚线框
   - 每项：**72×72 手绘** + 马善政名称 + 中文份量
   - 页脚「再忙也要好好吃饭」
5. **步骤列表**（见 [`step-layout-guide.md`](step-layout-guide.md)）：
   - 左上角黑色标签「**做法**」
   - 每步 **左图右文**；左侧为 **动作叙事插画**（非容器拼 icon）
   - 步骤文字：**马善政 / 站酷快乐体** + **淡黄荧光笔底纹** + 行首 **①②③** 圈号
   - 底部 **唠唠叨叨** 黄框小贴士

## 步骤叙事插画（Plan B）

每步左侧 = **`stepIllustrationUrl`**（独立动作场景，如腌制、煮粥、翻炒）。

| sceneId | 典型步骤 |
|---------|----------|
| `board_marinate` | 腌、用酱油调味 |
| `board_cut` | 切、切丁、手撕 |
| `pot_porridge_simmer` | 煮粥、七分熟 |
| `pot_season_finish` | 加盐、出锅调味 |
| `wok_stir_fry` | 炒、翻炒 |
| `wok_pan_fry` | 煎、烙 |
| … | 共 15 个，见 illustration-style-bible.md |

实现：`resolve_step_illustration()` in `illustration_resolver.py`。  
无 PNG 时网页显示「待出图」，**禁止**几何 SVG 回退。

## 中国计量（必遵）

详见 [`measurement-cn.md`](measurement-cn.md)：

- 温度用 **℃**，重量用 **克/斤**，体积用 **毫升**
- 禁止输出华氏、盎司、cup 及「美国烹饪计量单位」脚注
- 批量商用配方须换算为家庭份量后再展示
