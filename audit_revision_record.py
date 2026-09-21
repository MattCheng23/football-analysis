# -*- coding: utf-8 -*-
"""audit_revision_record.py — 改判战绩核销（批末自动出账）·2026-09-12 建立
用法：
  python audit_revision_record.py <批键>   # 单批核销（需已复盘场次 + 初稿快照）
  python audit_revision_record.py --all    # 所有有快照的批次
输出：逐场四维前后对比 + 改判战绩（得/失维、得/失场）+ 建议（净负则建议回滚初稿判定）
口径：初稿＝_backup/drafts/<批键>.draft.json（首次发布快照）／终稿＝现行 data.js／赛果＝**台账 v12db_full.json**
★ 2026-09-19 修（自身事故）：旧版赛果从 data-review.js 按 `"<批键>": {` 切块 → **越界**（实测 0918 段吞进
  后续多批场次，把别批的 014 当成 0918-014，虚报「已复盘 17 场」）。现改为：赛果一律取台账该日 act，
  并强制 **队名一致性** 校验（台账 teams 含票面主/客队名），不一致即拒判。
"""
import io, json, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"D:\Cola\足球分析学习"
DATA = os.path.join(ROOT, "_发布_public", "js", "data.js")
REV = os.path.join(ROOT, "_发布_public", "js", "data-review.js")
DRAFTS = os.path.join(ROOT, "_backup", "drafts")
FT = lambda a, b: "胜" if a > b else ("负" if a < b else "平")
RESn = lambda a, b: "主胜" if a > b else ("客胜" if a < b else "平")


def block(src, key):
    i = src.find('"%s": {' % key)
    if i < 0:
        return None
    m = re.search(r'\n  "\d{4}-\d{2}-\d{2}": \{', src[i + 10:])
    return src[i:i + 10 + m.start()] if m else src[i:i + 300000]


def preds(src, key):
    blk = block(src, key)
    if not blk:
        return {}
    out = {}
    for m in re.finditer(r'no: "(\d{3})"', blk):
        no = m.group(1)
        if no in out:
            continue
        b = blk[m.start():m.start() + 1600]
        d = re.search(r'dir: "([^"]*)"', b); sc = re.search(r'scores: "([^"]*)"', b)
        ht = re.search(r'ht: "([^"]*)"', b); ou = re.search(r'ou: "([^"]*)"', b)
        hm = re.search(r'home: "([^"]*)"', b); am = re.search(r'away: "([^"]*)"', b)
        if d and sc and ht and ou:
            out[no] = dict(dir=d.group(1), sc=sc.group(1), ht=ht.group(1), ou=ou.group(1),
                           home=hm.group(1) if hm else "", away=am.group(1) if am else "")
    return out


LEDGER = os.path.join(ROOT, "05_模型代码", "v12db_full.json")


def load_ledger():
    try:
        return json.load(io.open(LEDGER, encoding="utf-8"))
    except Exception:
        return []


def acts(key):
    """赛果真源＝台账（该日 act 括号值）。★ 不再从 data-review.js 切块（按批键切块会越界吞别批场次）。
    ★ act 分隔符两种都收：全量 658 行用 `A-B（C-D）`，**0914 整批 11 行用半角冒号 `A:B（C:D）`**
      （2026-09-19 实测）——只认 `-` 的解析器会把 0914 批静默丢光。
      另 5 行是裸比分（无半场括号）⇒ 半场维度不判。
    """
    out = {}
    for r in load_ledger():
        if str(r.get("date"))[:10] != key:
            continue
        m = re.match(r"(\d+)[-:](\d+)（(\d+)[-:](\d+)）", str(r.get("act") or ""))
        if m:
            out[r["no"]] = dict(teams=r.get("teams", ""), ft=m.group(1) + "-" + m.group(2),
                                ht=m.group(3) + "-" + m.group(4))
        else:
            m2 = re.match(r"(\d+)[-:](\d+)$", str(r.get("act") or ""))
            if m2:
                out[r["no"]] = dict(teams=r.get("teams", ""), ft=m2.group(1) + "-" + m2.group(2), ht=None)
    return out


def judge(p, a):
    if not a.get("ht"):
        return [None] * 4          # 台账缺半场 ⇒ 不判（两侧同值，不影响前后对比）
    fa, fb = map(int, a["ft"].split("-")); ha, hb = map(int, a["ht"].split("-"))
    d = RESn(fa, fb) in p["dir"].split("（")[0]
    sc = a["ft"] in [x.strip().replace("*", "") for x in p["sc"].split("/")]
    ht = (FT(ha, hb) + FT(fa, fb)) in [x.strip().replace("*", "") for x in p["ht"].split("/")]
    nums = []
    for rng in p["ou"].replace("总进球", "").split("+"):
        mm = re.search(r"(\d+)[·.](\d+)", rng.strip())
        if mm:
            nums += [int(mm.group(1)), int(mm.group(2))]
    return [d, sc, ht, (fa + fb) in nums]


def audit(key, cur, rev):
    p = os.path.join(DRAFTS, "%s.draft.json" % key)
    if not os.path.exists(p):
        print("批 %s：无初稿快照（%s）→ 无法核销（下次发布起自动拍摄）" % (key, p))
        return None
    draft = json.load(io.open(p, encoding="utf-8"))
    D = {}
    for m in draft["matches"]:
        m.setdefault("sc", m.get("scores", ""))   # 快照字段名兼容（scores → sc）
        D[m["no"]] = m
    F = preds(cur, key)
    A = acts(key)
    if not A:
        print("批 %s：台账无该日赛果 → 待赛后核销" % key)
        return None
    rows, gf = [], 0
    ch = gain_m = loss_m = 0
    g_dims = l_dims = 0
    new_matches = 0
    mismatch = []
    for no in sorted(A):
        if no not in F:
            continue
        if no not in D:
            new_matches += 1
            continue
        # ★ 队名一致性闸门（防「同编号不同批」错配）
        f = F[no]
        if f.get("home") and f["home"] not in A[no]["teams"]:
            mismatch.append(no); continue
        if f.get("away") and f["away"] not in A[no]["teams"]:
            mismatch.append(no); continue
        a = judge(D[no], A[no]); b = judge(F[no], A[no])
        if a == b:
            continue
        ch += 1
        d = sum(b) - sum(a)
        if d > 0:
            gain_m += 1; g_dims += d
        elif d < 0:
            loss_m += 1; l_dims += -d
        rows.append((no, A[no]["teams"], A[no]["ft"], a, b, d))
    print("== 批 %s 改判核销（初稿快照 %s · %d 场）==" % (key, draft.get("taken", "?")[:16], len(D)))
    print("   已复盘 %d 场｜改判 %d 场（得 %d / 失 %d）｜得维 +%d / 失维 -%d ＝ 净 %+d 维｜初稿未含的新增场次 %d" % (
        len(A) - len(mismatch), ch, gain_m, loss_m, g_dims, l_dims, g_dims - l_dims, new_matches))
    if mismatch:
        print("   ⚠ 队名不一致已跳过 %d 场（疑似同编号错配）：%s" % (len(mismatch), " ".join(mismatch)))
    for no, teams, ft, a, b, d in rows:
        print("   %s %-22s 实际 %-8s 初稿 %s → 终稿 %s（%+d）" % (
            no, teams, ft, "".join("✅" if x else "❌" for x in a), "".join("✅" if x else "❌" for x in b), d))
    if ch and g_dims - l_dims < 0:
        print("   ⚠ 建议：本批改判净负（%+d 维）→ 按流程「档 B 负收益回滚」，除有条款/事实依据者外应回滚初稿判定" % (g_dims - l_dims))
    elif ch:
        print("   ✅ 本批改判净 %+d 维（零期望附近属正常，注意登记依据）" % (g_dims - l_dims))
    return dict(key=key, ch=ch, gain=gain_m, loss=loss_m, gd=g_dims, ld=l_dims)


if __name__ == "__main__":
    cur = io.open(DATA, encoding="utf-8").read()
    if "--all" in sys.argv:
        fs = sorted(f for f in os.listdir(DRAFTS) if f.endswith(".draft.json")) if os.path.isdir(DRAFTS) else []
        for f in fs:
            audit(f.replace(".draft.json", ""), cur, None)
            print()
    elif len(sys.argv) > 1:
        audit(sys.argv[1], cur, None)
    else:
        print(__doc__)
