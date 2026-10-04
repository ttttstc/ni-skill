# -*- coding: utf-8 -*-
"""ni-book-downloader 离线冒烟测试：核心纯函数（不触网）。"""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BOOK_PY = os.path.join(HERE, '..', 'scripts', 'book.py')

spec = importlib.util.spec_from_file_location('ni_book', BOOK_PY)
bk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bk)


def _cand(**kw):
    base = {'source': 'zlib', 'title': '', 'author': '', 'lang': 'chinese',
            'ext': 'epub', 'size_bytes': 3 * 1024 * 1024, 'year': '2020'}
    base.update(kw)
    return base


def test_format_filter_text_excludes_pdf():
    spec_ = {'name': '崔玉涛育儿百科', 'format': 'text'}
    assert bk.score_candidate(_cand(title='崔玉涛育儿百科', ext='pdf'), spec_) == -1
    assert bk.score_candidate(_cand(title='崔玉涛育儿百科', ext='epub'), spec_) > 0


def test_format_filter_pdf_excludes_text():
    spec_ = {'name': '崔玉涛育儿百科', 'format': 'pdf'}
    assert bk.score_candidate(_cand(title='崔玉涛育儿百科', ext='epub'), spec_) == -1
    assert bk.score_candidate(_cand(title='崔玉涛育儿百科', ext='pdf'), spec_) > 0


def test_fake_books_rejected():
    spec_ = {'name': 'The Montessori Baby', 'format': 'any', 'lang': 'en'}
    bad = _cand(title='Summary of The Montessori Baby', ext='epub', lang='english')
    assert bk.score_candidate(bad, spec_) == -1


def test_title_mismatch_rejected():
    spec_ = {'name': 'The Montessori Baby', 'format': 'any', 'lang': 'en'}
    other = _cand(title='The Happiest Baby on the Block', ext='epub', lang='english')
    assert bk.score_candidate(other, spec_) == -1


def test_bag_of_words_false_positive_rejected():
    assert not bk.title_ok("There's No Such Thing as Bad Weather: A Scandinavian Mom's Secrets for Raising Healthy Kids", 'No Bad Kids')
    assert bk.title_ok('No bad kids: toddler discipline without shame', 'No Bad Kids')


def test_cjk_isbn_loose():
    spec_ = {'name': '崔玉涛育儿百科', 'format': 'text', 'loose': True,
             'must_any': ['9787508698366', '崔玉涛育儿百科']}
    c = _cand(title='9787508698366', ext='mobi', author='')
    assert bk.score_candidate(c, spec_) > 0
    # 无 must_any 命中仍然拒绝
    c2 = _cand(title='不相关的书', ext='mobi')
    assert bk.score_candidate(c2, spec_) == -1


def test_size_floor():
    spec_ = {'name': 'x', 'format': 'any'}
    assert bk.score_candidate(_cand(title='x', size_bytes=100), spec_) == -1


def test_unspecified_format_allows_all():
    spec_ = {'name': '崔玉涛育儿百科'}
    for ext in ('pdf', 'epub', 'mobi', 'azw3', 'txt'):
        assert bk.score_candidate(_cand(title='崔玉涛育儿百科', ext=ext), spec_) > 0, ext
    spec_pdf = {'name': '崔玉涛育儿百科', 'format': 'pdf'}
    assert bk.score_candidate(_cand(title='崔玉涛育儿百科', ext='epub'), spec_pdf) == -1


def test_verify_file_magic():
    with tempfile.TemporaryDirectory() as td:
        pdf = os.path.join(td, 'a.pdf')
        with open(pdf, 'wb') as f:
            f.write(b'%PDF-1.7' + b'0' * (bk.MIN_SIZE + 10))
        ok, _ = bk.verify_file(pdf, 'pdf')
        assert ok
        bad = os.path.join(td, 'b.pdf')
        with open(bad, 'wb') as f:
            f.write(b'<html>' + b'0' * (bk.MIN_SIZE + 10))
        ok2, msg = bk.verify_file(bad, 'pdf')
        assert not ok2

        epub = os.path.join(td, 'c.epub')
        with open(epub, 'wb') as f:
            f.write(b'PK\x03\x04' + b'0' * (bk.MIN_SIZE + 10))
        assert bk.verify_file(epub, 'epub')[0]

        mobi = os.path.join(td, 'd.mobi')
        with open(mobi, 'wb') as f:
            f.write(b'\x00' * 60 + b'BOOKMOBI' + b'0' * (bk.MIN_SIZE + 10))
        assert bk.verify_file(mobi, 'mobi')[0]


def test_safe_name():
    assert bk.safe_name('a/b:c*d?') == 'a_b_c_d_'
    assert bk.safe_name('书名') == '书名'


def test_size_to_bytes():
    assert bk.size_to_bytes('12 MB') == 12 * 1024 * 1024
    assert bk.size_to_bytes('364 KB') == 364 * 1024
    assert bk.size_to_bytes('') == 0


def test_norm_and_title_ok_cjk():
    assert bk.title_ok('崔玉涛图解家庭育儿 2 母乳与配方粉喂养', '崔玉涛图解家庭育儿_母乳与配方粉喂养')
    assert not bk.title_ok('完全无关的书', '崔玉涛图解家庭育儿_母乳')


IDX_FIXTURE = [
    {'title': '崔玉涛育儿百科', 'author': '崔玉涛', 'language': 'ZH',
     'link': 'https://url89.ctfile.com/f/31084289-100-abc?p=8866', 'formats': ['epub', 'mobi', 'azw3']},
    {'title': '美国儿科学会育儿百科（第6版）', 'author': '谢尔弗', 'language': 'ZH',
     'link': 'https://url89.ctfile.com/f/31084289-200-def?p=8866', 'formats': ['epub']},
    {'title': '无关的书', 'author': 'x', 'language': 'ZH',
     'link': 'https://url89.ctfile.com/f/31084289-300-ghi?p=8866', 'formats': ['epub']},
]


def test_search_github_index():
    hits = bk.search_github('崔玉涛育儿百科', index=IDX_FIXTURE)
    assert len(hits) == 1
    assert hits[0]['source'] == 'github'
    assert hits[0]['ext'] == 'epub'
    assert 'ctfile.com' in hits[0]['id']
    assert bk.search_github('这本书不存在ZZZ', index=IDX_FIXTURE) == []


def test_github_candidate_scores_as_text():
    spec_ = {'name': '崔玉涛育儿百科', 'format': 'text', 'lang': 'zh'}
    cand = bk.search_github('崔玉涛育儿百科', index=IDX_FIXTURE)[0]
    assert bk.score_candidate(cand, spec_) > 0
    spec_pdf = {'name': '崔玉涛育儿百科', 'format': 'pdf', 'lang': 'zh'}
    assert bk.score_candidate(cand, spec_pdf) == -1


def test_ctx_match_filters_unrelated():
    assert bk._ctx_match('崔玉涛育儿百科', '《崔玉涛育儿百科》电子书下载 | 崔玉涛 |')
    assert not bk._ctx_match('崔玉涛育儿百科', '| 崔玉涛自然养育法 | 崔玉涛 | 下载 |')
    assert bk._ctx_match('No Bad Kids', 'download: No Bad Kids epub format')
    assert not bk._ctx_match('No Bad Kids', 'There is No Such Thing as Bad Weather')


def test_extract_links():
    html = '''
    <a href="https://pan.quark.cn/s/abc123">夸克</a>
    https://pan.baidu.com/s/1XyZ_abc
    <a href="https://url89.ctfile.com/f/31084289-123456-abcdef?p=8866">城通</a>
    http://example.com/book.epub 与 https://files.example.org/a/b.pdf?x=1
    '''
    links = bk._extract_links(html)
    kinds = {l['kind'] for l in links}
    urls = [l['url'] for l in links]
    assert {'netdisk', 'ctfile', 'direct'} <= kinds
    assert any('pan.quark.cn/s/abc123' in u for u in urls)
    assert any('ctfile.com/f/31084289-123456-abcdef' in u for u in urls)
    assert any(u.endswith('.epub') for u in urls)
    assert any(u.endswith('.pdf') for u in urls)


def test_extract_links_multi_netdisk():
    html = '''
    https://pan.xunlei.com/s/VNabc123
    https://share.weiyun.com/abcdef
    https://caiyun.139.com/m/i?1A5C8x
    https://drive.uc.cn/s/2a9f1c
    https://www.lanzoub.com/iXyZ12
    https://123684.com/s/xyzABC
    https://cloud.189.cn/t/Ab12Cd
    https://pan.quark.cn/s/deadbeef
    https://mega.nz/file/abcDEF123
    https://drive.google.com/file/d/1AbCdEf/view
    '''
    urls = [l['url'] for l in bk._extract_links(html) if l['kind'] == 'netdisk']
    for frag in ('pan.xunlei.com/s/VNabc123', 'share.weiyun.com/abcdef', 'caiyun.139.com',
                 'drive.uc.cn/s/2a9f1c', 'lanzoub.com/iXyZ12', '123684.com/s/xyzABC',
                 'cloud.189.cn/t/Ab12Cd', 'pan.quark.cn/s/deadbeef', 'mega.nz/file/abcDEF123',
                 'drive.google.com/file/d/1AbCdEf'):
        assert any(frag in u for u in urls), frag


def test_search_engine_list_config():
    assert bk._search_engine_list('sogou,unknown,bing') == ['sogou', 'bing']
    assert bk._search_engine_list('') == ['bing', 'baidu']
    assert bk._search_engine_list('baidu') == ['baidu']


def test_resolve_bing_url():
    u = 'https://www.bing.com/ck/a?!&&p=abc&u=a1aHR0cHM6Ly9leGFtcGxlLmNvbS9ib29rLmVwdWI&ntb=1'
    assert bk._resolve_bing_url(u) == 'https://example.com/book.epub'
    assert bk._resolve_bing_url('https://example.com/x') == 'https://example.com/x'


if __name__ == '__main__':
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f'PASS {fn.__name__}')
        except AssertionError as e:
            failed += 1
            print(f'FAIL {fn.__name__}: {e}')
    print(f'{len(fns) - failed}/{len(fns)} passed')
    sys.exit(1 if failed else 0)
