# -*- coding: utf-8 -*-
"""snapshot_draft.py — 初稿快照（改判核算基线）·2026-09-12 建立
用法：
  python snapshot_draft.py <批键>          # 生成快照（幂等：已存在则跳过）
  python snapshot_draft.py <批键> --force  # 覆盖重拍
  python snapshot_draft.py --list          # 列出已有快照
  python snapshot_draft.py --latest        # 自动取 data.js 最后一个批键（发布脚本调用）
  python snapshot_draft.py <批键> --from <备份文件路径> --force   # 回填：从历史备份取首版内容
说明：
  快照在「首次发布」时由 deploy_publish.ps1 自动拍摄（＝首次发布版＝本项目的「初稿」口径）。
  之后任何改判都以此为基线，批末用 audit_revision_record.py 出「改判战绩 X 得 Y 失」。
存放：_backup/drafts/<批键>.draft.json
"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"D:\Cola\足球分析学习"
DATA = os.path.join(ROOT, "_发布_public", "js", "data.js")
DRAFTS = os.path.join(ROOT, "_backup", "drafts")


def batch_block(src, key):
    i = src.find('"%s": {' % key)
    if i < 0:
        return None
    m = re.search(r'\n  "\d{4}-\d{2}-\d{2}": \{', src[i + 10:])
    return src[i:i + 10 + m.start()] if m else src[i:i + 300000]


def extract(src, key):
    blk = batch_block(src, key)
    if not blk:
        return None
    title = re.search(r'title: "([^"]*)"', blk)
    ms = []
    for m in re.finditer(r'no: "(\d{3})"', blk):
        no = m.group(1)
        if any(x["no"] == no for x in ms):
            continue
        b = blk[m.start():m.start() + 1600]
        f = {}
        for k in ("home", "away", "league", "lg", "time", "dir", "dc", "scores", "ht", "ou"):
            mm = re.search(r'%s: "([^"]*)"' % k, b)
            if mm:
                f[k] = mm.group(1)
        rm = re.search(r'risk: (\d+)', b)
        if rm:
            f["risk"] = int(rm.group(1))
        if "dir" in f and "scores" in f and "ht" in f and "ou" in f:
            ms.append(dict(no=no, **f))
    warn = {}
    for arr in ("coldRisk", "alerts", "zeroZero", "bigSeven"):
        m = re.search(r'%s: \[(.*?)\](?:,\s*\n|\s*\n)' % arr, blk, re.S)
        if m:
            warn[arr] = re.findall(r'no: "(\d{3})"', m.group(1))
    return dict(key=key, title=title.group(1) if title else "", taken="", matches=ms, warn=warn)


def main():
    argv = sys.argv[1:]
    srcpath = None
    if "--from" in argv:                          # 回填：从备份文件取首版内容（历史批次）
        i = argv.index("--from")
        if i + 1 < len(argv):
            srcpath = argv[i + 1]
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    os.makedirs(DRAFTS, exist_ok=True)
    if "--list" in flags:
        fs = sorted(os.listdir(DRAFTS))
        print("已有快照 %d 个：" % len(fs))
        for f in fs:
            p = os.path.join(DRAFTS, f)
            d = json.load(io.open(p, encoding="utf-8"))
            print("   %s  %s  %d 场  %s" % (f, d.get("taken", "")[:34], len(d.get("matches", [])), d.get("title", "")[:40]))
        return
    src = io.open(srcpath or DATA, encoding="utf-8", errors="replace").read()
    if "--latest" in flags:                       # 发布脚本用：自动取 data.js 最后一个批键
        ks = re.findall(r'\n  "(\d{4}-\d{2}-\d{2})": \{', src)
        if not ks:
            print("❌ data.js 中未解析到批键")
            sys.exit(1)
        args = [ks[-1]]
    if not args:
        print(__doc__)
        sys.exit(1)
    key = args[0]
    d = extract(src, key)
    if not d:
        print("❌ 批键 %s 不在 %s 中" % (key, srcpath or "data.js"))
        sys.exit(1)
    p = os.path.join(DRAFTS, "%s.draft.json" % key)
    if os.path.exists(p) and "--force" not in flags:
        print("已存在快照（跳过）：%s" % p)
        return
    import datetime
    if srcpath:
        d["taken"] = datetime.datetime.fromtimestamp(os.path.getmtime(srcpath)).strftime("%Y-%m-%d %H:%M") + \
                     "（回填·%s）" % os.path.basename(srcpath)
    else:
        d["taken"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    io.open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    print("✅ 快照已写入 %s（%d 场·%s）" % (p, len(d["matches"]), d["title"]))


if __name__ == "__main__":
    main()
