# -*- coding: utf-8 -*-
"""下载器服务管理：启动/停止/配置 Tomato-Novel-Downloader"""
import json, os, subprocess, time, sys, urllib.request

EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "tnd.exe")
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PORT = 18423
BASE = "http://127.0.0.1:" + str(PORT)


def _http(method, path, body=None, timeout=30):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"_error": str(e)}


def is_running():
    r = _http("GET", "/api/status", timeout=5)
    return "_error" not in r


def start(wait=30):
    """启动下载器（后台）"""
    if is_running():
        return True
    if not os.path.exists(EXE):
        print("[!] 下载器不存在: " + EXE)
        return False
    os.makedirs(DATA_DIR, exist_ok=True)
    logf = open(os.path.join(DATA_DIR, "server.log"), "a", encoding="utf-8")
    flags = 0x00000008 if os.name == "nt" else 0
    subprocess.Popen([EXE, "--server", "--data-dir", DATA_DIR],
                     stdout=logf, stderr=logf, creationflags=flags)
    for i in range(wait):
        time.sleep(1)
        if is_running():
            return True
    return False


def stop():
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/IM", "tnd.exe"], capture_output=True)
    return True


def get_config():
    return _http("GET", "/api/config/full")


def set_config(**kw):
    """设置配置（segment_comments 等）"""
    return _http("POST", "/api/config/full", kw)


def get_jobs():
    r = _http("GET", "/api/jobs")
    return r.get("items", []) if isinstance(r, dict) else []


def create_job(book_id, start=None, end=None):
    body = {"book_id": str(book_id)}
    if start is not None: body["range_start"] = start
    if end is not None: body["range_end"] = end
    return _http("POST", "/api/jobs", body)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "start":
        print("启动:", start())
    elif cmd == "stop":
        print("停止:", stop())
    elif cmd == "status":
        print("运行中" if is_running() else "未运行")
        for j in get_jobs():
            p = j.get("progress") or {}
            print("  job%d %s %s/%s" % (j.get("id",0), j.get("state"), p.get("saved_chapters"), p.get("chapter_total")))
    elif cmd == "config":
        print(json.dumps(get_config(), ensure_ascii=False, indent=1))