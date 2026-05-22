"""access_token 文件缓存。

微信 access_token 有效期 7200 秒，且每天获取次数有限，必须缓存复用。
本模块负责：读缓存、未过期直接返回、过期或失效时重新拉取并写回。
用一个 sidecar 锁文件防止多进程并发拉取（跨平台，不依赖 fcntl/msvcrt）。
"""

import json
import os
import time

import requests

TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
DEFAULT_CACHE = os.path.expanduser("~/.cache/ni-skill/wechat_token.json")
BUFFER_SECONDS = 200   # 提前 200 秒视为过期，留安全余量
LOCK_TIMEOUT = 10      # 抢锁最长等待秒数，超时视为陈旧锁强行夺取


class _FileLock:
    """基于 O_CREAT|O_EXCL 原子创建的跨平台文件锁。"""

    def __init__(self, target_path, timeout=LOCK_TIMEOUT):
        self.lock_path = target_path + ".lock"
        self.timeout = timeout
        self.fd = None

    def __enter__(self):
        start = time.time()
        while True:
            try:
                self.fd = os.open(
                    self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY
                )
                return self
            except FileExistsError:
                if time.time() - start > self.timeout:
                    # 锁可能是上次崩溃残留的陈旧锁，夺取它
                    try:
                        os.unlink(self.lock_path)
                    except OSError:
                        pass
                    continue
                time.sleep(0.1)

    def __exit__(self, *exc):
        if self.fd is not None:
            os.close(self.fd)
        try:
            os.unlink(self.lock_path)
        except OSError:
            pass


def _read_cache(cache_path):
    """读缓存，未过期返回 token，否则返回 None。"""
    try:
        with open(cache_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if data.get("expires_at", 0) > time.time():
            return data.get("token")
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        pass
    return None


def _write_cache(cache_path, token, expires_in):
    os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
    data = {"token": token, "expires_at": time.time() + expires_in - BUFFER_SECONDS}
    with open(cache_path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def _fetch_token(appid, secret):
    resp = requests.get(
        TOKEN_URL,
        params={
            "grant_type": "client_credential",
            "appid": appid,
            "secret": secret,
        },
        timeout=10,
    )
    data = resp.json()
    if "access_token" not in data:
        errmsg = data.get("errmsg", data)
        raise RuntimeError(f"拿 access_token 失败：{errmsg}")
    return data["access_token"], data.get("expires_in", 7200)


def get_token(appid, secret, cache_path=DEFAULT_CACHE, force_refresh=False):
    """返回可用的 access_token，优先用缓存。

    force_refresh=True 时跳过缓存强制重拉（40001 失效后用）。
    """
    cache_path = os.path.expanduser(cache_path)
    if not force_refresh:
        token = _read_cache(cache_path)
        if token:
            return token
    with _FileLock(cache_path):
        # 双重检查：抢锁期间可能有别的进程已写好新 token
        if not force_refresh:
            token = _read_cache(cache_path)
            if token:
                return token
        token, expires_in = _fetch_token(appid, secret)
        _write_cache(cache_path, token, expires_in)
        return token


def invalidate(cache_path=DEFAULT_CACHE):
    """删缓存，下次 get_token 会重新拉取。收到 40001 时调用。"""
    cache_path = os.path.expanduser(cache_path)
    try:
        os.unlink(cache_path)
    except OSError:
        pass
