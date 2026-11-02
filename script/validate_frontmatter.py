#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_frontmatter.py — 校验 research note 的 YAML frontmatter。

规则（见 docs/ARCHITECTURE.md §3 与 skills/file-manager/references/naming-and-frontmatter.md）：每条 research note 必须带以下字段
  source      (str)   数据来源描述，如 "NeoData / 公司公告 / 网页URL"
  url         (str)   必须以 http:// 或 https:// 开头
  fetched_at  (str)   抓取日期 YYYY-MM-DD
  type        (enum)  structured | unstructured
  confidence  (enum)  high | medium | low

file-manager 在 md 落盘时会调用本脚本做校验；缺字段/格式错则告警。

用法：
  python -m script.validate_frontmatter <file.md> [<file2.md> ...]
  python -m script.validate_frontmatter archive/raw          # 递归目录
退出码：0 = 全部通过，1 = 存在错误
"""
import sys
import os
import re
import datetime

try:
    import yaml
except ImportError:
    sys.stderr.write("缺少依赖 pyyaml，请先安装：pip install pyyaml\n")
    sys.exit(2)

REQUIRED = {
    "source": str,
    "url": str,
    "fetched_at": str,
    "type": str,
    "structure": str,
    "confidence": str,
}
ENUMS = {
    "type": {"资讯", "行业", "公司", "热点", "宏观", "个人配置"},
    "structure": {"structured", "unstructured"},
    "confidence": {"high", "medium", "low"},
}
URL_RE = re.compile(r"^https?://", re.I)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PROJECT_RE = re.compile(r"^P\d{2}$")


def parse_frontmatter(text: str):
    """返回 dict；无/不规范返回 None。"""
    if not text.lstrip().startswith("---"):
        return None
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return "PARSE_ERROR"
    return data


def _date_to_str(v):
    """YAML 会把 2026-09-19 自动解析成 datetime.date，这里两种都接受。"""
    if isinstance(v, datetime.date):
        return v.isoformat()
    if isinstance(v, str):
        return v
    return None


def validate(fm):
    if fm is None:
        return ["缺 frontmatter（文件未以 --- 开头或不规范）"]
    if fm == "PARSE_ERROR":
        return ["frontmatter 不是合法 YAML"]
    if not isinstance(fm, dict):
        return ["frontmatter 顶层必须是映射（key: value）"]

    errors = []
    for k, t in REQUIRED.items():
        if k not in fm:
            errors.append(f"缺必填字段: {k}")
        elif k == "fetched_at":  # date 对象或字符串都接受
            if _date_to_str(fm[k]) is None:
                errors.append(f"字段类型错误: {k} 应为 日期/字符串")
        elif not isinstance(fm[k], t):
            errors.append(f"字段类型错误: {k} 应为 {t.__name__}，实际 {type(fm[k]).__name__}")

    if isinstance(fm.get("url"), str) and not URL_RE.match(fm["url"]):
        errors.append("url 必须以 http:// 或 https:// 开头")

    fa = _date_to_str(fm.get("fetched_at"))
    if fa is None:
        errors.append("fetched_at 必须是日期(YYYY-MM-DD)")
    elif not DATE_RE.match(fa):
        errors.append("fetched_at 格式应为 YYYY-MM-DD")
    else:
        try:
            datetime.date.fromisoformat(fa)
        except ValueError:
            errors.append("fetched_at 不是真实日期")

    # type / confidence：枚举比较统一转 str（防御 YAML 误解析）
    for k, allowed in ENUMS.items():
        if k in fm and str(fm[k]) not in allowed:
            errors.append(f"{k} 取值应为 {sorted(allowed)}，实际: {fm[k]!r}")

    # project：可选，写了就必须是 research/ 下存在的 P<两位数字>
    if "project" in fm and not PROJECT_RE.match(str(fm.get("project"))):
        errors.append(f"project 取值应为 P<两位数字>（如 P01），实际: {fm.get('project')!r}")

    # 一致性提示（非阻断）：structured 建议附带数据文件
    if str(fm.get("type")) == "structured" and not any(
        f in fm for f in ("data_file", "data_path")
    ):
        errors.append("提示: type=structured 建议带 data_file/data_path 指向 csv/json/sqlite")

    return errors


def collect_md(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, fs in os.walk(p):
                for f in fs:
                    if f.endswith(".md"):
                        files.append(os.path.join(root, f))
        elif p.endswith(".md"):
            files.append(p)
    return files


def main():
    args = sys.argv[1:] or ["archive/raw"]
    files = collect_md(args)
    if not files:
        print("无 .md 文件可校验")
        return 0
    total = 0
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as fh:
                text = fh.read()
        except OSError as e:
            print(f"[ERR ] {fp}: {e}")
            total += 1
            continue
        errs = validate(parse_frontmatter(text))
        if errs:
            total += len(errs)
            print(f"[FAIL] {fp}")
            for e in errs:
                print(f"   - {e}")
        else:
            print(f"[ OK ] {fp}")
    print(f"\n共校验 {len(files)} 个文件，{total} 个错误")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
