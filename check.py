#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""环境自检：验证工具可用性"""
import sys, os, json, subprocess, urllib.request

OK = "[OK]"; FAIL = "[!!]"; WARN = "[??]"
issues = []


def check_python():
    v = sys.version_info
    if v.major == 3 and v.minor >= 8:
        print("%s Python %d.%d.%d" % (OK, v.major, v.minor, v.micro))
        return True
    print("%s Python 版本过低（需3.8+），当前 %d.%d" % (FAIL, v.major, v.minor))
    issues.append("Python版本")
    return False


def check_network():
    try:
        req = urllib.request.Request("https://fanqienovel.com", headers={"User-Agent": "Mozilla/5.0"})
        urllib.request.urlopen(req, timeout=10)
        print("%s 网络连通（fanqienovel.com）" % OK)
        return True
    except Exception as e:
        print("%s 网络不通: %s" % (FAIL, str(e)[:60]))
        issues.append("网络")
        return False


def check_downloader():
    exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin", "tnd.exe")
    if os.path.exists(exe):
        size = os.path.getsize(exe) / 1048576
        print("%s 下载器存在 (%.1f MB)" % (OK, size))
        return True
    print("%s 缺少下载器: %s" % (FAIL, exe))
    issues.append("下载器")
    return False


def check_modules():
    d = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, d)
    ok = True
    for m in ["service", "harvest", "comments", "bookinfo"]:
        try:
            __import__(m)
            print("%s 模块 %s" % (OK, m))
        except Exception as e:
            print("%s 模块 %s 导入失败: %s" % (FAIL, m, str(e)[:60]))
            ok = False
            issues.append("模块" + m)
    return ok


def check_search():
    """实测搜索接口（无认证）"""
    try:
        d = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, d)
        import bookinfo
        r = bookinfo.search("测试")
        if r:
            print("%s 搜索接口可用（返回%d条）" % (OK, len(r)))
            return True
        print("%s 搜索接口无返回" % WARN)
        return False
    except Exception as e:
        print("%s 搜索失败: %s" % (FAIL, str(e)[:60]))
        issues.append("搜索")
        return False


def check_creds():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "creds.json")
    if os.path.exists(p):
        print("%s 登录凭据存在（章评功能可用）" % OK)
        return True
    print("%s 无登录凭据 — 仅影响章评功能（comments）" % WARN)
    print("     正文/段评/搜索 均不受影响")
    return False


def main():
    print("=" * 50)
    print("fanqie-harvest 环境自检")
    print("=" * 50)
    check_python()
    check_network()
    check_downloader()
    check_modules()
    check_search()
    check_creds()
    print("=" * 50)
    if issues:
        print("存在问题: " + ", ".join(issues))
    else:
        print("环境就绪，可开始采集")
        print("")
        print("快速开始:")
        print("  python bookinfo.py search \"书名\"")
        print("  python fanqie.py text <book_id>")
        print("  python fanqie.py segments <book_id>")
    print("=" * 50)


if __name__ == "__main__":
    main()