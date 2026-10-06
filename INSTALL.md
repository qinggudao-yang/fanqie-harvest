# 安装与使用

## 一、前置条件

| 项目 | 要求 |
|---|---|
| 操作系统 | Windows 10/11（64位）|
| Python | **3.8+**（无需第三方包，标准库即可）|
| 网络 | 能访问 fanqienovel.com |
| 磁盘 | 约 50MB（工具）+ 数据空间 |

**不需要**：模拟器、APP、账号登录。

## 二、准备下载器（首次必做）

本仓库**不附带**下载器可执行文件，请自行下载：

1. 访问 https://github.com/zhongbai2333/Tomato-Novel-Downloader/releases
2. 下载 `TomatoNovelDownloader-Win64-v2.4.15.exe`
3. 重命名为 `tnd.exe`，放入本目录的 `bin/` 子目录

```
fanqie-harvest/
  bin/
    tnd.exe    ← 放这里
```

> 核心下载能力来自该项目，感谢作者 zhongbai2333。

## 三、快速验证

```bash
cd fanqie-harvest
python check.py
```

看到 `环境就绪，可开始采集` 即可使用。

## 四、基本用法

### 3.1 按书名找书

```bash
python bookinfo.py search "关键词"
```

输出示例：
```json
[{"book_id": "7660134591012817982", "title": "穿越乱世：每天一份拼好饭", "author": "与天竞自由"}]
```

### 3.2 获取书籍信息

```bash
python fanqie.py info <book_id>
```

### 3.3 下载完整正文

```bash
python fanqie.py text <book_id>
# 或指定范围（第1-50章）
python fanqie.py text <book_id> 1 50
```

**输出**：
```
data/<book_id>/downloaded_chapters.jsonl   ← 结构化
data/<book_id>/...                          ← 自动转换
```

**速度参考**：1282章约3分钟。

### 3.4 采集段评（段落级评论）

```bash
python fanqie.py segments <book_id>
# 或指定范围
python fanqie.py segments <book_id> 1 100
```

**注意**：有风控限速，约 **20-40 秒/章**。支持断点续传。

### 3.5 采集章评（需登录凭据）

```bash
python fanqie.py comments <book_id> <标识>
```

需要一个 `creds.json`（见下节）。

### 3.6 导出段评（推荐）

```bash
python fanqie.py export <book_id> <标识>
```

输出扁平 JSONL，每条评论一行，含段落定位与对齐标注。

## 五、章评凭据配置（可选）

**仅章评功能需要**。正文、段评、搜索均不需要。

在工具目录创建 `creds.json`：

```json
{
  "token": "你的 X-Tt-Token",
  "cookie": "你的 Cookie 字符串"
}
```

**如何获取**：从已登录番茄 APP 的 Android 设备提取（需 root）：

```bash
adb shell "su 0 cat /data/data/com.dragon.read/shared_prefs/token_shared_preference.xml"
adb shell "su 0 cat /data/data/com.dragon.read/shared_prefs/cookieStore.xml"
```

**注意**：凭据属于个人账号，**自行使用，不要分享给他人**。

## 六、输出结构

```
data/
  <book_id>/
    downloaded_chapters.jsonl    正文（原始HTML，含段落索引属性）
    segment_comments/            段评（按章JSON）
    images/                      评论配图与头像
research/data/raw/
  fanqie_official_full/          转换后的纯文本正文
  fanqie_segment_comments/
    raw/                         段评原始备份
    flat/                        扁平导出（推荐使用）
  fanqie_comments/               章评
```

## 七、常见问题

### Q: 段评卡住不动了？

A: 触发了风控。等待 30-60 分钟后重新运行同一命令（会**断点续传**）。
也可降低并发：编辑 `data/config.yml`，设 `segment_comments_workers: 1`。

### Q: 正文有乱码/缺字？

A: 若用官方通道（本工具的 `text` 命令）不会出现。
若你自己抓网页，会遇到 PUA 字体混淆问题。

### Q: 段评与正文对不上？

A: 工具已自动处理 `+1` 偏移。若仍有不对齐，查看 `body_para_aligned` 字段——
为 `false` 说明该段落后来被作者修改过（正常现象）。

### Q: 能不能批量下载多本书？

A: 可以：
```bash
for id in <id1> <id2> <id3>; do
  python fanqie.py text $id
done
```

## 八、合规与免责

- 本工具**仅供学习研究**使用
- 采集内容版权归原作者与平台所有，**不得商用或再分发**
- 评论数据使用时必须**脱敏**（去除用户标识）
- 请遵守目标网站的用户协议与相关法律法规
- 使用者自行承担因不当使用产生的责任