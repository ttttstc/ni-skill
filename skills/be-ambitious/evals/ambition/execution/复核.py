"""核对产物并修正报告表述；不修改冻结规则、分析脚本、建议或原材料。"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

base = Path(__file__).resolve().parent
load = lambda name: json.loads((base / name).read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
frozen = load("冻结规则.json")
audit = load("审计.json")
decisions = load("逐次建议.json")
events = load("事件关联.json")
quality = load("数据检查.json")
assert sha(base / "离线分析.py") == frozen["implementation_sha256"]
assert sha(base / "冻结规则.json") == audit["frozen_sha256"]
for name, value in quality["input_sha256"].items():
    path = base / name if name == "任务.md" else base / "材料" / name
    assert sha(path) == value
with (base / "材料" / "运行记录.csv").open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))
by_id = {r["run_id"]: r for r in rows}
assert len(rows) == len(by_id) == 24
for d in decisions:
    current = by_id[d["run_id"]]
    expected = [r["run_id"] for r in rows if r["started_at"] <= current["started_at"]]
    assert d["visible_run_ids"] == expected
    assert not d["handling_records_visible"] and not d["recorded_outcome_visible"]
assert {e["event"]: e["runs"] for e in events} == {
    "E02": ["02", "03"], "E04": ["04", "05"], "E07": ["07", "08", "09"],
    "E10": ["10", "11"], "E12": ["12", "13", "14"], "E15": ["15", "16"],
    "E18": ["18", "19"], "E20": ["20"], "E22": ["22", "23", "24"],
}
assert sum(e["recovered"] for e in events) == 6
assert Counter(by_id[d["run_id"]]["log_excerpt"] for d in decisions) == Counter({"connection reset": 2, "expected 2 actual 3": 2, "HTTP 403": 4, "No space left on device": 2, "deadline exceeded": 3, "syntax error": 1})
text = (base / "答复.md").read_text(encoding="utf-8")
old = "若通过条件要求整个设计过程也未见留出答案，本轮严格留出条件**未通过**，须用另一批未用材料复验。"
new = "任务要求先探索训练段再保留后段回放；这一次在冻结前已看过后段，因此本轮严格留出条件**未通过，本轮验证不通过**，须用另一批未用材料复验。"
assert old in text
text = text.replace(old, new)
old = "但后来的成功对任何‘重复失败后必须改权限/不会再成功’强规则构成反例。当前建议未作该断言；成功原因、操作时间和纯重试结果均未知。"
new = "但后来的成功反驳了‘重复失败后不会再成功’这一强断言。它既不能证实也不能反驳‘必须改权限’，因为动作时间和因果链未知。当前建议未作这些断言；成功原因与纯重试结果均未知。"
assert old in text
text = text.replace(old, new)
hypotheses = {
    "E02": "短时连接扰动、持续网络/上游异常、配置或环境差异",
    "E04": "断言/逻辑或输入差异、不稳定测试、执行环境差异",
    "E07": "有效身份或目标策略不匹配、网关拒绝、上游临时异常；403不能单独确定权限根因",
    "E10": "短时连接扰动、持续网络/上游异常、配置或环境差异",
    "E12": "目标空间、inode或配额受限，或实际目标挂载与预期不同",
    "E15": "测试/输入耗时、资源限制、外部依赖等待、预算与实际耗时不匹配",
    "E18": "请求/传输等待、上游响应慢、超时预算或网络环境差异",
    "E20": "源代码或生成文件问题、配置解析或执行环境差异；节选不足以定位",
    "E22": "有效身份或目标策略不匹配、网关拒绝、上游临时异常；相似历史不证明相同根因",
}
for event, candidates in hypotheses.items():
    start = text.index("### " + event + "\n")
    end = text.find("\n### ", start + 1)
    if end == -1:
        end = text.index("\n## 7.", start)
    card = text[start:end]
    candidate_lines = [line for line in card.splitlines() if line.startswith("| 候选解释 |")]
    assert len(candidate_lines) == 1
    changed = card.replace(candidate_lines[0], "| 候选解释 | " + candidates + "；均未获根因确认。 |")
    text = text[:start] + changed + text[end:]
text = text.replace("没有建设Agent、改代码/配置、联网、安装依赖", "没有建设Agent、修改原有代码/配置、联网、安装依赖")
text = text.replace("本次实际依次执行：`rtk proxy python 离线分析.py freeze`、`rtk proxy python 离线分析.py replay`。", "本次实际依次执行：`rtk proxy python 离线分析.py freeze`、`rtk proxy python 离线分析.py replay`、`rtk proxy python 复核.py`。复核仅修正报告的候选解释和两处因果/验收表述，不修改冻结规则或逐次建议；复核结果见复核结果.json。")
text = text.replace("为保护已有产物，脚本以新建模式写文件；", "为保护已有产物，主分析脚本对JSON以新建模式写文件；")
assert "本轮验证不通过" in text
(base / "答复.md").write_text(text, encoding="utf-8")
result = {
    "frozen_rules_unchanged": sha(base / "冻结规则.json") == audit["frozen_sha256"],
    "analysis_script_unchanged": sha(base / "离线分析.py") == frozen["implementation_sha256"],
    "source_files_unchanged": True, "independent_prefix_checks": len(decisions),
    "failed_event_count": len(events), "observed_recovered_events": sum(e["recovered"] for e in events),
    "strict_holdout_pass": False, "verdict": "本轮验证不通过；目标可行性尚未证实。",
    "report_only_corrections": ["明确已见留出导致严格条件不通过", "成功不反驳必须改权限这一未经证实的必要性断言", "处置卡填入候选解释而非区分问题"],
    "report_sha256": sha(base / "答复.md"),
}
with (base / "复核结果.json").open("x", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(json.dumps(result, ensure_ascii=False))
