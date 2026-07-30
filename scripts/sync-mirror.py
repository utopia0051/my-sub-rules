#!/usr/bin/env python3
"""
sync-mirror.py —— 按 rules/mirror/MANIFEST.txt 同步上游社区规则到本仓库镜像。

用法：在仓库根目录执行  python scripts/sync-mirror.py
（走系统代理：设置环境变量 HTTPS_PROXY=http://127.0.0.1:7890 后再执行）

行为：
- 逐条下载 MANIFEST 里的上游 URL
- 在文件头部写入上游地址、上游仓库、同步时间（供人和 agent 追溯）
- 下载失败/内容异常（过小）时保留旧文件并报错，绝不用坏数据覆盖好数据
- 结束时打印每个文件的规则行数变化
"""
import os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "rules", "mirror")
MANIFEST = os.path.join(MIRROR, "MANIFEST.txt")
MIN_BYTES = 50  # 下载结果小于此值视为异常

def rule_lines(text):
    return sum(1 for l in text.splitlines() if l.strip() and not l.strip().startswith(("#", ";", "//")))

KNOWN_TYPES = ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "DOMAIN-REGEX", "IP-CIDR", "IP-CIDR6",
               "PROCESS-NAME", "DST-PORT", "SRC-PORT", "GEOIP", "IP-ASN", "SRC-IP-CIDR")

def payload_to_classical(text):
    """自动把 rule-provider 的 payload YAML（如 Loyalsoldier/clash-rules）转成 classical 文本。
    已是 classical 的文件原样返回。"""
    sig = next((l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith("#")), "")
    if sig != "payload:":
        return text, False
    out = []
    for l in text.splitlines():
        s = l.strip()
        if s.startswith("#"):
            out.append(s)
            continue
        if not s.startswith("- "):
            continue
        v = s[2:].strip().strip("'\"")
        v = v.split(" #", 1)[0].split("\t#", 1)[0].strip()   # 去掉行内注释
        import re as _re2
        v = _re2.sub(r"\s*,\s*", ",", v)                      # 规范逗号两侧空格
        head = v.split(",", 1)[0]
        if head in KNOWN_TYPES:
            out.append(v)                                   # payload 里已是 classical 规则
        elif v.startswith("+.") or v.startswith("*."):
            out.append("DOMAIN-SUFFIX," + v[2:])            # 域名通配 → 后缀
        elif "/" in v and (":" in v or v.count(".") == 3):
            out.append(("IP-CIDR6," if ":" in v else "IP-CIDR,") + v + ",no-resolve")
        else:
            out.append("DOMAIN," + v)                       # 裸域名 → 精确匹配
    return "\n".join(out) + "\n", True

def normalize_classical(text):
    """规范化 classical 规则，修复上游常见毛病：
    - IP-CIDR6 裸 IPv6 地址补 /128、IP-CIDR 裸 IPv4 补 /32（mihomo 会拒绝无前缀写法）
    - IP 类规则（IP-CIDR/IP-CIDR6/IP-ASN/GEOIP）缺 no-resolve 时补齐：
      少了它 mihomo 会为匹配规则先做一次本地 DNS 解析，在规则模式下这次解析
      会落到国内 DNS 上 —— 属于 DNS 泄露。上游 payload 常漏写（例：Accademia
      的 Grok_No_Resolve.yaml 里 `IP-CIDR , 17.253.4.125` 就没带）。
      SRC-IP-CIDR 不在此列：源 IP 无需解析，加 no-resolve 无意义。
    对注释和其它规则类型原样保留。"""
    NO_RESOLVE_TYPES = ("IP-CIDR", "IP-CIDR6", "IP-ASN", "GEOIP")
    out = []
    for l in text.splitlines():
        st = l.strip()
        if not st or st.startswith(("#", ";", "//")):
            out.append(l.rstrip())
            continue
        parts = [p.strip() for p in st.split(",")]
        if parts[0] in ("IP-CIDR6", "IP-CIDR") and len(parts) >= 2 and "/" not in parts[1]:
            parts[1] += "/128" if parts[0] == "IP-CIDR6" else "/32"
        if parts[0] in NO_RESOLVE_TYPES and "no-resolve" not in parts[1:]:
            parts.append("no-resolve")
        out.append(",".join(parts))
    return "\n".join(out) + "\n"

def main():
    entries = []
    for line in open(MANIFEST, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, url = line.split("\t") if "\t" in line else line.split(None, 1)
        entries.append((name.strip(), url.strip()))
    print(f"manifest: {len(entries)} 个镜像目标\n")

    failed = []
    for name, url in entries:
        dst = os.path.join(MIRROR, name)
        old = open(dst, encoding="utf-8").read() if os.path.exists(dst) else ""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "sync-mirror/1.0"})
            body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
            if len(body) < MIN_BYTES:
                raise ValueError(f"内容过小({len(body)}B)，疑似异常响应")
        except Exception as e:
            print(f"  ✗ {name}: 下载失败，保留旧文件 —— {e}")
            failed.append(name)
            continue
        body, converted = payload_to_classical(body)
        body = normalize_classical(body)
        import re as _re
        m = _re.search(r"githubusercontent\.com/([^/]+/[^/]+)/", url)
        repo = m.group(1) if m else "unknown"
        header = (
            "# ===== MIRRORED RULE (auto-generated header) =====\n"
            f"# Upstream: {url}\n"
            f"# Upstream repo: {repo}\n"
            f"# Synced: {time.strftime('%Y-%m-%d %H:%M:%S %z')}\n"
            + ("# Converted: payload YAML -> classical (by sync-mirror)\n" if converted else "")
            + "# Update: python scripts/sync-mirror.py  (或让 Claude/agent 执行)\n"
            "# =================================================\n"
        )
        open(dst, "w", encoding="utf-8", newline="\n").write(header + body)
        print(f"  ✓ {name}: {rule_lines(old)} -> {rule_lines(body)} 条规则")

    print(f"\n完成：{len(entries)-len(failed)} 成功，{len(failed)} 失败")
    if failed:
        print("失败列表:", ", ".join(failed))
        sys.exit(1)

if __name__ == "__main__":
    main()
