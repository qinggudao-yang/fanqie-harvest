# fanqie-harvest

**番茄小说全量数据采集工具** — 给书名或 book_id，一键获取完整正文、书籍信息、章评、段评（含段落级精确定位）。

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## ✨ 特性

| 功能 | 说明 | 需要登录 |
|---|---|---|
| 🔍 **搜索** | 按书名找 book_id | ❌ |
| 📖 **书籍信息** | 书名/作者/简介/章节数 | ❌ |
| 📄 **完整正文** | 无字体混淆的明文，数字完整 | ❌ |
| 💬 **段评** | **段落级评论 + 精确定位** | ❌ |
| 🗨️ **章评** | 章节级评论 | ⚠️ 是 |

**不需要模拟器、不需要 APP、不需要登录**（章评除外）。

---

## 🚀 快速开始

```bash
# 1. 环境自检
python check.py

# 2. 按书名搜索
python bookinfo.py search "关键词"

# 3. 获取正文
python fanqie.py text <book_id>

# 4. 获取段评
python fanqie.py segments <book_id>

# 5. 导出为 JSONL
python fanqie.py export <book_id> mybook
```

---

## 📊 段评数据样例

```json
{
  "chapter_title": "第6章 先把身体养好",
  "para_index": 1,
  "para_src_content": "【余额：19.80元】",
  "body_para_aligned": true,
  "text": "餐店老板:一直出餐，账怎么对不上啊，干一个月赚2块！？",
  "digg_count": 150,
  "reply_count": 1,
  "created_iso": "2026-07-23T12:37:29Z",
  "position": {
    "start_para_index": 1, "end_para_index": 1,
    "start_word_pos": 0, "end_word_pos": 11
  }
}
```

**每条评论都能定位到具体段落**，而非仅"某章"。

---

## 🔬 技术要点（踩坑记录）

### 1. 必须用官方通道

第三方镜像站存在**系统性失真**。实测对比：

| 书 | 官方字数 | 镜像字数 | 保留率 |
|---|---|---|---|
| 书A | 1,540,100 | 1,488,111 | 96.6% |
| 书B | 1,060,411 | 1,022,371 | 96.4% |
| **书C** | **2,878,442** | **1,399,044** | **48.6%** |

失真形式为**删句与改词**（如"孤身一人"→"独自一人"、"如今"→"今年"）。

### 2. PUA 字体混淆

番茄用私有区字符（U+E000–U+F8FF）替换数字与部分汉字，
渲染时才通过 woff2 还原。**直接抓网页会得到缺字文本**。
官方通道返回完全明文（0 个 PUA 字符）。

### 3. 段落索引偏移 +1

段评的 `para_index` 需要 **+1** 才能对应纯文本段落：

```
段评 para_index=1  →  正文 paras[2]
验证：856/912 = 93.9% 匹配率
```

工具已自动处理。

### 4. 约 6% 不对齐 = 内容修订

部分段评引用的段落在现行正文中已不存在（作者修订所致）。
导出时自动标注 `body_para_aligned: false`。
这**不是数据错误**，而是内容演变的历史痕迹。

### 5. 风控

段评有频率限制：

```yaml
segment_comments_workers: 2   # 不可调高
实际速率: 20-40 秒/章
断点续传: 支持
```

---

## 📁 输出结构

```
data/<book_id>/
  downloaded_chapters.jsonl    正文（含段落索引属性）
  segment_comments/            段评（按章 JSON）
research/data/raw/
  fanqie_official_full/        纯文本正文
  fanqie_segment_comments/flat/扁平段评 JSONL
```

---

## ⚙️ 依赖

- **Python 3.8+**（仅标准库）
- **Tomato-Novel-Downloader v2.4.15**（需自行下载，见 [INSTALL.md](INSTALL.md)）

> 核心下载能力来自开源项目 [Tomato-Novel-Downloader](https://github.com/zhongbai2333/Tomato-Novel-Downloader)（作者 zhongbai2333）。本工具在其之上做了封装与增强，详见 [ORIGINALITY.md](ORIGINALITY.md)。

---

## 📜 合规声明

- 本工具**仅供学习研究**使用
- 采集内容版权归原作者与平台所有，**不得商用或再分发**
- 评论数据使用时必须**脱敏**（工具导出已自动剔除用户标识）
- 请遵守目标网站用户协议与相关法律法规

---

## 📄 许可

MIT License（详见 [LICENSE](LICENSE)）

`bin/tnd.exe` 为第三方作品，遵循其原有许可。