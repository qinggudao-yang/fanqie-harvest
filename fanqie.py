#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""番茄小说数据采集 CLI

用法:
  python fanqie.py info <book_id>              书籍信息
  python fanqie.py toc <book_id>               目录
  python fanqie.py text <book_id> [start end]  正文
  python fanqie.py segments <book_id> [s e]    段评
  python fanqie.py comments <book_id> <key>    章评
  python fanqie.py status                      进度
  python fanqie.py export <book_id> <key>      导出段评
  python fanqie.py all <book_id> <key>         全量（正文+段评+章评）
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import service, harvest, comments, bookinfo


def cmd_info(book_id):
    i = bookinfo.get_book_info(book_id)
    print(json.dumps(i, ensure_ascii=False, indent=1))
    return i


def cmd_toc(book_id):
    ids = bookinfo.get_toc(book_id)
    print("章节数: %d" % len(ids))
    return ids


def cmd_text(book_id, start=None, end=None):
    if not service.start():
        print("[!] 下载器启动失败"); return False
    print("[*] 采集正文 %s %s-%s" % (book_id, start, end))
    return harvest.fetch_text(book_id, start, end)


def cmd_segments(book_id, start=None, end=None, workers=2):
    if not service.start():
        print("[!] 下载器启动失败"); return False
    print("[*] 采集段评 %s %s-%s (workers=%d)" % (book_id, start, end, workers))
    return harvest.fetch_segments(book_id, start, end, workers=workers)


def cmd_comments(book_id, key):
    ids = bookinfo.get_toc(book_id)
    if not ids:
        print("[!] 无法获取目录"); return False
    print("[*] 采集章评 %s (%d章)" % (book_id, len(ids)))
    r = comments.harvest(book_id, ids, key)
    print("完成: %d 条 -> %s" % (r["total"], r["path"]))
    return r


def cmd_status():
    print("下载器:", "运行中" if service.is_running() else "未运行")
    for j in service.get_jobs():
        p = j.get("progress") or {}
        print("  job%s %s 章节%s/%s 段评%s/%s" % (
            j.get("id"), j.get("state"), p.get("saved_chapters"),
            p.get("chapter_total"), p.get("comment_saved"), p.get("comment_total")))


def cmd_export(book_id, key):
    r = harvest.export_segments(book_id, key)
    if isinstance(r, dict):
        print("导出 %d 条（未对齐 %d）-> %s" % (r["total"], r["unaligned"], r["path"]))
    return r


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    c = sys.argv[1]
    a = sys.argv[2:]
    if c == "info" and a:
        cmd_info(a[0])
    elif c == "toc" and a:
        cmd_toc(a[0])
    elif c == "text" and a:
        cmd_text(a[0], int(a[1]) if len(a) > 1 else None, int(a[2]) if len(a) > 2 else None)
    elif c == "segments" and a:
        cmd_segments(a[0], int(a[1]) if len(a) > 1 else None, int(a[2]) if len(a) > 2 else None)
    elif c == "comments" and len(a) >= 2:
        cmd_comments(a[0], a[1])
    elif c == "status":
        cmd_status()
    elif c == "export" and len(a) >= 2:
        cmd_export(a[0], a[1])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()