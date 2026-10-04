#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ni-book-downloader / book.py

按书名下载电子书，区分文字版（epub/mobi/azw3/fb2/txt）与版式版（pdf）。

来源：
  libgen  LibGen（libgen.li，免账号，适合英文书）
  zlib    Z-Library（需在配套 Chrome 中登录，免费账号每日 ~10 本配额，适合中文书）
  aa      Anna's Archive（beta，慢速免费通道）
  github  GitHub 电子书索引（城通网盘链接，中文文字版主力）
  web     全网搜索兜底（网盘链接交用户处理；直接文件/网盘链接自动尝试下载）

用法：
  python book.py setup [--launch-chrome]                    环境诊断 / 拉起 Chrome
  python book.py search "书名" [--format text|pdf|any] [--web]  列候选（不下载）
  python book.py get --source zlib --dl /dl/xxx --name 书名  下载指定候选
  python book.py get --source github --link URL --name 书名 --ext epub
  python book.py auto "书名" --format text [-o DIR]         搜索+选优+下载（全失败自动全网兜底）
  python book.py batch manifest.json -o DIR                 批量
  python book.py quota                                      Z-Library 配额
  python book.py extract-pdf book.pdf -o book.txt           PDF 文字层提取

环境变量：
  NI_BOOK_PROXY           代理，默认 http://127.0.0.1:7890
  NI_BOOK_CDP_PORT        Chrome 调试端口，默认 9222
  NI_BOOK_CHROME          Chrome/Edge 可执行文件路径（默认自动查找）
  NI_BOOK_CHROME_PROFILE  CDP Chrome 用户目录（默认 %LOCALAPPDATA%/ni-book-downloader/chrome-profile）
"""
import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unicodedata
import urllib.parse
import urllib.request
import warnings

warnings.filterwarnings('ignore')
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------

TEXT_EXTS = ('epub', 'mobi', 'azw3', 'fb2', 'txt', 'rtf')
PDF_EXTS = ('pdf',)
ALL_EXTS = TEXT_EXTS + PDF_EXTS + ('djvu', 'cbz', 'cbr')

STOPWORDS = {'the', 'a', 'an', 'of', 'to', 'and', 'on', 'in', 'for', 'with', 'your', 'how', 'so',
             'will', 's', 'is', 'it', 'that', 'this', 'from', 'at', 'by', 'or'}
BAD_WORDS = ['summary of', 'study guide', 'workbook', 'companion to', 'quicklet', 'book review',
             'analysis of', 'coloring book', 'unofficial', 'cliffsnotes', 'sparknotes',
             'key takeaways', 'chapter by chapter']
EXT_SCORE = {'epub': 2.0, 'txt': 1.6, 'pdf': 1.5, 'mobi': 1.2, 'azw3': 1.2, 'fb2': 1.1, 'rtf': 1.0}
MIN_SIZE = 50 * 1024
MAX_SIZE = 500 * 1024 * 1024


def env(name, default=''):
    v = os.environ.get(name, '')
    return v if v else default


def default_profile_dir():
    base = env('LOCALAPPDATA') or os.path.expanduser('~/.local/share')
    return os.path.join(base, 'ni-book-downloader', 'chrome-profile')


def default_cache_dir():
    base = env('LOCALAPPDATA') or os.path.expanduser('~/.local/share')
    return os.path.join(base, 'ni-book-downloader', 'cache')


CFG = {
    'proxy': env('NI_BOOK_PROXY', 'http://127.0.0.1:7890'),
    'cdp_port': int(env('NI_BOOK_CDP_PORT', '9222')),
    'chrome': env('NI_BOOK_CHROME', ''),
    'chrome_profile': env('NI_BOOK_CHROME_PROFILE', default_profile_dir()),
    'cache_dir': env('NI_BOOK_CACHE', default_cache_dir()),
    'search_engines': env('NI_BOOK_SEARCH_ENGINES', 'bing,baidu,sogou'),
}

SEARCH_ENGINES = {
    'bing': ('https://www.bing.com/search?q=', '''(() => {
        const out = [];
        document.querySelectorAll('#b_results li.b_algo').forEach(li => {
            const a = li.querySelector('h2 a');
            const p = li.querySelector('.b_caption p, .b_lineclamp2');
            if (a) out.push({title: (a.innerText||'').trim().slice(0,80), url: a.href,
                             snippet: (p ? p.innerText : '').slice(0,160)});
        });
        return JSON.stringify(out.slice(0, 10));
    })()'''),
    'baidu': ('https://www.baidu.com/s?wd=', '''(() => {
        const out = [];
        document.querySelectorAll('h3 a').forEach(a => {
            out.push({title: (a.innerText||'').trim().slice(0,80),
                      url: a.getAttribute('href')||'', snippet: ''});
        });
        return JSON.stringify(out.slice(0, 12));
    })()'''),
    'sogou': ('https://www.sogou.com/web?query=', '''(() => {
        const out = [];
        document.querySelectorAll('.vrwrap h3 a, .results h3 a').forEach(a => {
            out.push({title: (a.innerText||'').trim().slice(0,80),
                      url: a.href || '', snippet: ''});
        });
        return JSON.stringify(out.slice(0, 12));
    })()'''),
}


def _search_engine_list(raw=None):
    s = raw if raw is not None else (CFG.get('search_engines') or '')
    names = [x.strip().lower() for x in s.split(',') if x.strip()]
    out = [n for n in names if n in SEARCH_ENGINES]
    return out or ['bing', 'baidu']

GITHUB_INDEX_URL = ('https://raw.githubusercontent.com/jbiaojerry/ebook-treasure-chest/'
                    'main/docs/all-books.json')

NETDISK_RES = [
    r'https?://pan\.quark\.cn/s/[0-9a-zA-Z]+',
    r'https?://(?:pan|yun|eyun)\.baidu\.com/(?:s|share|disk)/[0-9a-zA-Z_\-]+(?:#[0-9a-zA-Z_\-/]*)?',
    r'https?://(?:www\.)?(?:aliyundrive|alipan)\.com/s/[0-9a-zA-Z]+',
    r'https?://cloud\.189\.cn/[0-9a-zA-Z_\-/]+',
    r'https?://(?:www\.)?115\.com/s/[0-9a-zA-Z]+',
    r'https?://(?:www\.)?(?:123pan\.com|123pan\.cn|123684\.com|123865\.com|123912\.com)/s/[0-9a-zA-Z_\-]+',
    r'https?://pan\.xunlei\.com/s/[0-9a-zA-Z_\-]+',
    r'https?://share\.weiyun\.com/[0-9a-zA-Z_\-]+',
    r'https?://caiyun\.139\.com/[0-9a-zA-Z_\-/?=&]+',
    r'https?://drive\.uc\.cn/s/[0-9a-zA-Z_\-]+',
    r'https?://(?:www\.)?lanzou[a-z]?\.com/[0-9a-zA-Z_\-]+',
    r'https?://drive\.google\.com/file/d/[0-9a-zA-Z_\-]+',
    r'https?://1drv\.ms/[a-zA-Z0-9]+',
    r'https?://mega\.nz/(?:file|folder)/[a-zA-Z0-9_\-]+',
    r'https?://(?:www\.)?dropbox\.com/s/[0-9a-zA-Z]+',
    r'https?://(?:www\.)?(?:terabox|1024terabox)\.com/s/[a-zA-Z0-9_\-]+',
]
CTFILE_RE = r'https?://(?:url\d*\.|www\.)?ctfile\.com/f/[0-9a-zA-Z\-]+(?:\?p=\d+)?'
DIRECT_FILE_RE = r'https?://[^\s"\'<>\\]{6,200}?\.(?:epub|mobi|azw3|fb2|txt|pdf)'

_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def proxies():
    p = CFG['proxy']
    return {'http': p, 'https': p} if p else None


_BROWSER_EXE_HINTS = {
    'chrome': ['google-chrome', 'chrome', r'C:\Program Files\Google\Chrome\Application\chrome.exe',
               r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'],
    'edge': ['msedge', r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
             r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'],
    'brave': ['brave', r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'],
    'vivaldi': ['vivaldi', r'C:\Program Files\Vivaldi\Application\vivaldi.exe'],
    'opera': ['opera', r'C:\Program Files\Opera\launcher.exe'],
}


def _resolve_browser_exe(kind):
    for c in _BROWSER_EXE_HINTS.get(kind, []):
        if os.path.sep in c:
            if os.path.exists(c):
                return c
        else:
            w = shutil.which(c)
            if w:
                return w
    return ''


def _system_default_browser_exe():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r'Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice') as k:
            progid, _ = winreg.QueryValueEx(k, 'ProgId')
    except Exception:
        return ''
    pid = (progid or '').lower()
    for kind in ('chrome', 'edge', 'brave', 'vivaldi', 'opera'):
        if kind in pid:
            return _resolve_browser_exe(kind)
    return ''


def find_chrome():
    if CFG['chrome'] and os.path.exists(CFG['chrome']):
        return CFG['chrome']
    sysdef = _system_default_browser_exe()
    if sysdef:
        return sysdef
    for kind in ('chrome', 'edge'):
        exe = _resolve_browser_exe(kind)
        if exe:
            return exe
    return ''


# ---------------------------------------------------------------------------
# 文本匹配 / 评分（单候选模型，两个来源共用）
# ---------------------------------------------------------------------------

def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r'[^a-z0-9\u4e00-\u9fff ]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def tokens(s):
    return [t for t in norm(s).split() if t not in STOPWORDS and len(t) > 1]


def has_cjk(s):
    return bool(re.search(r'[\u4e00-\u9fff]', s or ''))


def title_ok(cand_title, name):
    ct = norm(cand_title)
    if has_cjk(name):
        base = norm(name).replace(' ', '')
        ct_ns = ct.replace(' ', '')
        if base and base in ct_ns:
            return True
        common = sum(1 for ch in set(base) if ch in ct_ns)
        return bool(base) and common / max(1, len(set(base))) >= 0.75
    nt = tokens(name)
    st = set(nt)
    if not st:
        return False
    ct_tokens = tokens(cand_title)
    overlap = len(st & set(ct_tokens)) / len(st)
    if overlap < 0.55:
        return False
    if len(nt) >= 2:
        cand_adjacent_pairs = set(zip(ct_tokens, ct_tokens[1:]))
        if not any(p in cand_adjacent_pairs for p in zip(nt, nt[1:])):
            return False
    return True


def author_ok(cand_author, spec):
    a = norm(spec.get('author') or '')
    if not a:
        return True
    ca = norm(cand_author or '')
    if has_cjk(a):
        aa, caa = a.replace(' ', ''), ca.replace(' ', '')
        if aa in caa or caa in aa:
            return True
        return sum(1 for ch in set(aa) if ch in caa) / max(1, len(set(aa))) >= 0.6
    at = tokens(a)
    if not at:
        return True
    cat = set(tokens(cand_author or ''))
    return sum(1 for t in at if t in cat) >= max(1, len(at) // 2)


def size_to_bytes(txt):
    m = re.search(r'([\d.]+)\s*(KB|MB|GB)', txt or '', re.I)
    if not m:
        return 0
    return int(float(m.group(1)) * {'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3}[m.group(2).upper()])


def score_candidate(cand, spec):
    """cand: {source,title,author,lang,ext,size_bytes,...}; spec: {name,author,lang,format,must_any,must_not}"""
    title = cand.get('title') or ''
    ext = (cand.get('ext') or '').lower()
    size = cand.get('size_bytes') or 0
    fmt = spec.get('format', 'any')

    if ext not in ALL_EXTS:
        return -1
    if fmt == 'text' and ext not in TEXT_EXTS:
        return -1
    if fmt == 'pdf' and ext not in PDF_EXTS:
        return -1
    if size and (size < MIN_SIZE or size > MAX_SIZE):
        return -1
    tl = title.lower()
    if any(b in tl for b in BAD_WORDS):
        return -1
    if spec.get('must_not') and any(m.lower() in tl for m in spec['must_not']):
        return -1
    if spec.get('must_any') and not any(m.lower() in tl for m in spec['must_any']):
        return -1
    if not spec.get('loose'):
        if not title_ok(title, spec['name']):
            return -1
        strong = norm(spec['name']).replace(' ', '') in norm(title).replace(' ', '')
        if not strong and not author_ok(cand.get('author', ''), spec):
            return -1

    sc = EXT_SCORE.get(ext, 0.5)
    pref = spec.get('lang')
    lang = (cand.get('lang') or '').lower()
    if pref and not spec.get('ignore_lang'):
        if pref == 'zh':
            sc += 1.5 if ('chinese' in lang or lang.startswith('zh')) else -0.5
        elif pref == 'en':
            sc += 1.5 if ('english' in lang or lang == 'en') else -0.5
    if size > 2 * 1024 * 1024:
        sc += 0.6
    elif size > 500 * 1024:
        sc += 0.3
    if norm(spec['name']).replace(' ', '') in norm(title).replace(' ', ''):
        sc += 0.5
    if cand.get('source') == 'libgen':
        sc += 0.2  # 免配额来源轻微优先
    return sc


# ---------------------------------------------------------------------------
# LibGen（libgen.li）
# ---------------------------------------------------------------------------

LIBGEN = 'https://libgen.li'


def _session():
    import requests
    s = requests.Session()
    if proxies():
        s.proxies = proxies()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'})
    s.verify = False
    return s


_LG_TR = re.compile(r'<tr[^>]*>(.*?)</tr>', re.S)
_LG_TD = re.compile(r'<td[^>]*>(.*?)</td>', re.S)
_LG_TBODY = re.compile(r'<tbody>(.*?)</tbody>', re.S)


def _strip_tags(s):
    return re.sub(r'<[^>]+>', ' ', s or '').strip()


def search_libgen(query, session=None):
    s = session or _session()
    r = s.get(LIBGEN + '/index.php', params={'req': query, 'res': 25}, timeout=45)
    if r.status_code != 200:
        return []
    tb = _LG_TBODY.search(r.text)
    body = tb.group(1) if tb else r.text
    out = []
    for tr in _LG_TR.findall(body):
        if 'md5=' not in tr:
            continue
        tds = _LG_TD.findall(tr)
        if len(tds) < 8:
            continue
        tm = re.search(r'href="edition\.php\?id=\d+"[^>]*>\s*(.*?)\s*</a>', tds[0], re.S)
        md5m = re.search(r'md5=([a-f0-9]{32})', tr)
        if not tm or not md5m:
            continue
        out.append({
            'source': 'libgen',
            'title': _strip_tags(tm.group(1)),
            'author': _strip_tags(tds[1]),
            'lang': _strip_tags(tds[4]).lower(),
            'size_str': _strip_tags(tds[6]),
            'size_bytes': size_to_bytes(_strip_tags(tds[6])),
            'ext': _strip_tags(tds[7]).lower(),
            'year': _strip_tags(tds[3]),
            'id': md5m.group(1),
        })
    return out


def download_libgen(cand, out_path, session=None, attempts=4):
    s = session or _session()
    md5 = cand['id']
    tmp = out_path + '.part'
    err = 'unknown'
    for attempt in range(attempts):
        try:
            r = s.get(LIBGEN + '/ads.php', params={'md5': md5}, timeout=45,
                      headers={'Referer': LIBGEN + '/'})
            m = re.search(r'href="(get\.php\?[^"]+)"', r.text)
            if not m:
                err = 'no get link'
                time.sleep(3 + attempt * 4)
                continue
            get_url = LIBGEN + '/' + m.group(1).replace('&amp;', '&')
            offset = os.path.getsize(tmp) if os.path.exists(tmp) else 0
            hdrs = {'Referer': r.url}
            if offset > 0:
                hdrs['Range'] = f'bytes={offset}-'
            r2 = s.get(get_url, timeout=(30, 300), stream=True, headers=hdrs)
            if r2.status_code not in (200, 206):
                err = f'get status {r2.status_code}'
                time.sleep(3 + attempt * 4)
                continue
            append = (r2.status_code == 206 and offset > 0)
            with open(tmp, 'ab' if append else 'wb') as f:
                for c in r2.iter_content(1 << 16):
                    f.write(c)
            if os.path.getsize(tmp) < MIN_SIZE:
                err = 'too small'
                os.remove(tmp)
                time.sleep(3 + attempt * 4)
                continue
            os.replace(tmp, out_path)
            return True, os.path.getsize(out_path)
        except Exception as e:
            err = str(e)[:90]
            time.sleep(4 + attempt * 6)
    return False, f'failed {attempts}x: {err}'


# ---------------------------------------------------------------------------
# Z-Library（Chrome CDP：搜索 → /dl/ 触发 → 截获 CDN 直链 → Python 拉取）
# ---------------------------------------------------------------------------

def _cdp_get_json(path, host=None):
    """Fetch a DevTools JSON endpoint. host like '[::1]' or '127.0.0.1'."""
    last = None
    for h in ([host] if host else ['[::1]', '127.0.0.1']):
        try:
            with _opener.open(f'http://{h}:{CFG["cdp_port"]}{path}', timeout=10) as r:
                return json.loads(r.read().decode('utf-8-sig'))
        except Exception as e:
            last = e
    raise RuntimeError(f'CDP unreachable: {last}')


def cdp_alive():
    """Strict liveness: /json/version must answer with a real Chrome payload.

    Note: some other process may squat 127.0.0.1:<port> and accept sockets
    while returning 404 — a plain TCP check gives false positives.
    """
    for host in ('[::1]', '127.0.0.1'):
        try:
            d = _cdp_get_json('/json/version', host=host)
            if d.get('Browser'):
                return True
        except Exception:
            pass
    return False


JS_CARDS = '''(() => {
    return JSON.stringify([...document.querySelectorAll('z-bookcard')].map(e => ({
        title: (e.querySelector('[slot=title]')||{}).innerText || '',
        author: (e.querySelector('[slot=author]')||{}).innerText || '',
        href: e.getAttribute('href'), download: e.getAttribute('download'),
        ext: e.getAttribute('extension'), size: e.getAttribute('filesize'),
        lang: e.getAttribute('language'), year: e.getAttribute('year')
    })));
})()'''

ZLIB_HOME = 'https://1lib.sk'


class ZlibTab:
    """A CDP tab driven over raw websocket (no Playwright)."""

    def __init__(self):
        import websocket
        ver = _cdp_get_json('/json/version')
        bws = websocket.create_connection(ver['webSocketDebuggerUrl'], timeout=30, suppress_origin=True)
        bws.send(json.dumps({'id': 1, 'method': 'Target.createTarget', 'params': {'url': ZLIB_HOME + '/'}}))
        tid = None
        while True:
            d = json.loads(bws.recv())
            if d.get('id') == 1:
                tid = d['result']['targetId']
                break
        bws.close()
        time.sleep(1)
        targets = _cdp_get_json('/json/list')
        t = next(x for x in targets if x['id'] == tid)
        self.ws = websocket.create_connection(t['webSocketDebuggerUrl'], timeout=30, suppress_origin=True)
        self.ws.settimeout(3)
        self.mid = 0
        self.cdn_url = None
        self._send('Page.enable')
        self._send('Browser.setDownloadBehavior', {'behavior': 'allow',
                                                   'downloadPath': tempfile.gettempdir(),
                                                   'eventsEnabled': True})

    def _send(self, method, params=None, wait=True):
        self.mid += 1
        mid = self.mid
        self.ws.send(json.dumps({'id': mid, 'method': method, 'params': params or {}}))
        if not wait:
            return None
        while True:
            d = json.loads(self.ws.recv())
            if d.get('id') == mid:
                return d
            self._handle(d)

    def _handle(self, d):
        if d.get('method') == 'Browser.downloadWillBegin':
            self.cdn_url = d['params']['url']

    def drain(self):
        while True:
            try:
                self._handle(json.loads(self.ws.recv()))
            except Exception:
                return

    def navigate(self, url):
        self.cdn_url = None
        try:
            self._send('Page.navigate', {'url': url})
        except Exception:
            pass
        t0 = time.time()
        while time.time() - t0 < 6:
            self.drain()
            time.sleep(0.4)

    def wait_cdn(self, timeout=25):
        t0 = time.time()
        while time.time() - t0 < timeout:
            self.drain()
            if self.cdn_url:
                return self.cdn_url
            time.sleep(0.5)
        return None

    def wait_ready(self, timeout=25):
        t0 = time.time()
        while time.time() - t0 < timeout:
            r = self._send('Runtime.evaluate', {
                'expression': "document.readyState + '|' + (document.title||'') + '|' + "
                              "(document.querySelectorAll('z-bookcard').length)",
                'returnByValue': True})
            try:
                state, title, n = r['result']['result']['value'].split('|', 2)
                if 'DiamWall' in title or '验证' in title:
                    time.sleep(2)
                    continue
                if state in ('interactive', 'complete'):
                    return title, int(n)
            except Exception:
                pass
            time.sleep(1.2)
        return None, 0

    def eval(self, expr, await_promise=False):
        r = self._send('Runtime.evaluate', {'expression': expr, 'returnByValue': True,
                                            'awaitPromise': await_promise})
        return r.get('result', {}).get('result', {}).get('value')

    def close(self):
        try:
            self.ws.close()
        except Exception:
            pass


def zlib_profile(tab=None):
    """Return user profile JSON via in-browser EAPI fetch."""
    own = tab is None
    if own:
        tab = ZlibTab()
    try:
        tab.navigate(ZLIB_HOME + '/')
        tab.wait_ready()
        val = tab.eval('''(async () => {
            try {
                const r = await fetch('/eapi/user/profile');
                const j = await r.json();
                return JSON.stringify(j);
            } catch (e) { return JSON.stringify({success: 0, error: String(e)}); }
        })()''', await_promise=True)
        return json.loads(val) if val else {}
    finally:
        if own:
            tab.close()


def search_zlib(query, tab=None):
    own = tab is None
    if own:
        tab = ZlibTab()
    try:
        tab.navigate(ZLIB_HOME + '/s/?q=' + urllib.parse.quote(query))
        title, n = tab.wait_ready()
        if n == 0:
            return []
        cards = json.loads(tab.eval(JS_CARDS) or '[]')
        out = []
        for c in cards:
            if not c.get('download'):
                continue
            out.append({
                'source': 'zlib',
                'title': c.get('title') or '',
                'author': c.get('author') or '',
                'lang': (c.get('lang') or '').lower(),
                'size_str': c.get('size') or '',
                'size_bytes': size_to_bytes(c.get('size')),
                'ext': (c.get('ext') or '').lower(),
                'year': c.get('year') or '',
                'id': c.get('download'),   # /dl/xxx
            })
        return out
    finally:
        if own:
            tab.close()


def download_zlib(cand, out_path, tab=None):
    import requests
    own = tab is None
    if own:
        tab = ZlibTab()
    try:
        tab.navigate(ZLIB_HOME + cand['id'])
        cdn = tab.wait_cdn(timeout=25)
        if not cdn:
            return False, 'no downloadWillBegin (配额用尽或条目失效)'
        s = _session()
        r = s.get(cdn, timeout=600, stream=True)
        if r.status_code != 200:
            return False, f'cdn status {r.status_code}'
        tmp = out_path + '.part'
        size = 0
        with open(tmp, 'wb') as f:
            for c in r.iter_content(1 << 16):
                f.write(c)
                size += len(c)
        if size < MIN_SIZE:
            os.remove(tmp)
            return False, f'too small {size}'
        os.replace(tmp, out_path)
        return True, size
    finally:
        if own:
            tab.close()


def zlib_quota():
    prof = zlib_profile()
    u = (prof or {}).get('user') or {}
    if not u:
        return {'logged_in': False, 'raw': str(prof)[:200]}
    return {'logged_in': True, 'used': u.get('downloads_today'), 'limit': u.get('downloads_limit'),
            'premium': bool(u.get('isPremium'))}


# ---------------------------------------------------------------------------
# Anna's Archive（beta）
# ---------------------------------------------------------------------------

AA = 'https://annas-archive.gl'


def search_aa(query, tab=None, limit=15):
    own = tab is None
    if own:
        tab = ZlibTab()
    try:
        tab.navigate(AA + '/search?q=' + urllib.parse.quote(query))
        # 等页面就绪（DDoS-Guard 通常几秒内放行）
        t0 = time.time()
        while time.time() - t0 < 25:
            title = (tab.eval('document.title') or '')
            if title and 'DDoS' not in title:
                break
            time.sleep(2)
        time.sleep(3)
        rows = tab.eval('''(() => {
            const anchors = [...document.querySelectorAll('a[href*="/md5/"]')];
            const out = [];
            const seen = new Set();
            for (const a of anchors) {
                const r = a.getBoundingClientRect();
                if (r.height === 0) continue;
                const href = a.getAttribute('href');
                if (seen.has(href)) continue;
                let el = a;
                let best = null;
                for (let i = 0; i < 8 && el; i++) {
                    el = el.parentElement;
                    if (!el) break;
                    const tx = el.innerText || '';
                    if (tx.length > 30 && tx.length < 420 && /(EPUB|PDF|MOBI|AZW3|FB2|TXT|DJVU)/.test(tx)) { best = el; break; }
                }
                const txt = (best ? best.innerText : a.innerText).replace(/\\s+/g, ' ').slice(0, 260);
                if (!/(EPUB|PDF|MOBI|AZW3|FB2|TXT|DJVU)/.test(txt)) continue;
                seen.add(href);
                const fm = txt.match(/·\\s*(EPUB|PDF|MOBI|AZW3|FB2|TXT|DJVU)/i);
                const sm = txt.match(/([\\d.]+\\s*(?:KB|MB|GB))/i);
                out.push({href: href, title: txt.slice(0, 90), ext: (fm ? fm[1] : '').toLowerCase(),
                          size_str: sm ? sm[1] : '', amd5: (href.match(/[a-f0-9]{32}/) || [''])[0]});
                if (out.length >= 20) break;
            }
            return JSON.stringify(out);
        })()''')
        out = []
        for r in (json.loads(rows) if rows else []):
            if not r.get('amd5'):
                continue
            out.append({'source': 'aa', 'title': r['title'], 'author': '', 'lang': '',
                        'size_str': r['size_str'], 'size_bytes': size_to_bytes(r['size_str']),
                        'ext': r['ext'], 'year': '', 'id': r['amd5']})
        return out[:limit]
    finally:
        if own:
            tab.close()


def download_aa(cand, out_path, tab=None):
    import requests
    own = tab is None
    if own:
        tab = ZlibTab()
    try:
        md5 = cand['id']
        ok = False
        for n in (9, 7, 5, 3, 0):
            tab.navigate(f'{AA}/slow_download/{md5}/0/{n}')
            t0 = time.time()
            while time.time() - t0 < 40:
                title = (tab.eval('document.title') or '')
                if title and 'DDoS' not in title and 'partner' in title.lower() is not None:
                    pass
                body = tab.eval('document.body ? document.body.innerText : ""') or ''
                m = re.search(r'(https?://(?:\d{1,3}\.){3}\d{1,3}:\d+/[^\s"]+)', body)
                if m:
                    ok = m.group(1)
                    break
                time.sleep(4)
            if ok:
                break
        if not ok:
            return False, 'AA 未给出直链（可能被反爬或需更久等待）'
        s = _session()
        r = s.get(ok, timeout=900, stream=True)
        if r.status_code != 200:
            return False, f'aa cdn status {r.status_code}'
        tmp = out_path + '.part'
        size = 0
        with open(tmp, 'wb') as f:
            for c in r.iter_content(1 << 16):
                f.write(c)
                size += len(c)
        if size < MIN_SIZE:
            os.remove(tmp)
            return False, f'too small {size}'
        os.replace(tmp, out_path)
        return True, size
    finally:
        if own:
            tab.close()


# ---------------------------------------------------------------------------
# GitHub 书库索引（城通网盘链接）
# ---------------------------------------------------------------------------

def load_github_index(max_age_days=7):
    os.makedirs(CFG['cache_dir'], exist_ok=True)
    p = os.path.join(CFG['cache_dir'], 'ebook-chest.json')
    if os.path.exists(p) and (time.time() - os.path.getmtime(p)) < max_age_days * 86400:
        try:
            with open(p, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    s = _session()
    r = s.get(GITHUB_INDEX_URL, timeout=180)
    r.raise_for_status()
    data = r.json()
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    return data


def search_github(query, index=None, limit=15):
    idx = index if index is not None else load_github_index()
    q = norm(query)
    q_ns = q.replace(' ', '')
    out = []
    seen_links = set()
    for b in idx:
        title = b.get('title') or ''
        if not title:
            continue
        tn = norm(title)
        tn_ns = tn.replace(' ', '')
        if has_cjk(query):
            hit = bool(q_ns) and (q_ns in tn_ns or tn_ns in q_ns)
            if not hit:
                common = sum(1 for ch in set(q_ns) if ch in tn_ns)
                hit = bool(q_ns) and common / max(1, len(set(q_ns))) >= 0.8
        else:
            st = set(tokens(query))
            hit = bool(st) and len(st & set(tokens(title))) / len(st) >= 0.8
        if not hit:
            continue
        fmts = [f.lower() for f in (b.get('formats') or [])]
        ext = next((e for e in ('epub', 'mobi', 'azw3', 'fb2', 'txt') if e in fmts), '')
        if not ext or not b.get('link'):
            continue
        out.append({'source': 'github', 'title': title, 'author': b.get('author') or '',
                    'lang': 'chinese' if (b.get('language') or '').upper() == 'ZH' else (b.get('language') or '').lower(),
                    'size_str': '', 'size_bytes': 0, 'ext': ext, 'year': '',
                    'id': b.get('link'), 'formats': fmts})
        if len(out) >= limit:
            break
    return out


def _wait_new_file(dirs, timeout=1800):
    seen = {}
    for d in dirs:
        try:
            seen[d] = set(os.listdir(d))
        except OSError:
            seen[d] = set()
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(3)
        for d in dirs:
            try:
                files = os.listdir(d)
            except OSError:
                continue
            new = [f for f in files if f not in seen[d] and not f.endswith('.crdownload')]
            if new:
                newest = max(new, key=lambda f: os.path.getmtime(os.path.join(d, f)))
                return os.path.join(d, newest)
    return None


def download_ctfile(cand, out_path, timeout=1800):
    import shutil as _sh
    import zipfile
    link = cand['id']
    staging = tempfile.mkdtemp(prefix='ni_book_ctfile_')
    dl_default = os.path.join(os.path.expanduser('~'), 'Downloads')
    tab = ZlibTab()
    try:
        tab._send('Browser.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': staging,
                                                  'eventsEnabled': True})
        tab.navigate(link)
        t0 = time.time()
        clicked = False
        while time.time() - t0 < 40:
            body = tab.eval('document.body ? document.body.innerText : ""') or ''
            if '立即下载' in body or '普通下载' in body:
                clicked = bool(tab.eval('''(() => {
                    const cands = [];
                    document.querySelectorAll('a, button, div').forEach(b => {
                        const t = (b.innerText||'').replace(/\\s+/g,' ').trim();
                        if (t === '立即下载') cands.push(b);
                    });
                    if (!cands.length) return false;
                    cands[0].click();
                    return true;
                })()'''))
                if clicked:
                    break
            time.sleep(3)
        if not clicked:
            return False, 'ctfile: 未找到下载按钮或页面未就绪'
        found = _wait_new_file([staging, dl_default], timeout=timeout)
        if not found:
            return False, 'ctfile: 等待下载超时'
        if found.lower().endswith('.zip'):
            extract_dir = found + '_x'
            os.makedirs(extract_dir, exist_ok=True)
            with zipfile.ZipFile(found) as z:
                z.extractall(extract_dir)
            picked = []
            for root, _, files in os.walk(extract_dir):
                for fn in files:
                    ext = os.path.splitext(fn)[1].lower().lstrip('.')
                    fp = os.path.join(root, fn)
                    if (ext in TEXT_EXTS or ext in PDF_EXTS) and os.path.getsize(fp) >= MIN_SIZE:
                        picked.append(fp)
            if not picked:
                return False, 'ctfile: 压缩包内未找到电子书文件'
            pref = {'epub': 0, 'mobi': 1, 'azw3': 2, 'fb2': 3, 'txt': 4, 'pdf': 5}
            picked.sort(key=lambda x: (pref.get(os.path.splitext(x)[1].lstrip('.').lower(), 9),
                                       -os.path.getsize(x)))
            base = os.path.splitext(out_path)[0]
            moved, used = [], set()
            for fp in picked:
                ext = os.path.splitext(fp)[1].lstrip('.').lower()
                if ext in used:
                    continue
                used.add(ext)
                dst = f'{base}.{ext}'
                _sh.move(fp, dst)
                moved.append(dst)
            return True, moved[0]
        ext = os.path.splitext(found)[1].lstrip('.').lower() or (cand.get('ext') or 'bin')
        dst = os.path.splitext(out_path)[0] + '.' + ext
        _sh.move(found, dst)
        return True, dst
    finally:
        tab.close()


# ---------------------------------------------------------------------------
# 全网搜索兜底（网盘链接 + 直接文件链接）
# ---------------------------------------------------------------------------

def _resolve_bing_url(u):
    if 'bing.com/ck/' not in (u or ''):
        return u
    import base64 as _b64
    m = re.search(r'[?&]u=([^&]+)', u)
    if not m:
        return u
    raw = urllib.parse.unquote(m.group(1))
    if raw.startswith('a1'):
        raw = raw[2:]
    raw = raw.replace('-', '+').replace('_', '/')
    raw += '=' * (-len(raw) % 4)
    try:
        return _b64.b64decode(raw).decode('utf-8', 'ignore') or u
    except Exception:
        return u


def _extract_links(html_text):
    import html as _html
    text = _html.unescape(html_text or '')
    out = []

    def add(kind, url, pos):
        ctx = re.sub(r'\s+', ' ', text[max(0, pos - 150):pos + 80]).strip()
        out.append({'kind': kind, 'url': url.rstrip('.,;"\''), 'ctx': ctx[:180]})

    for pat in NETDISK_RES:
        for m in re.finditer(pat, text, re.I):
            add('netdisk', m.group(0), m.start())
    for m in re.finditer(CTFILE_RE, text, re.I):
        add('ctfile', m.group(0), m.start())
    for m in re.finditer(DIRECT_FILE_RE, text, re.I):
        add('direct', m.group(0), m.start())
    return out


def _ctx_match(name, ctx):
    nn = norm(name).replace(' ', '')
    cn = norm(ctx).replace(' ', '')
    if not nn or not cn:
        return False
    if nn in cn:
        return True
    n = len(nn)
    for L in range(min(n, 8), 3, -1):
        for i in range(0, n - L + 1):
            if nn[i:i + L] in cn:
                return True
    if has_cjk(name):
        return False
    st = set(tokens(name))
    return bool(st) and len(st & set(tokens(ctx))) / len(st) >= 0.85


def _resolve_baidu_url(u):
    if 'baidu.com/link?' not in (u or ''):
        return u
    try:
        s = _session()
        r = s.get(u, timeout=12, allow_redirects=True, stream=True)
        final = r.url
        r.close()
        if final and 'baidu.com' not in final:
            return final
    except Exception:
        pass
    return u


def web_search_links(query, tab=None, max_pages=5, max_engines=2):
    own = tab is None
    if own:
        tab = ZlibTab()
    try:
        def try_engine(name):
            prefix, parser = SEARCH_ENGINES[name]
            tab.navigate(prefix + urllib.parse.quote(query))
            t0 = time.time()
            while time.time() - t0 < 20:
                raw = tab.eval(parser)
                if raw and raw != '[]':
                    try:
                        rows = json.loads(raw)
                    except Exception:
                        rows = []
                    if rows:
                        html = tab.eval('document.documentElement ? document.documentElement.outerHTML : ""') or ''
                        return rows, html
                time.sleep(2)
            return [], ''

        results, serp_html, engines_used = [], '', []

        def collect():
            nonlocal serp_html
            for name in _search_engine_list():
                if len(engines_used) >= max_engines:
                    break
                rows, html = try_engine(name)
                if rows:
                    engines_used.append(name)
                    results.extend(rows)
                    serp_html += '\n' + html

        collect()
        if not results:
            time.sleep(15)
            engines_used.clear()
            collect()
        found = _extract_links(serp_html)
        s = _session()
        dedup_results, seen_urls = [], set()
        for r in results:
            u = _resolve_bing_url(r.get('url') or '')
            u = _resolve_baidu_url(u)
            r['url'] = u
            if u in seen_urls:
                continue
            seen_urls.add(u)
            dedup_results.append(r)
        results = dedup_results
        for r in results[:max_pages]:
            u = r.get('url') or ''
            if not u.startswith('http') or 'baidu.com/link' in u:
                continue
            if any(d in u for d in ('bing.com', 'baidu.com', 'microsoft.com', 'sogou.com')):
                continue
            for attempt in (0, 1):
                try:
                    rr = s.get(u, timeout=20)
                    if rr.status_code == 200 and len(rr.content) < 3 * 1024 * 1024:
                        found += _extract_links(rr.text)
                    break
                except Exception:
                    time.sleep(2)
        dedup, seen = [], set()
        for item in found:
            if item['url'] in seen:
                continue
            seen.add(item['url'])
            dedup.append(item)
        return {'query': query, 'engines': engines_used, 'results': results[:12], 'links': dedup[:30]}
    finally:
        if own:
            tab.close()


def download_direct(url, out_path):
    s = _session()
    r = s.get(url, timeout=600, stream=True)
    if r.status_code != 200:
        return False, f'http {r.status_code}'
    tmp = out_path + '.part'
    size = 0
    with open(tmp, 'wb') as f:
        for c in r.iter_content(1 << 16):
            f.write(c)
            size += len(c)
    if size < MIN_SIZE:
        os.remove(tmp)
        return False, f'too small {size}'
    os.replace(tmp, out_path)
    return True, size


def web_fallback(name, outdir, spec):
    if not cdp_alive():
        return {'status': 'needs_manual', 'query': name,
                'error': '全网搜索兜底需要 Chrome CDP：先执行 setup --launch-chrome'}
    links, results, engines_used, last_err = [], [], [], ''
    for q in (f'{name} epub 下载', f'{name} 网盘 电子书'):
        try:
            res = web_search_links(q)
        except Exception as e:
            last_err = str(e)[:150]
            continue
        engines_used += res.get('engines', [])
        results += res.get('results', [])
        links += res.get('links', [])
        matched_now = [l for l in links if l.get('ctx') and _ctx_match(name, l['ctx'])]
        if any(l['kind'] in ('ctfile', 'direct') for l in matched_now):
            break
    if not links and last_err and not results:
        return {'status': 'needs_manual', 'query': name, 'error': last_err}
    dedup, seen = [], set()
    for l in links:
        if l['url'] in seen:
            continue
        seen.add(l['url'])
        dedup.append(l)
    links = dedup
    matched = [l for l in links if l.get('ctx') and _ctx_match(name, l['ctx'])]
    ordered = matched + [l for l in links if l not in matched]
    import urllib.parse as _up
    for l in [x for x in matched if x['kind'] == 'ctfile'][:3]:
        out_guess = os.path.join(outdir, f'{safe_name(name)}.epub')
        ok, info = download_ctfile({'id': l['url'], 'ext': 'epub'}, out_guess)
        if ok:
            return {'status': 'downloaded', 'source': 'web-ctfile', 'url': l['url'],
                    'path': info, 'title': name}
    for l in [x for x in matched if x['kind'] == 'direct'][:2]:
        path_part = _up.urlparse(l['url']).path
        ext = os.path.splitext(path_part)[1].lstrip('.').lower() or 'bin'
        if spec.get('format') == 'text' and ext not in TEXT_EXTS:
            continue
        if spec.get('format') == 'pdf' and ext not in PDF_EXTS:
            continue
        out_path = os.path.join(outdir, f'{safe_name(name)}.{ext}')
        ok, info = download_direct(l['url'], out_path)
        if ok:
            vok, _ = verify_file(out_path, ext)
            if vok:
                return {'status': 'downloaded', 'source': 'web-direct', 'url': l['url'],
                        'path': out_path, 'bytes': info, 'title': name}
    out = {'status': 'needs_manual', 'query': name, 'engines': engines_used,
           'results': results[:10], 'links': ordered[:20], 'matched': len(matched)}
    if not out['results'] and not links:
        out['error'] = '搜索引擎无结果或被限流（连续高频查询会触发），稍后重试'
    return out


# ---------------------------------------------------------------------------
# 校验 + 命名
# ---------------------------------------------------------------------------

MAGIC = {
    'pdf': [b'%PDF'],
    'epub': [b'PK\x03\x04'],
    'fb2': [b'<?xml', b'\xef\xbb\xbf<?xml'],
    'txt': None,
    'rtf': [b'{\\rtf'],
}


def verify_file(path, ext):
    if not os.path.exists(path) or os.path.getsize(path) < MIN_SIZE:
        return False, 'missing/too small'
    with open(path, 'rb') as f:
        head = f.read(4096)
    ext = (ext or '').lower()
    sigs = MAGIC.get(ext)
    if ext in ('mobi', 'azw3'):
        if head[:4] in (b'BOOK', b'TPZ\x00', b'PK\x03'):
            return True, ''
        if b'BOOKMOBI' in head[:200]:
            return True, ''
        return False, 'bad mobi/azw3 magic'
    if ext == 'fb2':
        if b'FictionBook' in head or head[:5] in (b'<?xml',):
            return True, ''
        return False, 'bad fb2 magic'
    if sigs:
        if any(head.startswith(s) for s in sigs):
            return True, ''
        return False, f'bad {ext} magic'
    return True, ''


def safe_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip().rstrip('.')


# ---------------------------------------------------------------------------
# 核心流程
# ---------------------------------------------------------------------------

def search_all(query, fmt='any', sources=('github', 'libgen', 'zlib', 'aa'), verbose=True):
    cands = []
    errors = []
    if 'libgen' in sources:
        try:
            cands += search_libgen(query)
        except Exception as e:
            errors.append(f'libgen: {str(e)[:80]}')
    if 'zlib' in sources:
        if cdp_alive():
            try:
                cands += search_zlib(query)
            except Exception as e:
                errors.append(f'zlib: {str(e)[:80]}')
        else:
            errors.append('zlib: Chrome CDP 未运行（先跑 setup --launch-chrome 并登录）')
    if 'aa' in sources:
        if cdp_alive():
            try:
                cands += search_aa(query)
            except Exception as e:
                errors.append(f'aa: {str(e)[:80]}')
        else:
            errors.append('aa: 需要 Chrome CDP')
    if 'github' in sources and fmt != 'pdf':
        try:
            cands += search_github(query)
        except Exception as e:
            errors.append(f'github: {str(e)[:80]}')
    if verbose and errors:
        for e in errors:
            print(f'[warn] {e}', file=sys.stderr)
    return cands


def pick_best(cands, spec):
    best = None
    for c in cands:
        try:
            sc = score_candidate(c, spec)
        except Exception:
            continue
        if sc > 0 and (best is None or sc > best[0]):
            best = (sc, c)
    return best


def auto_one(query, name, fmt='any', outdir='.', spec_extra=None, dry=False,
             sources=('libgen', 'zlib', 'aa', 'github'), allow_web=True):
    spec = {'name': name or query, 'format': fmt}
    if spec_extra:
        spec.update(spec_extra)
    groups = [[s] for s in ('github', 'libgen', 'zlib', 'aa') if s in sources]
    tried = []
    for grp in groups:
        if not grp:
            continue
        cands = search_all(query, fmt, tuple(grp))
        best = pick_best(cands, spec)
        if not best:
            tried.append({'sources': grp, 'candidates': len(cands), 'note': 'no acceptable match'})
            continue
        sc, cand = best
        ext = cand['ext']
        out_path = os.path.join(outdir, f'{safe_name(spec["name"])}.{ext}')
        res = {'status': 'picked', 'score': round(sc, 2), 'source': cand['source'],
               'title': cand['title'], 'ext': ext, 'size_str': cand.get('size_str'),
               'path': out_path, 'tried': tried}
        if dry:
            return res
        if os.path.exists(out_path) and os.path.getsize(out_path) > MIN_SIZE:
            res['status'] = 'exists'
            return res
        if cand['source'] == 'libgen':
            ok, info = download_libgen(cand, out_path)
        elif cand['source'] == 'zlib':
            ok, info = download_zlib(cand, out_path)
        elif cand['source'] == 'github':
            ok, info = download_ctfile(cand, out_path)
        else:
            ok, info = download_aa(cand, out_path)
        if ok:
            final = info if isinstance(info, str) and os.path.exists(info) else out_path
            f_ext = os.path.splitext(final)[1].lstrip('.').lower() or ext
            vok, vmsg = verify_file(final, f_ext)
            if not vok:
                res['status'] = 'verify_failed'
                res['err'] = vmsg
                return res
            res.update({'status': 'downloaded', 'path': final, 'bytes': os.path.getsize(final)})
            return res
        tried.append({'sources': grp, 'candidate': cand['title'][:80],
                      'note': f'download failed: {str(info)[:120]}'})
    if allow_web and not dry:
        wres = web_fallback(spec['name'], outdir, spec)
        wres['tried'] = tried
        return wres
    return {'status': 'not_found', 'query': query, 'tried': tried}


# ---------------------------------------------------------------------------
# setup / quota / extract
# ---------------------------------------------------------------------------

def cmd_setup(args):
    import importlib
    report = {'config': CFG, 'checks': {}}
    for mod in ('requests', 'websocket', 'fitz'):
        try:
            m = importlib.import_module(mod)
            report['checks'][mod] = getattr(m, '__version__', 'ok')
        except Exception as e:
            report['checks'][mod] = f'MISSING: {str(e)[:60]}'
    if proxies():
        try:
            host = CFG['proxy'].split('//')[-1]
            h, p = host.split(':')
            s = socket.socket()
            s.settimeout(2)
            s.connect((h, int(p)))
            s.close()
            report['checks']['proxy'] = 'ok'
        except Exception:
            report['checks']['proxy'] = 'unreachable'
    report['checks']['browser'] = find_chrome() or 'not found'
    report['checks']['search_engines'] = _search_engine_list()
    if args.launch_chrome:
        ch = find_chrome()
        if not ch:
            print(json.dumps({'error': 'Chrome/Edge not found'}, ensure_ascii=False))
            return
        os.makedirs(CFG['chrome_profile'], exist_ok=True)
        if not cdp_alive():
            subprocess.Popen([ch, f'--remote-debugging-port={CFG["cdp_port"]}',
                              '--user-data-dir=' + CFG['chrome_profile'],
                              '--no-first-run', '--no-default-browser-check',
                              ZLIB_HOME + '/login'])
            for _ in range(60):
                time.sleep(1)
                if cdp_alive():
                    break
    report['checks']['cdp'] = 'up' if cdp_alive() else 'down'
    if cdp_alive():
        try:
            zq = zlib_quota()
            if not zq.get('logged_in'):
                zq['hint'] = ('请在专用 Chrome 窗口中注册（免费）或登录 Z-Library，登录一次即可；'
                              '无需向本 skill 提供密码')
            report['zlib'] = zq
        except Exception as e:
            report['zlib'] = {'error': str(e)[:120]}
    else:
        report['zlib'] = {'hint': 'CDP Chrome 未运行：先执行 setup --launch-chrome 拉起窗口并登录 Z-Library'}
    print(json.dumps(report, ensure_ascii=False, indent=1))


def cmd_quota(args):
    if not cdp_alive():
        print(json.dumps({'error': 'Chrome CDP 未运行，先 setup --launch-chrome'}, ensure_ascii=False))
        return
    print(json.dumps(zlib_quota(), ensure_ascii=False, indent=1))


def cmd_search(args):
    name = args.name
    spec = {'name': name, 'format': args.format, 'author': args.author, 'lang': args.lang}
    cands = search_all(name, args.format, tuple(args.source.split(',')))
    ranked = []
    for c in cands:
        sc = score_candidate(c, spec)
        if sc > 0:
            ranked.append((sc, c))
    ranked.sort(key=lambda x: -x[0])
    out = []
    for sc, c in ranked[:args.limit]:
        out.append({'score': round(sc, 2), **{k: c.get(k) for k in
                    ('source', 'title', 'author', 'ext', 'size_str', 'year', 'lang', 'id')}})
    report = {'query': name, 'format': args.format, 'count': len(out), 'candidates': out}
    if getattr(args, 'web', False):
        if not cdp_alive():
            report['web'] = {'error': 'web 兜底需要 Chrome CDP（setup --launch-chrome）'}
        else:
            report['web'] = web_search_links(f'{name} epub 下载')
    print(json.dumps(report, ensure_ascii=False, indent=1))


def cmd_get(args):
    cand = {
        'source': args.source,
        'title': args.title or args.name,
        'author': args.author or '',
        'lang': args.lang or '',
        'ext': args.ext,
        'size_str': args.size or '',
        'size_bytes': size_to_bytes(args.size),
        'id': args.md5 or args.dl or args.link,
    }
    if not cand['id']:
        print(json.dumps({'error': '需要 --md5 (libgen/aa) / --dl (zlib) / --link (github / 网盘)'},
                         ensure_ascii=False))
        return
    out_path = os.path.join(args.outdir, f'{safe_name(args.name)}.{args.ext}')
    if os.path.exists(out_path) and os.path.getsize(out_path) > MIN_SIZE:
        print(json.dumps({'status': 'exists', 'path': out_path}, ensure_ascii=False))
        return
    if args.source == 'libgen':
        ok, info = download_libgen(cand, out_path)
        final = out_path
    elif args.source == 'zlib':
        ok, info = download_zlib(cand, out_path)
        final = out_path
    elif args.source == 'aa':
        ok, info = download_aa(cand, out_path)
        final = out_path
    elif args.source == 'github':
        ok, info = download_ctfile(cand, out_path)
        final = info if isinstance(info, str) and os.path.exists(info) else out_path
    else:
        print(json.dumps({'error': f'unknown source {args.source}'}, ensure_ascii=False))
        return
    if ok:
        f_ext = os.path.splitext(final)[1].lstrip('.').lower() or args.ext
        vok, vmsg = verify_file(final, f_ext)
        print(json.dumps({'status': 'downloaded' if vok else 'verify_failed',
                          'path': final, 'bytes': os.path.getsize(final), 'verify': vmsg or 'ok'},
                         ensure_ascii=False))
    else:
        print(json.dumps({'status': 'download_failed', 'err': str(info)[:200]}, ensure_ascii=False))


def cmd_auto(args):
    spec_extra = {}
    if args.author:
        spec_extra['author'] = args.author
    if args.lang:
        spec_extra['lang'] = args.lang
    if args.must_any:
        spec_extra['must_any'] = args.must_any.split('|')
    if args.must_not:
        spec_extra['must_not'] = args.must_not.split('|')
    if args.loose:
        spec_extra['loose'] = True
    res = auto_one(args.name, args.name, fmt=args.format, outdir=args.outdir,
                   spec_extra=spec_extra, dry=args.dry, sources=tuple(args.source.split(',')),
                   allow_web=not getattr(args, 'no_web', False))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    if res.get('status') in ('download_failed', 'not_found'):
        sys.exit(2)


def cmd_batch(args):
    with open(args.manifest, encoding='utf-8') as f:
        man = json.load(f)
    books = man.get('books', man if isinstance(man, list) else [])
    results = []
    for b in books:
        name = b.get('name') or b.get('slug')
        if not name:
            continue
        extra = {k: b[k] for k in ('author', 'lang', 'must_any', 'must_not', 'loose', 'queries') if k in b}
        queries = b.get('queries') or [name]
        res = None
        for q in queries:
            res = auto_one(q, name, fmt=b.get('format', args.format), outdir=args.outdir,
                           spec_extra=extra, dry=args.dry, sources=tuple(args.source.split(',')),
                           allow_web=not getattr(args, 'no_web', False))
            if res.get('status') not in ('not_found',):
                break
        results.append({'name': name, **res})
        print(f"[{res.get('status')}] {name} -> {res.get('title', '')[:60]}", flush=True)
    out = os.path.join(args.outdir, 'ni_book_batch_report.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    done = sum(1 for r in results if r.get('status') in ('downloaded', 'exists'))
    print(f'== {done}/{len(results)} downloaded/exists == report: {out}')


def cmd_extract_pdf(args):
    try:
        import pymupdf
    except ImportError:
        print(json.dumps({'error': 'pymupdf 未安装：pip install pymupdf'}, ensure_ascii=False))
        return
    doc = pymupdf.open(args.pdf)
    pages = len(doc)
    parts = []
    for page in doc:
        t = page.get_text()
        if t.strip():
            parts.append(t)
    doc.close()
    text = '\n'.join(parts)
    avg = len(text) / max(1, pages)
    cls = 'TEXT' if avg > 300 else ('SPARSE' if avg > 50 else 'IMAGE')
    out = args.out or (os.path.splitext(args.pdf)[0] + '.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(text)
    print(json.dumps({'status': 'ok' if cls != 'IMAGE' else 'scanned_no_text',
                      'classification': cls, 'pages': pages, 'chars': len(text),
                      'out': out, 'note': '扫描件无文字层，需 OCR 或换文字版来源' if cls == 'IMAGE' else ''},
                     ensure_ascii=False, indent=1))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(prog='book.py', description='ni-book-downloader')
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('setup', help='环境诊断 / 拉起 Chrome')
    p.add_argument('--launch-chrome', action='store_true')
    p.set_defaults(fn=cmd_setup)

    p = sub.add_parser('quota', help='Z-Library 配额')
    p.set_defaults(fn=cmd_quota)

    p = sub.add_parser('search', help='列候选（不下载）')
    p.add_argument('name')
    p.add_argument('--format', choices=['text', 'pdf', 'any'], default='any')
    p.add_argument('--source', default='github,libgen,zlib,aa',
                   help='逗号分隔: libgen,zlib,aa,github')
    p.add_argument('--author', default='')
    p.add_argument('--lang', default='')
    p.add_argument('--web', action='store_true', help='附带全网搜索结果（网盘/直链）')
    p.add_argument('--limit', type=int, default=10)
    p.set_defaults(fn=cmd_search)

    p = sub.add_parser('get', help='下载指定候选')
    p.add_argument('--source', required=True, choices=['libgen', 'zlib', 'aa', 'github'])
    p.add_argument('--md5', default='', help='libgen/aa 的 md5')
    p.add_argument('--dl', default='', help='zlib 的 /dl/xxx')
    p.add_argument('--link', default='', help='github/网盘的分享链接')
    p.add_argument('--name', required=True)
    p.add_argument('--ext', required=True)
    p.add_argument('--title', default='')
    p.add_argument('--author', default='')
    p.add_argument('--lang', default='')
    p.add_argument('--size', default='')
    p.add_argument('-o', '--outdir', default='.')
    p.set_defaults(fn=cmd_get)

    p = sub.add_parser('auto', help='搜索+选优+下载（含全网兜底）')
    p.add_argument('name')
    p.add_argument('--format', choices=['text', 'pdf', 'any'], default='any',
                   help='text=仅文字版；pdf=仅 PDF；不指定=全量格式允许')
    p.add_argument('--source', default='github,libgen,zlib,aa')
    p.add_argument('--author', default='')
    p.add_argument('--lang', default='')
    p.add_argument('--must-any', default='')
    p.add_argument('--must-not', default='')
    p.add_argument('--loose', action='store_true')
    p.add_argument('--dry', action='store_true')
    p.add_argument('--no-web', action='store_true', help='全部来源失败后不做全网搜索')
    p.add_argument('-o', '--outdir', default='.')
    p.set_defaults(fn=cmd_auto)

    p = sub.add_parser('batch', help='批量（manifest.json）')
    p.add_argument('manifest')
    p.add_argument('--format', choices=['text', 'pdf', 'any'], default='any',
                   help='text=仅文字版；pdf=仅 PDF；不指定=全量格式允许')
    p.add_argument('--source', default='github,libgen,zlib,aa')
    p.add_argument('--dry', action='store_true')
    p.add_argument('--no-web', action='store_true')
    p.add_argument('-o', '--outdir', default='.')
    p.set_defaults(fn=cmd_batch)

    p = sub.add_parser('extract-pdf', help='PDF 文字层提取')
    p.add_argument('pdf')
    p.add_argument('-o', '--out', default='')
    p.set_defaults(fn=cmd_extract_pdf)

    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
