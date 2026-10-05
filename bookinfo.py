# -*- coding: utf-8 -*-
"""书籍信息：搜索、元数据、目录（走官网，无需登录）"""
import json, re, gzip, urllib.request, urllib.parse, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36"


def _get(url, headers=None, timeout=25):
    h = {"User-Agent": UA, "Accept": "*/*", "Accept-Encoding": "gzip"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                data = gzip.decompress(data)
            return data.decode("utf-8", "replace")
    except Exception:
        return ""


def get_book_page(book_id):
    return _get("https://fanqienovel.com/page/" + str(book_id))


def get_toc(book_id):
    html = get_book_page(book_id)
    ids, seen = [], set()
    for m in re.finditer(r"/reader/(\d{15,})", html):
        i = m.group(1)
        if i not in seen:
            seen.add(i); ids.append(i)
    return ids


def _clean_title(t):
    """清理标题后缀"""
    for sep in ["_", "-", "|"]:
        if sep in t:
            t = t.split(sep)[0]
    t = re.sub(r"(番茄小说|免费阅读|在线阅读|最新章节).*$", "", t)
    t = t.replace("最新章节", "").strip()
    return t.strip()


def get_book_info(book_id):
    html = get_book_page(book_id)
    info = {"book_id": str(book_id)}
    m = re.search(r"<title>([^<]+)</title>", html)
    if m:
        info["title"] = _clean_title(m.group(1))
    # 页面内 h1 或书名标签
    m = re.search(r"<h1[^>]*>([^<]{2,60})</h1>", html)
    if m:
        info["title_h1"] = m.group(1).strip()
    m = re.search(r"作者[：:]\s*</?[^>]*>?\s*([^<\s]{2,20})", html)
    if m:
        info["author"] = m.group(1)
    m = re.search(r"作品简介[\s\S]{0,200}?<[^>]+>([^<]{20,600})", html)
    if m:
        info["description"] = m.group(1).strip()
    m = re.search(r"目录(\d+)章", html)
    if m:
        info["chapter_count"] = int(m.group(1))
    # 评分
    m = re.search(r"([0-9]\.[0-9])\s*分", html)
    if m:
        info["score"] = m.group(1)
    if "chapter_count" not in info:
        info["chapter_count"] = len(get_toc(book_id))
    return info


def search(keyword):
    """搜索书籍（用官方搜索接口）"""
    q = urllib.parse.quote(keyword)
    url = ("https://novel.snssdk.com/api/novel/channel/homepage/search/search/v1/"
           "?aid=1967&q=" + q + "&offset=0&count=10")
    txt = _get(url, headers={"Accept": "application/json"})
    if not txt:
        return []
    try:
        j = json.loads(txt)
    except Exception:
        return []
    out = []
    data = j.get("data") or {}
    items = data.get("ret_data") or data.get("book_data") or []
    for it in items:
        bid = it.get("book_id") or it.get("id")
        if bid:
            out.append({
                "book_id": str(bid),
                "title": it.get("book_name") or it.get("title"),
                "author": it.get("author"),
                "word_count": it.get("word_number"),
            })
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2 and sys.argv[1] == "search":
        print(json.dumps(search(sys.argv[2]), ensure_ascii=False, indent=1))
    elif len(sys.argv) > 1:
        print(json.dumps(get_book_info(sys.argv[1]), ensure_ascii=False, indent=1))