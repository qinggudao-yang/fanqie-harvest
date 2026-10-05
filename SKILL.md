---
name: fanqie-harvest
description: 番茄小说全量数据采集。给书名或book_id，自动获取完整正文（无字体混淆）、书籍信息、目录、章评、段评（含段落级精确定位）。用于网文语料构建、读者反应研究、内容分析。
---

# 番茄小说数据采集

## 适用场景

- 需要某本番茄小说的**完整全文**（含数字、无乱码）
- 需要**读者评论数据**（章评/段评）做反应研究
- 需要**书籍元数据**（作者、简介、章节数、评分）
- 批量构建网文语料库

## 快速使用

工具位置：`tools/fanqie/`

```bash
cd tools/fanqie

# 1) 按书名找 book_id
python bookinfo.py search "书名关键词"

# 2) 获取全部数据
python fanqie.py info <book_id>        # 书籍信息
python fanqie.py text <book_id>        # 完整正文
python fanqie.py segments <book_id>    # 段评（段落级，有风控）
python fanqie.py comments <book_id> <key>  # 章评（章节级，无风控）
python fanqie.py status                # 进度
python fanqie.py export <book_id> <key>    # 导出段评
```

## 关键事实（避免踩坑）

### 1. 必须用官方通道

第三方镜像站（如 dongtinghighschool.com、jgywy.com）存在**系统性失真**：

| 书 | 镜像保留率 |
|---|---|
| 类型A | 96%（可用）|
| 类型B | **48.6%（严重缺失）** |

**务必用官方通道**（本工具的 `text` 命令）。

### 2. 字体混淆问题

番茄官网/APP 用 PUA 私有区字符（U+E000–U+F8FF）替换数字与部分汉字，
渲染时才用 woff2 字体显示。**直接抓网页会得到乱码或缺字**。

官方下载通道返回**完全明文**（0 个 PUA 字符），无需字体反混淆。

### 3. 段评 vs 章评

| | 章评 | 段评 |
|---|---|---|
| 粒度 | 整章 | **段落+字位置** |
| 字段 | 无位置 | `para_index`/`start_word_pos`/`end_word_pos` |
| 段落原文 | 无 | **`para_src_content`** |
| 风控 | 无 | **有（并发≤2）** |
| 速度 | 快 | 20-40秒/章 |

**优先段评**（粒度细，能回答"哪一段让读者炸了"）。

### 4. 段落索引必须 +1

```
段评 para_index=1  →  纯文本段落 paras[2]
```

工具已自动处理。验证匹配率 93.9%。

### 5. 约6%不对齐 = 内容修订（非错误）

段评保留的是**评论发布时的段落**。作者改文后，段评仍指向旧版本，
表现为 `body_para_aligned: false`。这是**内容演变的证据**，有研究价值。

### 6. 风控参数

```
segment_comments_workers: 2   # 不可调高
等待间隔: 2000-5000ms
断点续传: 支持（中断后重跑同范围会跳过已缓存）
```

触发风控后表现为**长时间停滞**（>20分钟无新文件），此时应降低并发或等待。

## 输出位置

```
research/data/raw/
  fanqie_official_full/        正文（*_chapters.jsonl + *_full.txt）
  fanqie_segment_comments/     段评（raw/ 原始 + flat/ 扁平）
  fanqie_comments/             章评
```

## 隐私边界

导出脚本**已剔除**用户ID/昵称/头像，仅保留：
评论内容、点赞数、回复数、时间、段落位置。

采集数据仅供研究使用，不得用于商业分发。

## 依赖

| 组件 | 说明 |
|---|---|
| Python 3.11+ | 标准库，无需第三方包 |
| Tomato-Novel-Downloader | 提供官方通道，需放于 `D:/ldsetup/tnd.exe` |
| 凭据 | `.work/duanping/creds.json`（章评需要）|