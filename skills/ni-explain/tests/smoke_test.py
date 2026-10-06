"""离线自检：check.py 对带病样例报出预期规则；对「存疑类」样例不报确定命中。"""
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
CHECK = SKILL_DIR / "scripts" / "check.py"


def run(sample):
    return subprocess.run(
        [sys.executable, str(CHECK), "--lang", "zh", "-"],
        input=sample, capture_output=True, text=True, timeout=60,
    )


def test_dirty_sample_hits_expected_rules():
    out = run("我们对日志进行了压缩处理,性能有显著提升。\n")
    for rule in ("3.1", "1.5", "1.4", "8.1"):
        assert rule in out.stdout, f"missing rule {rule} in:\n{out.stdout}"
    assert out.returncode == 1, "带确定命中的样例应返回 1"


def test_clean_sample_passes():
    out = run("任务在 5 秒后重试。\n")
    assert "确定" not in out.stdout, f"干净样例不应有确定命中:\n{out.stdout}"
    assert out.returncode == 0


def test_context_rules_are_maybe_not_sure():
    # 「建议/操作/支持/调整」是上下文规则，只报存疑，不算确定 —— 这是打磨掉的误报
    out = run("建议把这块操作交给支持团队调整。\n")
    assert "存疑" in out.stdout, out.stdout
    assert "确定" not in out.stdout, f"不该报确定:\n{out.stdout}"
    assert out.returncode == 0, "只有存疑时退出码应为 0"


def test_ai_tells_flagged():
    # AI 腔（9.7）应被检出，且不被「定义行」降噪误杀
    out = run("综上所述，值得注意的一点是，基于此我们从而改进了流程。\n")
    assert "9.7" in out.stdout, f"AI 腔未检出:\n{out.stdout}"


def test_banned_word_list_is_skipped():
    # 禁用词清单是「提及」不是「使用」，应被降噪跳过
    out = run("不用含糊词：适当、有关的、较为、显著、大幅。\n")
    assert "1.4" not in out.stdout, f"定义行不该报违规:\n{out.stdout}"


if __name__ == "__main__":
    test_dirty_sample_hits_expected_rules()
    test_clean_sample_passes()
    test_context_rules_are_maybe_not_sure()
    test_ai_tells_flagged()
    test_banned_word_list_is_skipped()
    print("smoke ok")
