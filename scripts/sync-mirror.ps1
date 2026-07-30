# sync-mirror.ps1 —— Windows 一键同步上游社区规则到本仓库镜像
# 用法：在仓库根目录右键"使用 PowerShell 运行"，或：
#   powershell -ExecutionPolicy Bypass -File scripts\sync-mirror.ps1
# 需要走代理时先执行：$env:HTTPS_PROXY = "http://127.0.0.1:7890"

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Mirror = Join-Path $Root "rules\mirror"
$Manifest = Join-Path $Mirror "MANIFEST.txt"
$MinBytes = 50

$ok = 0; $fail = @()
Get-Content $Manifest -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }
    $parts = $line -split "`t| +", 2
    $name = $parts[0].Trim(); $url = $parts[1].Trim()
    $dst = Join-Path $Mirror $name
    try {
        $body = (Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 60).Content
        if ($body.Length -lt $MinBytes) { throw "内容过小($($body.Length)B)" }
        # payload YAML -> classical 自动转换（如 Loyalsoldier/clash-rules）
        $converted = $false
        $sig = ($body -split "`n" | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith('#') } | Select-Object -First 1).Trim()
        if ($sig -eq 'payload:') {
            $known = @('DOMAIN','DOMAIN-SUFFIX','DOMAIN-KEYWORD','DOMAIN-REGEX','IP-CIDR','IP-CIDR6','PROCESS-NAME','DST-PORT','SRC-PORT','GEOIP','IP-ASN','SRC-IP-CIDR')
            $out = foreach ($l in ($body -split "`n")) {
                $s = $l.Trim()
                if ($s.StartsWith('#')) { $s; continue }
                if (-not $s.StartsWith('- ')) { continue }
                $v = $s.Substring(2).Trim().Trim("'").Trim('"')
                $v = ($v -split ' #', 2)[0].Trim()
                $v = $v -replace '\s*,\s*', ','
                $head = ($v -split ',', 2)[0]
                if ($known -contains $head) { $v }
                elseif ($v.StartsWith('+.') -or $v.StartsWith('*.')) { "DOMAIN-SUFFIX," + $v.Substring(2) }
                elseif ($v.Contains('/') -and ($v.Contains(':') -or ([regex]::Matches($v, '\.')).Count -eq 3)) {
                    $(if ($v.Contains(':')) { "IP-CIDR6,$v,no-resolve" } else { "IP-CIDR,$v,no-resolve" })
                }
                else { "DOMAIN,$v" }
            }
            $body = ($out -join "`n") + "`n"
            $converted = $true
        }
        # 规范化：裸 IP-CIDR/IP-CIDR6 补前缀（mihomo 拒绝无前缀），IP 类规则补
        # no-resolve（缺了会触发本地 DNS 解析 = 规则模式下泄露，上游 payload 常漏写）。
        # SRC-IP-CIDR 不在此列：源 IP 无需解析。逻辑与 sync-mirror.py 保持一致。
        $noResolve = @('IP-CIDR','IP-CIDR6','IP-ASN','GEOIP')
        $norm = foreach ($l in ($body -split "`n")) {
            $st = $l.Trim()
            if (-not $st -or $st -match '^(#|;|//)') { $l.TrimEnd(); continue }
            $p = @(($st -split ',').Trim())
            if ($p[0] -in 'IP-CIDR','IP-CIDR6' -and $p.Count -ge 2 -and $p[1] -notmatch '/') {
                $p[1] += if ($p[0] -eq 'IP-CIDR6') { '/128' } else { '/32' }
            }
            if ($p[0] -in $noResolve -and $p -notcontains 'no-resolve') { $p += 'no-resolve' }
            $p -join ','
        }
        # py 的 splitlines() 丢弃尾部空元素，-join 不会 —— TrimEnd 对齐两者产出
        $body = ($norm -join "`n").TrimEnd("`n") + "`n"
        $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz"
        $repo = if ($url -match 'githubusercontent\.com/([^/]+/[^/]+)/') { $Matches[1] } else { 'unknown' }
        $conv = if ($converted) { "# Converted: payload YAML -> classical (by sync-mirror)`n" } else { "" }
        $header = "# ===== MIRRORED RULE (auto-generated header) =====`n# Upstream: $url`n# Upstream repo: $repo`n# Synced: $stamp`n$conv# Update: python scripts/sync-mirror.py  (或让 Claude/agent 执行)`n# =================================================`n"
        [System.IO.File]::WriteAllText($dst, $header + $body, (New-Object System.Text.UTF8Encoding($false)))
        $lines = ($body -split "`n" | Where-Object { $_.Trim() -and -not $_.Trim().StartsWith("#") }).Count
        Write-Host "  OK  $name  ($lines 条规则)"
        $script:ok++
    } catch {
        Write-Host "  FAIL $name  保留旧文件 —— $_" -ForegroundColor Red
        $script:fail += $name
    }
}
Write-Host "`n完成：$ok 成功，$($fail.Count) 失败"
if ($fail.Count -gt 0) { Write-Host ("失败列表: " + ($fail -join ", ")) -ForegroundColor Red; exit 1 }
