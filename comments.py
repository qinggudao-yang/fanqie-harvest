# -*- coding: utf-8 -*-
"""章评/书评采集：直接调用官方接口（无风控，速度快）"""
import json, os, time, gzip, urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS = os.path.join(ROOT, "creds.json")
OUT = os.path.join(ROOT, "research/data/raw/fanqie_comments")
BASE = "https://api5-normal-sinfonlinec.fqnovel.com"

_COMMON = ("klink_egdi=AAJ4JpgSxwN5yAURwAEsDkHZXnR7Wi5fglXE87OuBITHqerf19S4FhZA"
           "&iid=4210494720256314&device_id=23554262072875&ac=wifi&channel=vivo_1967_64"
           "&aid=1967&app_name=novelapp&version_code=73090&version_name=7.3.9"
           "&device_platform=android&os_version=14")


def _load_creds():
    if not os.path.exists(CREDS):
        raise RuntimeError("缺少凭据文件: " + CREDS)
    return json.load(open(CREDS, encoding="utf-8"))


def _get(url, retries=3):
    c = _load_creds()
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "com.dragon.read/7.3.9 (Linux; U; Android 14; zh_CN; x86_64)",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Tt-Token": c["token"],
                "Cookie": c["cookie"],
            })
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return json.loads(data.decode("utf-8"))
        except Exception:
            if i == retries - 1:
                return None
            time.sleep(2)
    return None


def fetch_chapter_comments(book_id, item_id, count=20, max_pages=10):
    """采集单章评论（含分页）"""
    out, offset = [], 0
    for _ in range(max_pages):
        url = (BASE + "/reading/ugc/novel_comment/item/v1/?item_id=" + str(item_id)
               + "&book_id=" + str(book_id) + "&offset=" + str(offset)
               + "&count=" + str(count) + "&" + _COMMON)
        j = _get(url)
        if not j or j.get("code") != 0:
            break
        d = j.get("data") or {}
        cs = d.get("comment") or []
        out.extend(cs)
        if not d.get("has_more"):
            break
        offset = d.get("next_offset", offset + count)
        time.sleep(0.4)
    return out


def clean(c, item_id):
    """只保留研究字段（剔除用户隐私）"""
    return {
        "comment_id": c.get("comment_id"),
        "item_id": item_id,
        "text": c.get("text"),
        "digg_count": c.get("digg_count"),
        "reply_count": c.get("reply_count"),
        "disagree_count": c.get("disagree_count"),
        "create_timestamp": c.get("create_timestamp"),
        "has_author_digg": c.get("has_author_digg"),
        "num_lines": c.get("num_lines"),
        "read_duration": c.get("read_duration"),
        "level": c.get("level"),
    }


def harvest(book_id, item_ids, key, sleep=0.8):
    """批量采集章评"""
    os.makedirs(OUT, exist_ok=True)
    out_path = os.path.join(OUT, key + "_chapter_comments.jsonl")
    n = 0
    with open(out_path, "w", encoding="utf-8") as fo:
        for i, iid in enumerate(item_ids):
            try:
                cs = fetch_chapter_comments(book_id, iid)
                for c in cs:
                    fo.write(json.dumps(clean(c, iid), ensure_ascii=False) + "\n")
                n += len(cs)
                fo.flush()
            except Exception as e:
                print("  第%d章失败: %s" % (i + 1, e))
            if i % 50 == 0:
                print("  [%d/%d] %d条" % (i + 1, len(item_ids), n))
            time.sleep(sleep)
    return {"total": n, "path": out_path}