# -*- coding: utf-8 -*-
"""番茄小说数据采集：正文、章评、段评"""
import json, os, time, re, glob
import service

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "research/data/raw")


def _book_dir(book_id):
    return os.path.join(ROOT, str(book_id))


def wait_job(book_id, timeout=7200, poll=30, quiet=False):
    """等待任务完成"""
    t0 = time.time()
    while time.time() - t0 < timeout:
        jobs = service.get_jobs()
        j = None
        for x in jobs:
            if str(x.get("book_id")) == str(book_id):
                j = x; break
        if j is None:
            return True
        st = j.get("state")
        p = j.get("progress") or {}
        if not quiet:
            print("  %s 章节%s/%s 段评%s/%s" % (st, p.get("saved_chapters"), p.get("chapter_total"),
                                                p.get("comment_saved"), p.get("comment_total")))
        if st in ("done", "failed"):
            return st == "done"
        time.sleep(poll)
    return False


def fetch_text(book_id, start=None, end=None, wait=True):
    """采集正文（自动关闭段评以加速）"""
    service.set_config(enable_segment_comments=False)
    service.create_job(book_id, start, end)
    if wait:
        return wait_job(book_id)
    return True


def fetch_segments(book_id, start=None, end=None, wait=True, workers=2):
    """采集段评（低并发防风控）"""
    service.set_config(
        enable_segment_comments=True,
        segment_comments_workers=workers,
        segment_comments_top_n=10,
        novel_format="epub",
    )
    service.create_job(book_id, start, end)
    if wait:
        return wait_job(book_id)
    return True


def scan_segments(book_id):
    """扫描段评目录，返回统计"""
    d = os.path.join(_book_dir(book_id), "segment_comments")
    if not os.path.isdir(d):
        return {"files": 0, "with_data": 0, "reviews": 0, "paras": 0}
    files = [f for f in os.listdir(d) if f.endswith(".json")]
    wd = rv = pr = 0
    for f in files:
        try:
            j = json.load(open(os.path.join(d, f), encoding="utf-8"))
        except Exception:
            continue
        ps = [(k, v) for k, v in (j.get("paras") or {}).items() if v.get("count", 0) > 0]
        if ps:
            wd += 1
        pr += len(ps)
        for _, p in ps:
            rv += len((p.get("detail") or {}).get("reviews") or [])
    return {"files": len(files), "with_data": wd, "reviews": rv, "paras": pr}


def export_segments(book_id, key):
    """导出段评为扁平JSONL（关联正文+对齐标注，剔除用户信息）"""
    src = os.path.join(_book_dir(book_id), "segment_comments")
    if not os.path.isdir(src):
        return 0
    ch_path = os.path.join(OUT, "fanqie_official_full", key + "_chapters.jsonl")
    body = {}
    if os.path.exists(ch_path):
        for line in open(ch_path, encoding="utf-8"):
            line = line.strip()
            if line:
                c = json.loads(line)
                body[str(c["chapter_id"])] = c
    out_dir = os.path.join(OUT, "fanqie_segment_comments", "flat")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, key + "_segment_comments.jsonl")
    n = mis = 0
    fo = open(out_path, "w", encoding="utf-8")
    for f in sorted(os.listdir(src)):
        if not f.endswith(".json"):
            continue
        cid = f[:-5]
        try:
            j = json.load(open(os.path.join(src, f), encoding="utf-8"))
        except Exception:
            continue
        ch = body.get(cid)
        paras = ch["text"].split("\n\n") if ch else []
        for idx_s, p in (j.get("paras") or {}).items():
            det = p.get("detail") or {}
            meta = det.get("meta") or {}
            pi = int(idx_s)
            bp = paras[pi + 1] if ch and 0 <= pi + 1 < len(paras) else None
            for r in (det.get("reviews") or []):
                sp = (r.get("para_src_content") or meta.get("para_content") or "").strip()
                aligned = bool(bp and sp and bp.strip().startswith(sp[:10]))
                if not aligned:
                    mis += 1
                fo.write(json.dumps({
                    "chapter_id": cid,
                    "chapter_title": ch["title"] if ch else None,
                    "chapter_num": ch["num"] if ch else None,
                    "para_index": pi,
                    "para_src_content": sp,
                    "body_para_aligned": aligned,
                    "comment_id": r.get("comment_id"),
                    "text": r.get("text"),
                    "digg_count": r.get("digg_count"),
                    "reply_count": r.get("reply_count"),
                    "created_iso": r.get("created_iso"),
                    "position": r.get("position"),
                }, ensure_ascii=False) + "\n")
                n += 1
    fo.close()
    return {"total": n, "unaligned": mis, "path": out_path}