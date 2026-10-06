#!/usr/bin/env python3
"""受控中文的机械检查。

用法：check.py FILE...（或 - 读 stdin）[--lang auto|zh|en]

只做中文检查（本 skill 面向中文写作）。规则编号对应 references/rules-zh.md 的九章。
默认 --lang auto：一行里汉字数 >= 英文词数时按中文检查。

每命中一行打印：path:line: [规则 级别] 说明: 片段

级别是**检测置信度**，不是规则本身的硬/软（后者见 rules-zh.md）：
  - 确定：机械可判，几乎不误报（万能动词 进行/加以、含糊词 显著/大幅、半角标点、缺空格、范围用 ~）。看到就改。
  - 存疑：靠上下文，**常见误报**（「操作/支持」可能是领域术语、「建议」可能是名词、长句有时该长、
    「的」密集可能本就该拆）。看到先判断，是误报就跳过。
退出码：有「确定」命中返回 1，否则 0。只用标准库；Python 3.8+。

跳过代码围栏、表格分隔行、URL；行内代码与引号里的字不算违规。降噪规则：表格行只做
标点检查、不做词规则（单元格多为标签/数据）；带「不用 / 禁用 / 不写」标记且命中 >=2 个词的
行按「禁用词清单 / 定义行」跳过（提及 ≠ 使用）；同一分句「的」计数只在正文行判定。
"""
import re
import sys

CJK = r'[一-鿿㐀-䶿]'
C = CJK

# (规则, 置信度, 说明, 正则)  —— 置信度：确定 | 存疑
ZH_WORDS = [
    ('3.1', '确定', '万能动词，还原成具体物理动作', r'进行|加以|予以|做出'),
    ('3.1', '确定', '“实现了对……的支持”句式，改回动词', r'实现了?对[^。；，]{1,20}的'),
    ('1.4', '确定', '含糊词，写成数字、名称或条件',
     r'适当|有关的|一定程度上?|较为|基本上|基本(?=[无不没都])|若干|显著|大幅|明显'),
    ('1.5', '存疑', '模糊动词，写出具体动作（领域术语如“操作/支持”可保留）', r'处理|操作|支持|调整|优化'),
    ('3.4', '存疑', '若是表达要求，改用 应/不应/宜/不宜/可/不必', r'必须|务必|最好|尽量|建议'),
    ('1.4', '存疑', '“相关”常是含糊词，写出是哪些', r'相关(?![系性])'),
    ('9.4', '存疑', '套话/成语，写出具体做了什么',
     r'开箱即用|无缝|一劳永逸|飞跃|极致|赋能|抓手|闭环|全方位|强大的'),
    ('9.7', '存疑', 'AI 腔/形式感词，删掉或换成具体说法',
     r'这说明|可以看出|由此可见|综上所述|值得注意|需要指出|具体来说|基于此|有鉴于此|从而|进而|整体而言|随着[^，。]{0,8}的发展'),
    ('3.2', '存疑', '被动句，写出执行主体', r'被[A-Za-z一-鿿]{0,6}(转发|调用|执行|处理|校验|读取|写入|发送|触发|拒绝)'),
    ('3.3', '存疑', '陈述事实不用“正在”', r'正在'),
]

ZH_PUNCT = [
    ('8.1', '确定', '中文旁用了半角标点', rf'{C}[,;:?!]|[,;:?!]{C}|{C}\(|\){C}'),
    ('8.3', '确定', '中文和英文、数字之间缺空格', rf'{C}[A-Za-z0-9]|[A-Za-z0-9]{C}'),
    ('8.6', '确定', '范围用“–”，不用“~”', r'\d\s*[~～]\s*\d'),
]

LIMITS = {'zh': (50, 40)}  # (描述句, 步骤句) 字上限


def language(line, forced):
    if forced != 'auto':
        return forced
    cjk = len(re.findall(C, line))
    words = len(re.findall(r'[A-Za-z]+', line))
    if cjk and cjk >= words:
        return 'zh'
    return None


def length(sentence):
    # 汉字算 1，英文词/数字/代码名各算 1
    return len(re.findall(r"[A-Za-z0-9_.'’-]+", sentence)) + len(re.findall(C, sentence))


def sentences(text):
    return [s.strip() for s in re.split(r'[。？！；]', text) if s.strip()]


def check(path, text, forced):
    hits = []
    in_fence = False
    for n, raw in enumerate(text.split('\n'), 1):
        if raw.lstrip().startswith(('```', '~~~')):
            in_fence = not in_fence
            continue
        if in_fence or re.match(r'^\s*\|?\s*:?-{3,}', raw) or raw.lstrip().startswith('<!--'):
            continue
        line = re.sub(r'`[^`]*`', 'X', raw)
        line = re.sub(r'\]\([^)]*\)', ']', line)
        line = re.sub(r'https?://\S+', 'X', line)
        if language(line, forced) != 'zh':
            continue
        # 标点检查对表格也做（机械、无歧义）
        for rule, conf, msg, pat in ZH_PUNCT:
            for m in re.finditer(pat, line):
                hits.append((n, rule, conf, msg, m.group(0)))
        # 表格行不做词规则：单元格多为标签/数据，词规则命中噪音大
        if line.lstrip().startswith('|'):
            continue
        bare = re.sub(r'“[^”]{1,120}”|「[^」]{1,120}」|"[^"]{1,120}"', '""', line)
        word_hits = []
        for rule, conf, msg, pat in ZH_WORDS:
            for m in re.finditer(pat, bare):
                word_hits.append((rule, conf, msg, m.group(0)))
        # 「禁用词清单 / 定义行」：含 不用/禁用/不写 等标记、且命中 >=2 个词 → 属提及而非使用，跳过
        if not (re.search(r'不用|禁用|不写|别用|删掉|剔除|避免使用', line) and len(word_hits) >= 2):
            for rule, conf, msg, snip in word_hits:
                hits.append((n, rule, conf, msg, snip))
        for clause in re.split(r'[，。；：、？！,;:]', bare):
            if clause.count('的') > 1:
                hits.append((n, '2.1', '存疑', '一个分句里超过一个“的”，考虑拆开', clause.strip()[:30]))
        is_step = re.match(r'^\s*\d+[.、)]\s', line) is not None
        limit = LIMITS['zh'][1] if is_step else LIMITS['zh'][0]
        body = re.sub(r'^\s*(?:[-*+]|\d+[.、)]|#+|>)\s*', '', line)
        for s in sentences(body):
            k = length(s)
            if k > limit:
                rule = '5.4' if is_step else '6.3'
                hits.append((n, rule, '存疑', f'{k} 字 > {limit}（压长句见 explain-patterns 四）', s[:40] + '…'))
    hits.sort(key=lambda h: h[0])
    for n, rule, conf, msg, snip in hits:
        print(f'{path}:{n}: [{rule} {conf}] {msg}' + (f': {snip}' if snip else ''))
    return hits


def main(argv):
    forced = 'auto'
    paths = []
    args = iter(argv)
    for a in args:
        if a == '--lang':
            forced = next(args)
        else:
            paths.append(a)
    if not paths or forced not in ('auto', 'zh', 'en'):
        print(__doc__.strip())
        return 2
    sure = maybe = 0
    for p in paths:
        text = sys.stdin.read() if p == '-' else open(p, encoding='utf-8').read()
        for h in check(p, text, forced):
            sure += h[2] == '确定'
            maybe += h[2] == '存疑'
    print(f'-- {sure} 确定, {maybe} 存疑', file=sys.stderr)
    return 1 if sure else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
