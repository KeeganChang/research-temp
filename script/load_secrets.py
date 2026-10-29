#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
load_secrets.py — 安全读取密钥（secrets/ 与 .env），供脚本运行态注入。

设计原则（AGENTS.md 铁律 1：绝不硬编码绝对路径与私密信息）
  - 路径一律相对 workspace 根推导，不在代码里写死盘符/绝对路径；
  - 密钥只从 secrets/<service>.env 与根 .env 读取，文档与代码只写"放哪"不写值；
  - secrets/ 与 .env 均被 .gitignore 排除，绝不入库。

查找顺序（get_secret）
  1. 环境变量（已注入时直接用）
  2. secrets/<service>.env（service 指定时）
  3. 根 .env
  4. secrets/ 下所有 *.env（按文件名排序，最后兜底扫描）

用法
  # 作为模块
  from load_secrets import get_secret, load_env
  token = get_secret("FEISHU_APP_TOKEN")
  feishu = load_env("feishu")            # 返回 dict，读 secrets/feishu.env

  # 作为 CLI（调试用，注意别把输出贴进日志）
  python -m script.load_secrets --list           # 列出已配置的 key 名（不打印值）
  python -m script.load_secrets --get FEISHU_APP_TOKEN

退出码：0 成功；2 未找到 workspace 根；3 指定 key 不存在。
"""
import os
import sys
import glob

# --- 定位 workspace 根：向上查找 AGENTS.md（项目标志文件），不硬编码路径 ---
def find_workspace_root(start=None):
    """从 start（默认本文件所在目录）向上查找含 AGENTS.md 的目录。"""
    cur = os.path.abspath(start or os.path.dirname(os.path.abspath(__file__)))
    for _ in range(10):
        if os.path.isfile(os.path.join(cur, "AGENTS.md")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None


ROOT = os.environ.get("WORKSPACE_ROOT") or find_workspace_root()
if ROOT is None:
    sys.stderr.write("未找到 workspace 根（向上 10 级未发现 AGENTS.md）；"
                     "可设置环境变量 WORKSPACE_ROOT 指定。\n")
    sys.exit(2)

SECRETS_DIR = os.path.join(ROOT, "secrets")
DOTENV = os.path.join(ROOT, ".env")


def _parse_env_file(path):
    """解析 KEY=VALUE 文件，忽略注释与空行；支持去除配对引号；不做变量展开（保持简单可预测）。"""
    data = {}
    if not os.path.isfile(path):
        return data
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
                v = v[1:-1]
            data[k] = v
    return data


def load_env(service=None):
    """读取指定服务的 secrets/<service>.env；service 为空则读根 .env。返回 dict。"""
    path = os.path.join(SECRETS_DIR, f"{service}.env") if service else DOTENV
    return _parse_env_file(path)


def get_secret(name, service=None, default=None):
    """按优先级取一个密钥值：环境变量 → secrets/<service>.env → .env → secrets/*.env 兜底。"""
    if name in os.environ:
        return os.environ[name]
    if service:
        v = load_env(service).get(name)
        if v is not None:
            return v
    v = load_env().get(name)
    if v is not None:
        return v
    for p in sorted(glob.glob(os.path.join(SECRETS_DIR, "*.env"))):
        v = _parse_env_file(p).get(name)
        if v is not None:
            return v
    return default


def list_keys(service=None):
    """列出已配置的 key 名（不打印值，避免泄露）。"""
    keys = set()
    if service:
        keys |= set(load_env(service))
    keys |= set(load_env())
    for p in sorted(glob.glob(os.path.join(SECRETS_DIR, "*.env"))):
        keys |= set(_parse_env_file(p))
    return sorted(keys)


def main():
    args = sys.argv[1:]
    if "--list" in args:
        for k in list_keys():
            print(k)
        return 0
    if "--get" in args:
        i = args.index("--get")
        if i + 1 >= len(args):
            sys.stderr.write("--get 需要指定 key 名\n")
            return 3
        name = args[i + 1]
        val = get_secret(name)
        if val is None:
            sys.stderr.write(f"未找到密钥: {name}\n")
            return 3
        print(val)
        return 0
    sys.stderr.write(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
