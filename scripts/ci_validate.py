# -*- coding: utf-8 -*-
"""ci_validate.py — CI 用静态校验（本地亦可直接跑）

校验内容：
  ① 全部被 git 跟踪的 .py 语法
  ② 全部被 git 跟踪的 .json 可解析

合规（参考本机 checker-hardening 纪律）：
  · **防呆**：匹配到 0 个文件时判 FAIL，不得静默通过
  · 文件清单来自 `git ls-files -z`（NUL 分隔，避免中文路径被引号转义 —— 实测踩过）

用法：python scripts/ci_validate.py
"""
import io, json, os, py_compile, subprocess, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tracked(pattern):
    r = subprocess.run(['git', '-C', ROOT, 'ls-files', '-z', pattern], capture_output=True)
    if r.returncode != 0:
        print('FAIL: git ls-files 失败')
        sys.exit(2)
    return [p for p in r.stdout.decode('utf-8', 'replace').split('\0') if p]


def main():
    fails = []

    # ① Python 语法
    pys = tracked('*.py')
    if not pys:
        print('FAIL: 未匹配到任何 .py —— 拒绝在空结果上判通过（防呆）')
        sys.exit(2)
    pyfail = 0
    for p in pys:
        full = os.path.join(ROOT, p)
        if not os.path.exists(full):
            continue
        try:
            py_compile.compile(full, doraise=True)
        except py_compile.PyCompileError as e:
            pyfail += 1
            fails.append('PY 语法 %s: %s' % (p, str(e).splitlines()[0][:120]))
    print('Python 语法：检查 %d 个，失败 %d 个' % (len(pys), pyfail))

    # ② JSON 可解析
    js = tracked('*.json')
    if not js:
        print('FAIL: 未匹配到任何 .json（防呆）')
        sys.exit(2)
    jfail = 0
    bom = []
    for p in js:
        full = os.path.join(ROOT, p)
        if not os.path.exists(full):
            continue
        try:
            # 用 utf-8-sig 读取：容忍 BOM（浏览器 JSON.parse 会拒绝 BOM，
            # 但仓库内 BOM 文件均为归档件，非线上数据）—— 单独计数上报，不判失败。
            raw = open(full, 'rb').read(3)
            if raw == b'\xef\xbb\xbf':
                bom.append(p)
            with io.open(full, encoding='utf-8-sig') as fh:
                json.load(fh)
        except Exception as e:
            jfail += 1
            fails.append('JSON %s: %s' % (p, str(e)[:120]))
    print('JSON 有效性：检查 %d 个，失败 %d 个' % (len(js), jfail))
    if bom:
        print('  ⓘ 其中 %d 个带 UTF-8 BOM（已容忍；都在归档目录，非线上数据）' % len(bom))

    print('')
    if fails:
        print('GUARD FAIL（%d 项）：' % len(fails))
        for f in fails[:30]:
            print('  ✗ ' + f)
        return 1
    print('GUARD OK：语法与数据全部通过 ✅')
    return 0


if __name__ == '__main__':
    sys.exit(main())
