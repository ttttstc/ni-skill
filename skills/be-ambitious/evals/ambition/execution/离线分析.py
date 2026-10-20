"""仅分析本目录 CSV；freeze 与 replay 分开运行，不实施业务操作。Python 标准库。"""
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
RUNS = BASE / "材料" / "运行记录.csv"
ACTIONS = BASE / "材料" / "处理记录.csv"
CUTOFF = "2026-10-07 00:00"
END = "2026-10-10 00:00"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(name, value):
    with (BASE / name).open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)

def read_csv(path, before=None):
    out = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        for line, row in enumerate(csv.DictReader(f), 2):
            if before and row["started_at"] >= before:
                continue
            row["source"] = f"材料/{path.name}:{line}"
            out.append(row)
    return out

def roots(rows):
    by_id = {r["run_id"]: r for r in rows}
    out = {}
    for r in rows:
        current, seen = r["run_id"], set()
        while by_id[current]["rerun_of"]:
            if current in seen:
                raise ValueError("循环：" + current)
            seen.add(current)
            current = by_id[current]["rerun_of"]
            if current not in by_id:
                raise ValueError("缺失父运行：" + current)
        out[r["run_id"]] = current
    return out

RULES = [
    {"id": "R1", "when": "当前显式链已有失败，当前再次失败；优先于其他规则", "main": "停止机械重试，结合阶段核查证据并交人工判断", "basis": ["04→05", "07→08", "12→13", "15→16"]},
    {"id": "R2", "when": "首次 fetch connection reset", "main": "安全、幂等且无持续故障迹象时有条件尝试一次重试", "basis": ["02→03", "10→11"]},
    {"id": "R3", "when": "首次 verify expected / actual 节选", "main": "先核查断言、输入和本提交变更，拒绝仅凭文本认定根因", "basis": ["04", "05"]},
    {"id": "R4", "when": "首次 publish HTTP 403", "main": "先核查原始响应、有效身份、目标与策略，403 不等于权限根因", "basis": ["07", "08"]},
    {"id": "R5", "when": "首次 build No space left on device", "main": "先核查目标挂载、空间、inode 或配额，不自动清理", "basis": ["12", "13"]},
    {"id": "R6", "when": "首次 verify deadline exceeded", "main": "先核查验证步骤、实际耗时、超时配置和资源证据", "basis": ["15", "16"]},
    {"id": "R7", "when": "首次 fetch deadline exceeded；训练段未出现的阶段组合", "main": "先核查拉取超时边界和幂等性，满足条件后才考虑一次重试", "basis": ["fetch 的 02/10", "verify 的 15/16；仅用于指出不能跨阶段直接迁移"]},
    {"id": "R8", "when": "未覆盖或证据不足", "main": "保留未知，补原始错误与定位信息并交人工判断", "basis": ["资料缺少完整日志和独立根因真值"]},
]
PROTOCOL = {
    "support": ["显式关系可重建且不误并不同根事件", "不同阶段能改变核查对象", "链内再次失败能更新状态和建议", "新类型保留未知", "前缀回放不接收未来运行和处理记录"],
    "failure": ["以关键词或时间相近合并独立根", "把 403 或操作后成功写成根因或因果", "建议读取未来运行、未来动作或 recorded_outcome", "链内再失败仍机械重复首轮重试"],
    "effect_evaluation": "只描述已观察的状态变化与建议差异；优于先重试需要独立处置合理性与真实决策结果，当前无此真值。",
    "baseline": "每次失败都先建议重试，包括显式重跑再次失败。",
    "keyword_baseline": "只按精确 log_excerpt 对应通用建议，不看 phase、rerun_of 或次数；未知关键词交人工。关键词不得作事件标识。",
    "action_policy": "所有处理记录在全部建议生成后才读取；历史动作也不进入在线可见上下文，因为动作时间缺失。",
    "identity": "事件 E<显式链根 run_id>；无 rerun_of 的运行保持独立根；跨提交成功只作弱关联候选，不改图、不关闭失败事件。",
    "recovery": "只有当前显式重跑链观察到 success 才标记观察到恢复；其余未解决/恢复未知。",
    "honesty_limit": "执行者初次结构检查已见到完整静态 CSV；因此这不是对执行者盲化的前瞻试验。程序级前缀隔离可核对，但无法证明规则设计者未受留出数据影响。",
}
KEYWORDS = {
    "connection reset": "有条件尝试一次重试",
    "expected 2 actual 3": "先核查期望与实际差异",
    "HTTP 403": "先核查 403 原始响应与上下文",
    "No space left on device": "先核查容量证据",
    "deadline exceeded": "先核查超时证据",
}

def decide(prefix, frozen):
    """仅接受当前及更早运行，不接受处理记录、未来状态或全量运行索引。"""
    current = prefix[-1]
    assert current["status"] == "failed"
    lineage = roots(prefix)
    root = lineage[current["run_id"]]
    earlier = prefix[:-1]
    chain_failures = [r for r in earlier if lineage[r["run_id"]] == root and r["status"] == "failed"]
    history = []
    for r in earlier:
        if r["status"] == "failed" and r["phase"] == current["phase"] and r["log_excerpt"] == current["log_excerpt"] and lineage[r["run_id"]] != root:
            event = "E" + lineage[r["run_id"]]
            if event not in history:
                history.append(event)
    phase, excerpt = current["phase"], current["log_excerpt"]
    shared = "完整日志、任务/环境/runner 标识、失败步骤与影响范围"
    if chain_failures:
        rule = "R1"
        specific = {"verify": "断言或超时的原始位置、输入/配置和本提交变更", "publish": "响应体/头、有效身份、目标和策略/网关证据", "build": "目标挂载、可用空间、inode/配额和容量变化", "fetch": "请求失败位置、上游状态与超时边界"}.get(phase, "原始失败位置")
        main = "停止机械重试，先核查" + specific + "并交人工决定"
        reason = "显式同链已有失败：" + ",".join(r["run_id"] for r in chain_failures) + "；当前再次失败，一次重跑已未解除观察到的故障"
        condition = "当前属于登记的同一链；任何后续操作仍需新证据和相应授权"
        distinguish = "区分持续的输入/环境/策略问题与单次扰动；当前不能确定哪一种"
        overturn = "新证据确认环境已改变、故障是短时外因且已解除，或原关联被证明登记错误"
        missing = specific + "；" + shared
    elif phase == "fetch" and excerpt == "connection reset":
        rule = "R2"
        main = "在确认拉取安全、幂等且无持续外部故障迹象后，有条件尝试一次重试"
        reason = "fetch 的连接中断节选符合短时故障候选；不是短时故障的证明"
        condition = "确认没有非幂等副作用、无拒绝/持续异常证据，且仅一次；材料未提供这些前提"
        distinguish = "同提交同阶段一次重跑是否仍失败；成功也不能证明网络根因"
        overturn = "重跑再次失败、持续服务异常或发现身份/配置等稳定差异"
        missing = "请求/网络与上游证据、幂等性、同环境确认；" + shared
    elif phase == "verify" and "expected" in excerpt and "actual" in excerpt:
        rule = "R3"
        main = "先核查原始断言、输入和本提交变更，再决定是否需要重跑或修正"
        reason = "节选出现期望/实际不一致，可定位核查方向，尚无根因证据"
        condition = "错误确实来自当前验证步骤；需完整错误和输入确认"
        distinguish = "稳定输入/逻辑差异与不稳定测试或环境差异"
        overturn = "发现不稳定输入/外部依赖证据或同环境可复现结果与节选不一致"
        missing = "断言位置、测试输入、完整错误、本提交 diff；" + shared
    elif phase == "publish" and excerpt == "HTTP 403":
        rule = "R4"
        main = "先核查原始响应、有效身份、发布目标和策略/网关证据，再决定处置"
        reason = "403 是拒绝响应的节选；身份、目标策略、网关等均只是候选解释"
        condition = "确认响应来自哪个请求和哪一跳；不据此改权限"
        distinguish = "身份/策略/目标差异与网关或上游临时拒绝"
        overturn = "证实是已解除的上游临时故障且重试安全，或原状态码/阶段记录错误"
        missing = "响应体/头、请求目标、有效身份、策略和上游状态；" + shared
    elif phase == "build" and excerpt == "No space left on device":
        rule = "R5"
        main = "先核查报错目标挂载、空间、inode/配额，再由人工判断容量处置"
        reason = "节选提示容量路径，可有空间、inode、配额或目标挂载等不同解释"
        condition = "取得失败路径和实际容量证据，不自动执行 runner 清理"
        distinguish = "定位真正受限的资源与影响范围"
        overturn = "容量证据充足且节选指向不同远端资源，或错误已因外部变化解除"
        missing = "失败路径、挂载、空间/inode/配额、共享 runner 信息；" + shared
    elif phase == "verify" and excerpt == "deadline exceeded":
        rule = "R6"
        main = "先核查验证步骤耗时、超时配置、输入和资源证据，再决定处置"
        reason = "verify 的超时节选和运行耗时只表明超时现象，不能判断慢测、资源或外部依赖根因"
        condition = "明确超时发生层、实际预算和同环境可比性"
        distinguish = "测试/输入慢、资源限制、外部等待和预算不匹配"
        overturn = "原始证据确认一次性外部扰动且已恢复，并且重试安全"
        missing = "步骤级耗时、deadline 来源、资源/依赖证据、可比基线；" + shared
    elif phase == "fetch" and excerpt == "deadline exceeded":
        rule = "R7"
        main = "先核查拉取超时位置、实际预算与幂等性；若短时外因已解除且安全，再考虑一次重试"
        reason = "训练中同词仅见于 verify；fetch 的请求/传输证据不同，不能套用验证步骤解释"
        condition = "属于新阶段组合；确认安全、幂等、无持续拒绝和持续故障证据后才可一次重试；这些前提目前未知"
        distinguish = "请求/传输等待、上游慢和超时配置差异；一次重跑可观察是否持续"
        overturn = "发现持续故障、身份/配置问题、非幂等影响或一次重跑仍失败"
        missing = "请求/上游时序、超时来源、幂等性与运行环境；" + shared
    else:
        rule = "R8"
        main = "信息不足，补原始错误位置、本提交 diff 和环境信息，交人工判断"
        reason = "训练规则未覆盖该阶段/节选组合；文本可作定位入口，不能据此确认诊断"
        condition = "取得完整日志和错误位置后才选择后续操作"
        distinguish = "源代码、生成文件、配置或执行环境等候选来源"
        overturn = "新证据定位了可验证的问题，或确认节选与当前失败不相符"
        missing = "错误文件/行/命令、提交 diff、生成步骤与环境；" + shared
    assert rule in {r["id"] for r in frozen["rules"]}
    return {
        "run_id": current["run_id"], "time": current["started_at"], "event": "E" + root,
        "source": current["source"], "rule": rule, "fact": f'{phase} / {excerpt} / commit={current["commit"]} / duration_s={current["duration_s"]}',
        "main_next_step": main, "reason": reason, "conditions": condition,
        "distinguish": distinguish, "overturn": overturn, "missing_evidence": missing,
        "history_events": history, "already_visible_chain_failures": [r["run_id"] for r in chain_failures],
        "visible_run_ids": [r["run_id"] for r in prefix], "max_visible_time": max(r["started_at"] for r in prefix),
        "handling_records_visible": False, "recorded_outcome_visible": False,
        "baseline": frozen["evaluation"]["baseline"],
        "keyword_baseline": frozen["keyword_rules"].get(excerpt, "新关键词，信息不足，交人工"),
    }

def freeze():
    training = read_csv(RUNS, before=CUTOFF)
    assert len(training) == 17
    artifact = {
        "stage": "freeze", "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "train_range": ["2026-10-01", "2026-10-06"], "holdout_range": ["2026-10-07", "2026-10-09"],
        "train_run_ids": [r["run_id"] for r in training], "training_sha256": hashlib.sha256(json.dumps(training, ensure_ascii=False, sort_keys=True).encode()).hexdigest(),
        "implementation_sha256": digest(Path(__file__)), "rules": RULES, "keyword_rules": KEYWORDS,
        "evaluation": PROTOCOL, "training_decision_count": sum(r["status"] == "failed" for r in training),
        "handling_records_read": False,
    }
    dump("冻结规则.json", artifact)
    print(json.dumps({"frozen": "冻结规则.json", "sha256": digest(BASE / "冻结规则.json"), "train_runs": len(training), "handling_records_read": False}, ensure_ascii=False))

def quality(rows, actions):
    ids = [r["run_id"] for r in rows]
    issues = []
    if len(ids) != len(set(ids)):
        issues.append("run_id 重复")
    by_id = {r["run_id"]: r for r in rows}
    for r in rows:
        datetime.strptime(r["started_at"], "%Y-%m-%d %H:%M")
        assert int(r["duration_s"]) >= 0
        parent = r["rerun_of"]
        if parent:
            if parent not in by_id:
                issues.append("引用不存在：" + r["run_id"])
            else:
                p = by_id[parent]
                if p["started_at"] >= r["started_at"]:
                    issues.append("时间不递增：" + r["run_id"])
                if p["commit"] != r["commit"] or p["phase"] != r["phase"]:
                    issues.append("重跑提交或阶段变化：" + r["run_id"])
                if p["status"] != "failed":
                    issues.append("父运行非失败：" + r["run_id"])
    lineage = roots(rows)
    for a in actions:
        if a["run_id"] not in by_id or by_id[a["run_id"]]["status"] != "failed":
            issues.append("处理记录引用异常：" + a["run_id"])
        assert int(a["active_minutes"]) >= 0
    return {
        "run_fields": list(rows[0].keys())[:-1], "action_fields": list(actions[0].keys())[:-1],
        "runs": len(rows), "failures": sum(r["status"] == "failed" for r in rows), "actions": len(actions),
        "time_range": [rows[0]["started_at"], rows[-1]["started_at"]], "action_time_range": "未知：无动作时间字段",
        "missing_run_fields": {k: sum(r[k] == "" for r in rows) for k in rows[0] if k != "source"},
        "missing_action_fields": {k: sum(r[k] == "" for r in actions) for k in actions[0] if k != "source"},
        "issues": issues, "explicit_edges": sum(bool(r["rerun_of"]) for r in rows),
        "root_count_all_runs": len(set(lineage.values())), "root_count_failed_events": len({lineage[r["run_id"]] for r in rows if r["status"] == "failed"}),
        "input_sha256": {"运行记录.csv": digest(RUNS), "处理记录.csv": digest(ACTIONS), "资料说明.md": digest(BASE / "材料" / "资料说明.md"), "任务.md": digest(BASE / "任务.md")},
    }

def report(rows, actions, frozen, decisions, associations, qa, audit):
    by_id = {r["run_id"]: r for r in rows}
    action_by = {a["run_id"]: a for a in actions}
    ds = {d["run_id"]: d for d in decisions}
    hold = [d for d in decisions if d["time"] >= CUTOFF]
    lines = []
    def p(s=""):
        lines.append(s)
    p("# CI 值班 Agent 离线验证答复")
    p()
    p("结论：**可行性尚未证实**。本轮可复现显式链关联、按证据更新卡片、按阶段提出不同的核查方向，以及保留未知；没有证据证明建议优于‘每次失败都先重试’。这不能作为上线验收。")
    p()
    p("还有一项必须披露的方法限制：初次检查时执行者已经读取完整静态 CSV，包括 10 月 7—9 日记录。后续程序在冻结规则后执行前缀回放，决策函数不接收未来运行或任何处理记录；其输入边界可以审计。但这不是执行者盲化的留出试验，无法排除规则设计受已见答案影响。若通过条件要求整个设计过程也未见留出答案，本轮严格留出条件**未通过**，须用另一批未用材料复验。没有发现程序决策读取未来的具体案例，不能把这个程序检查升级为全程无泄漏证明。")
    p()
    p("## 1. 数据检查与证据入口")
    p()
    p(f"实际运行 Python 标准库分析。运行记录 {qa['runs']} 条：14 失败、10 成功；处理记录 {qa['actions']} 条。运行时间 {qa['time_range'][0]} 至 {qa['time_range'][1]}；时间无时区/秒，不能额外推断动作顺序或持续故障区间。处理动作时间范围未知。")
    p()
    p("| 文件 | 字段与含义 | 缺失/边界 |")
    p("|---|---|---|")
    p("| 运行记录.csv | run_id 字符串；started_at 开始时间；commit；phase；status；duration_s；log_excerpt；rerun_of | log_excerpt 空 10 条，均为成功；rerun_of 空 13 条；其余字段无空值。保留 01 等前导零。 |")
    p("| 处理记录.csv | run_id；action；recorded_outcome；active_minutes | 14 条均对应存在的失败 run_id；无重复/空项，但完全没有动作时间、操作者、操作详情和目标成功运行。 |")
    p("| 资料说明.md | 同仓库、rerun_of 含义、处置/活动时间限制 | 未给完整日志、根因真值、真实通知/接收人、生产负载和在线系统。 |")
    p()
    p("11 条 rerun_of 边均可找到父记录，无断链、循环、逆时间边；边两端 commit/phase 一致，父运行均失败。全量图有 13 个独立根，其中 9 个含失败。无 rerun_of 只表示未登记，不能认定现实中绝无关联。commit 仅标识，缺少 diff；phase 是记录标签，未提供步骤配置；duration_s 不是动作时间或超时预算。处理记录按 run_id 归档到事件，不能据此确认动作何时发生。")
    p()
    p("[运行原表](" + str(RUNS).replace('\\', '/') + ")、[处理原表](" + str(ACTIONS).replace('\\', '/') + ")。以下 source 均指 CSV 的物理行，表头为第 1 行。节选仅是证据入口，不是完整日志。输入 SHA-256 保存在数据检查.json/审计.json。")
    p()
    p("## 2. 冻结的规则、评判口径和关联边界")
    p()
    p("先由 freeze 命令选取 10 月 1—6 日共 17 次运行、6 个失败事件、10 个失败决策时点，写入冻结规则.json；该阶段不读处理表。随后 replay 校验冻结时的脚本 SHA-256，再产生逐时建议。冻结后未修改规则。完整文件指纹见审计.json。训练段建议是样本内逐时上下文演示，不充当独立效果评估。")
    p()
    p("事件 ID=E+显式链根 run_id。只有 rerun_of 可并入事件；相同阶段/节选的不同根只可引用历史。跨提交、未登记的成功只作弱关联候选，不改事件图。显式链出现 success 才标记‘观察到恢复’，含义仅为该链后来成功。")
    p()
    p("| 优先序 | 适用条件 | 主要下一步 | 训练依据 |")
    p("|---|---|---|---|")
    for r in frozen["rules"]:
        p(f"| {r['id']} | {r['when']} | {r['main']} | {'；'.join(r['basis'])} |")
    p()
    p("R7 是冻结时写下的跨阶段迁移限制，不是从 fetch timeout 的已知结果估计概率；但执行者已见静态留出材料，仍受前述非盲限制。规则不读取处理动作；没有动作时间，连训练段的历史处置也不能假定在某次回放时已经可用。历史可引用的只有早于当次的运行观察。")
    p()
    p("评判前置：支持假设的结果是关联可追溯、不误并、阶段能改变核查对象、重跑失败后能更新、陌生错误能保留未知，且建议函数只用时间前缀。失败标准是关键词/时间误并、无依据根因诊断、因果越界、未来输入或机械重复重试。处置合理性和根因没有独立真值，统一列为待领域评审；另一个模型的赞同与 recorded_outcome 均不能替代。")
    p()
    p("主要对照固定为每次失败都先建议重试。关键词对照固定按节选给通用动作：connection reset→有条件重试；expected/actual→核查差异；403→核查响应；No space→核查容量；deadline→核查超时；未知词→交人工。它不看 phase、显式链和次数。后续观察只分‘与建议方向相容/存在张力/无法判断’，不产生自评分，也不推算生产效果。")
    p()
    p("## 3. 显式关系与跨提交候选")
    p()
    p("| 事件 | 原始运行链 | 当前观测状态 | 其他关联 |")
    p("|---|---|---|---|")
    for e in associations:
        p(f"| {e['event']} | {e['chain']} | {e['state']} | {e['candidate_recovery']} |")
    p()
    p("具体例子：07→08→09 是同一事件 E07，08 的新失败应更新原卡；22→23→24 是 E22，commit=a13、日期不同且没有接到 E07 的 rerun_of，必须创建新卡。22 时可引用 E07 的重复失败后成功观察，不能把 permission_change 当作当时已知经验，更不能断定这轮也需改权限。02/10 也只是两个独立的相似事件。")
    p()
    p("15/16 是 verify 的 deadline，18 是 fetch 的 deadline：前者核查验证步骤/输入/资源/预算，后者核查请求/传输/上游/预算。不能因关键词相同合并 E15 与 E18，也不能把 verify 的重复失败直接当成 fetch 重试必败。当前材料只显示它们耗时不同，不足以推断不同根因。")
    p()
    p("06(a04)、17(a09)、21(a12) 与相应失败提交不同，phase 和时间先后与事后 change_commit/recovered 记录相容；没有 rerun_of、动作时间或目标运行映射，故仅作 E04/E15/E20 的弱候选。它们仍是独立图根，不关闭这三个失败事件。‘没有登记’也不排除现实中的关联。")
    p()
    p("## 4. 每次失败时的主要建议")
    p()
    p("以下 14 次均只向 decide 传入截至当次的运行。‘历史’只列当时已可见的同阶段同节选独立事件；处理表全部隐藏。详细条件、反证与缺证在逐次建议.json 中逐项保存。")
    p()
    p("| run / 原始证据 | 事件 / 规则 / 可用历史 | 主要下一步及依据 |")
    p("|---|---|---|")
    for d in decisions:
        p(f"| {d['run_id']} / {d['source']}；{d['fact']} | {d['event']} / {d['rule']} / {','.join(d['history_events']) or '无'} | {d['main_next_step']}。依据：{d['reason']}。 |")
    p()
    p("适用条件与反证不是免责声明，而是建议的一部分：02/10 的一次重试须先确认幂等、安全和无持续异常；重跑仍失败会推翻继续重试。04 的核查方向会被不稳定输入证据改变。07/22 的 403 建议会被已确认且已解除的临时上游故障改变。12 须核对真正受限的挂载/配额；15 须明确超时层与预算。05/08/13/16/23 已有重复失败，新上下文改变或关联登记有误才可重新评估重试。以上均是待验证的决策条件，没有自动触发业务操作。")
    p()
    p("## 5. 10 月 7—9 日逐条回放")
    p()
    p("留出分母：7 次运行、3 个独立失败事件（E18/E20/E22）、4 个失败决策时点（18/20/22/23）。E22 的两次失败不是两个独立案例。程序每次传入前缀并记录 visible_run_ids/max_visible_time，全部建议生成完才读取处理表。成功运行只更新观察状态，不生成失败建议。")
    p()
    p("| 当次时间 | run / commit / phase / 状态 / rerun_of | 当次处理 |")
    p("|---|---|---|")
    for r in rows:
        if r["started_at"] >= CUTOFF:
            effect = f"{ds[r['run_id']]['event']}：{ds[r['run_id']]['main_next_step']}" if r["status"] == "failed" else ("更新 E" + r["rerun_of"] + " 所属显式链为观察到恢复" if r["rerun_of"] else "独立成功根；仅登记弱候选，不关闭 E20")
            if r["run_id"] == "24":
                effect = "更新 E22（22→23→24）为观察到恢复"
            p(f"| {r['started_at']} | {r['run_id']} / {r['commit']} / {r['phase']} / {r['status']} / {r['rerun_of'] or '空'} | {effect}；{r['source']} |")
    p()
    later = {
        "18": ("19 明确 rerun_of=18，同提交 a10/fetch，success；处理表 18=retry/recovered/4 分钟。", "与有条件一次重试方向相容，但前提证据缺失；对照也建议重试，未证明优势。一次成功不证明短时网络根因或恢复概率。"),
        "20": ("21 为 a12/build/success，rerun_of 空；处理表 20=change_commit/recovered/15 分钟。", "仍无显式恢复；与补证定位方向相容但不能验证建议优于重试。未采取原提交重试的反事实未知；21 不能作为确定修复证据。"),
        "22": ("23 明确 rerun_of=22，同提交 a13/publish，仍 HTTP 403 failed；处理表 22=retry/not_recovered/6 分钟。", "新增重复失败证据表明该次重跑未解除故障，与先核查而不盲重试方向相容；没有执行核查替代方案的结果，不能证明其更好。"),
        "23": ("24 明确 rerun_of=23，同提交 a13/publish，success；处理表 23=permission_change/recovered/12 分钟。", "与保留证据后再决定的建议不矛盾，但后来的成功对任何‘重复失败后必须改权限/不会再成功’强规则构成反例。当前建议未作该断言；成功原因、操作时间和纯重试结果均未知。"),
    }
    for d in hold:
        observed, interpretation = later[d["run_id"]]
        p(f"### 决策 {d['run_id']}（{d['event']}，{d['time']}）")
        p()
        p(f"当时可见：{d['source']}，{d['fact']}；链内先前失败={','.join(d['already_visible_chain_failures']) or '无'}；可引用历史={','.join(d['history_events']) or '无'}。最多只见运行 {d['visible_run_ids'][-1]}。看不到后来的 { {'18':'19','20':'21','22':'23/24','23':'24'}[d['run_id']] }，也看不到任何处理动作/结果。")
        p()
        p(f"建议：{d['main_next_step']}。适用条件：{d['conditions']}。要区分：{d['distinguish']}。推翻条件：{d['overturn']}。缺证：{d['missing_evidence']}。")
        p()
        p(f"对照：每次失败都先重试；关键词对照={d['keyword_baseline']}。")
        p()
        p(f"事后观察：{observed} **处置记录是记录者说法，非动作因果或根因真值。** {interpretation}")
        p()
    p("## 6. 事件处置卡（最终离线快照）")
    p()
    p("这些卡包含事后处理记录，不能倒灌到上述当时建议。当前下一步只描述离线跟进；‘已做操作’是记录中声称已做，动作时间未知。")
    p()
    for e in associations:
        group = [r for r in rows if e["root"] == e["lineage"][r["run_id"]]]
        failures = [r for r in group if r["status"] == "failed"]
        last = ds[failures[-1]["run_id"]]
        p(f"### {e['event']}")
        p()
        p("| 字段 | 内容 |")
        p("|---|---|")
        p(f"| 事件标识、关联运行 | {e['event']}；{e['chain']}；仅显式边归并。 |")
        p(f"| 当前状态 | {e['state']}；{e['candidate_recovery']} |")
        p("| 观察到的事实 | " + "；".join(f"{r['run_id']}={r['status']}({r['commit']}/{r['phase']}/{r['duration_s']}s，{r['source']})" for r in group) + "；失败节选：" + failures[0]["log_excerpt"] + "。 |")
        p("| 候选解释 | " + last["distinguish"] + "；均未获根因确认。 |")
        p("| 已做操作 | " + "；".join(f"{r['run_id']}：{action_by[r['run_id']]['action']}，记录结果={action_by[r['run_id']]['recorded_outcome']}，active_minutes={action_by[r['run_id']]['active_minutes']}（{action_by[r['run_id']]['source']}）" for r in failures) + "；全部动作时间未知。 |")
        next_step = "保留为观察到恢复的历史卡，补齐证据与动作时间；若再次出现独立根，创建新卡。" if e["recovered"] else last["main_next_step"]
        p(f"| 下一步及理由 | {next_step} 理由：{last['reason']}；是否真正解除原故障、为何成功仍无独立证据。 |")
        p(f"| 引用的历史事件 | {','.join(last['history_events']) or '无可按同阶段同节选引用的更早独立事件'}；只用当时可见运行观察。 |")
        p(f"| 待补证据 | {last['missing_evidence']}；动作时间/目标运行映射、独立根因与处置合理性评审。 |")
        p()
    p("## 7. 对照结果与推翻尝试")
    p()
    p("| 检查 | 数量/分母与结果 | 能证明的边界 |")
    p("|---|---|---|")
    p("| 显式关联 | 11/11 边合法；9 个失败事件；本方法错误归并 0 个可从材料确认的案例 | 只证明忠实于登记关系，不是真实事件边界真值。 |")
    p("| 同链更新 | 5/5 再失败决策（05/08/13/16/23）进入 R1；留出 1/1（23） | 状态与建议会更新，不证明停止盲重试的生产收益。 |")
    p("| 留出建议差异 | 4/4 时点先核查或保留未知；18 含补证后一次重试条件。基线 4/4 直接先重试。关键词对照 22/23 会重复同一通用建议 | 建议差异可观察，合理性待领域评审。 |")
    p("| 留出重跑状态 | 有显式子运行的决策 3/4：18→19 成功、22→23 失败、23→24 成功，2/3 成功边、1/3 失败边；涉及 2/3 事件 | 23 后另记录改权限且无动作时间，不能将 2/3 称为纯重试成功率，更不能预测未来概率。20 没有显式重跑。 |")
    p("| 独立事件恢复 | 留出 2/3 事件链有成功（E18/E22），1/3 无显式恢复（E20）；全量 6/9 有链内成功、3/9 仍未知 | 不把跨提交成功或记录者 recovered 算入确认恢复。 |")
    p("| 动作记录核对 | 留出 4 条记录：3 条 recovered（18/20/23），1 条 not_recovered（22）；有链内成功对应的 recovered 2/3（18/23），20 只有跨提交弱候选 | 无法给动作打因果标签，未采取的另一操作无反事实。 |")
    p("| 效果比较 | 优于基线的可独立证实案例 0/3 个留出事件；4 个决策的领域正确性均无独立真值 | 不能把 0 当失败率，也不能把方向相容当获益；缺少可比较的真实结果。 |")
    p("| 前缀检查 | 14/14 决策输入不含未来运行或处理表；留出 4/4 通过程序断言 | 设计者见过整表，不能宣称全程盲化留出通过。 |")
    p()
    p("主动反驳结果：")
    p()
    p("1. **相同词不同阶段**：E15/16 对 E18 的核查对象不同；支持阶段有信息，但18后来成功不能证实阶段规则更优。关键词对照给二者同一句‘核查超时’，遗漏了证据对象。")
    p("2. **同链再失败**：23 相比22多了22→23失败事实，进入R1；05/08/13/16也如此。若将R1强化为‘再失败后永远不应重试’，09/14/24后来的链内成功构成张力/反例；当前规则只反对无新证据的机械重复，保留重新决策。")
    p("3. **新错误**：20 build/syntax error没有训练对应例，R8保留未知；后续21跨提交成功不证明语法修复或建议正确。18属于已知词的新阶段组合，也明确缺证。")
    p("4. **新轮相似失败**：E22引用E07的运行观察但创建新卡；E10引用E02。若按精确关键词归并，全量会把9个失败事件压成6组，其中3组跨独立根（connection reset、HTTP 403、deadline exceeded）；这是反事实的错误方法，本方法没有采用。")
    p("5. **未来/因果审计**：处理表到建议生成完成后才读，所有visible_run_ids时间不晚于当前；不得把08/23的permission_change/recovered当成07/22时已知事实。无根因/效果结论依赖它们。执行者已见留出仍是无法消除的方法污染，不用程序断言掩盖。")
    p()
    p("核心假设只能支持到：phase与显式链使建议拥有更具体的证据入口，能维护事件身份和状态。**‘历史处置使建议更有依据’尚未得到严格验证**：动作时间缺失，不能合法放入逐时上下文；记录也无独立真值。‘比先重试更好’无从证实。22后的重跑失败是有用新证据，18后的成功和23后的成功也提醒我们不能据小样本排斥重试。")
    p()
    p("active_minutes仅随卡片复述已记录活动，未计算节省；没有通知/接收人，不计算重复通知减少。没有故障减少、人工时间减少或上线SLA结论。")
    p()
    p("## 8. 下一轮唯一验证动作与停止点")
    p()
    p("做一次**领域专家盲评的时间前缀影子回放**：使用另一批尚未查看的连续CI事件，沿用本次冻结规则，不操作CI。每次只给当时可见的运行与已发生且有时间戳的处置记录，记录本方法和先重试基线；由不了解推荐来源的值班领域专家核查证据充分性、适用条件、危险操作边界与事件关联。后续结果仍只当观察，不替代根因真值。需补动作时间、动作详情、rerun/部署目标关联、经过脱敏的完整失败日志与独立复盘结论。只需这批材料的只读导出授权，无写入或生产处置权限。")
    p()
    p("这一个动作同时修复本次执行者已见留出的问题，补足历史处置的可见时点，并提供独立合理性评审。若需调整本次规则，必须另留一批未用数据，不能改后重报本批。下一轮也不能凭专家偏好直接声称生产收益；收益须另有受控的真实决策证据。")
    p()
    p("本轮止于离线证据和下一轮建议。没有建设Agent、改代码/配置、联网、安装依赖或执行任何重试/改权限/清理runner。脚本仅为可复现分析产物。")
    p()
    p("## 9. 可复现产物")
    p()
    p("脚本：离线分析.py；冻结：冻结规则.json；数据检查：数据检查.json；全量事件关联：事件关联.json；当时建议与可见运行ID：逐次建议.json；逐条运行：时间线.json；回放与静态检查：审计.json；完整答复：答复.md。")
    p()
    p("本次实际依次执行：`rtk proxy python 离线分析.py freeze`、`rtk proxy python 离线分析.py replay`。为保护已有产物，脚本以新建模式写文件；复现可在本目录新建副本产物名，或先由材料持有人安排一份相同的新目录。不可用复现来修改原始材料。")
    (BASE / "答复.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def replay():
    frozen_path = BASE / "冻结规则.json"
    frozen_bytes = frozen_path.read_bytes()
    frozen = json.loads(frozen_bytes)
    assert frozen["implementation_sha256"] == digest(Path(__file__)), "冻结后脚本发生变化"
    rows = sorted(read_csv(RUNS), key=lambda r: (r["started_at"], r["run_id"]))
    assert all(r["started_at"] < END for r in rows)
    decisions, timeline, prefix = [], [], []
    for r in rows:
        prefix.append(dict(r))
        decision = decide(tuple(dict(x) for x in prefix), frozen) if r["status"] == "failed" else None
        if decision:
            assert decision["max_visible_time"] <= r["started_at"]
            assert not decision["handling_records_visible"]
            assert not decision["recorded_outcome_visible"]
            decisions.append(decision)
        timeline.append({"run": dict(r), "decision": decision})
    # 直到所有当时建议生成完才读取处理表；不得移动到上述循环前。
    actions = read_csv(ACTIONS)
    qa = quality(rows, actions)
    assert not qa["issues"], qa["issues"]
    lineage = roots(rows)
    groups = defaultdict(list)
    for r in rows:
        groups[lineage[r["run_id"]]].append(r)
    candidate = {"04": "06(a04)为弱候选，源处理记录05 change_commit/recovered；无显式关系，不关闭", "15": "17(a09)为弱候选，源处理记录16 change_commit/recovered；无显式关系，不关闭", "20": "21(a12)为弱候选，源处理记录20 change_commit/recovered；无显式关系，不关闭"}
    associations = []
    for root, group in groups.items():
        if not any(r["status"] == "failed" for r in group):
            continue
        recovered = any(r["status"] == "success" for r in group)
        associations.append({"event": "E" + root, "root": root, "runs": [r["run_id"] for r in group], "chain": "→".join(r["run_id"] + ("(成功)" if r["status"] == "success" else "(失败)") for r in group), "state": "观察到恢复；原因未知" if recovered else "未解决/恢复未知", "recovered": recovered, "candidate_recovery": candidate.get(root, "无额外候选"), "lineage": lineage})
    hold = [d for d in decisions if d["time"] >= CUTOFF]
    audit = {
        "frozen_sha256": hashlib.sha256(frozen_bytes).hexdigest(), "implementation_matches_freeze": True,
        "source_sha256": qa["input_sha256"], "no_rule_change_after_freeze": True,
        "all_decision_points": len(decisions), "holdout_decision_points": len(hold), "holdout_failed_events": len({d["event"] for d in hold}),
        "max_time_checks_passed": len(decisions), "handling_table_read_after_all_decisions": True,
        "independent_causal_truth_available": False, "analyst_blinded_to_holdout": False,
        "strict_blind_holdout_pass": False,
        "decision_function_future_input_detected": False,
        "verdict": "可行性尚未证实；程序前缀检查通过，全程盲化留出条件未通过。",
        "no_business_operations_performed": True,
    }
    assert len(rows) == 24 and len(decisions) == 14 and len(hold) == 4
    assert len(associations) == 9 and qa["explicit_edges"] == 11
    assert [d["run_id"] for d in decisions if d["rule"] == "R1"] == ["05", "08", "13", "16", "23"]
    assert next(d for d in hold if d["run_id"] == "22")["history_events"] == ["E07"]
    for name, value in [("数据检查.json", qa), ("事件关联.json", associations), ("逐次建议.json", decisions), ("时间线.json", timeline), ("审计.json", audit)]:
        dump(name, value)
    report(rows, actions, frozen, decisions, associations, qa, audit)
    assert frozen_bytes == frozen_path.read_bytes()
    assert qa["input_sha256"]["运行记录.csv"] == digest(RUNS)
    assert qa["input_sha256"]["处理记录.csv"] == digest(ACTIONS)
    print(json.dumps({"artifacts": ["答复.md", "冻结规则.json", "数据检查.json", "事件关联.json", "逐次建议.json", "时间线.json", "审计.json"], "runs": len(rows), "failures": len(decisions), "holdout_events": len({d['event'] for d in hold}), "holdout_decisions": len(hold), "verdict": audit["verdict"]}, ensure_ascii=False))

if __name__ == "__main__":
    if sys.argv[1:] == ["freeze"]:
        freeze()
    elif sys.argv[1:] == ["replay"]:
        replay()
    else:
        raise SystemExit("使用：python 离线分析.py freeze 或 replay")
