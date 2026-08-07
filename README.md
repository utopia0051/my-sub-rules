# my-sub-rules —— 订阅转换分流规则（机场/自建双组 · 防泄露版）

subconverter 远程配置 ×2 + Clash/mihomo 基础模板。相比旧版 [utopia0051/sub-rules](https://github.com/utopia0051/sub-rules) 的核心改进：

1. **规则新鲜且完全自主可控**：旧版把 90+ 个规则快照拷进仓库后三年不更新，分流烂掉——根因是"有副本、无更新机制"。新版采用**带同步机制的镜像**：社区规则（上游 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)）收在本仓库 `rules/mirror/` 下，每个文件头部记录上游地址和同步时间，`MANIFEST.txt` 是完整来源清单，跑一次 `scripts/sync-mirror.py`（或让 Claude/agent 执行）即可全部刷新。上游删库不受影响，规则也不会再冻死。
2. **防 DNS 泄露**：旧版没有指定 `clash_rule_base`，DNS 吃后端默认模板。新版自带 `base/clash_base.yml`：fake-ip 模式 + 全程加密 DoH + 节点域名专用解析。
3. **防 WebRTC/UDP 泄露**：`🔒 隐私防护` 分组拦截 STUN（域名+端口双重匹配），配合 TUN 模式，WebRTC 检测不再暴露真实 IP。
4. **保留你的节点分组习惯**：`✈️ 机场订阅` 与 `🚀 遵纪守法小组`（自建）沿用旧配置的同一套正则，去掉了多余的 `Proxies` 混合组；旧配置里的 50+ 条个人规则（YY 屏蔽包、PT 站直连、NTP/ddns 直连、暴雪代理等）已全部迁移到 `rules/` 下。

## 仓库结构

```
config/sub-rules.ini      Clash 完整版：机场/自建双组 + AI/流媒体/Telegram/广告/隐私分组
config/basic.ini          Clash 精简版：单组直出（对标旧 Basic/basic.ini），同样防泄露
config/shadowrocket.ini   Shadowrocket 专用（iOS）：同分组、STUN 端口内联、DoH 防泄露
config/sub-rules-adblock.ini        【可选/备用】硬核去广告版：= sub-rules.ini + Cats-Team AdRules
config/openclash.ini      软路由精简版：geosite/geoip 替代大表、手动选节点、防泄露完整
config/openclash-jichang.ini  软路由精简版·仅机场订阅：规则同 openclash.ini，只留一个机场节点组
base/clash_base.yml       Clash/mihomo 基础模板（DNS 防泄露、sniffer、TUN 参数）
base/shadowrocket.conf    Shadowrocket 基础模板（Surge 格式，DoH + 关 IPv6）
rules/claude-code.list    Claude/Claude Code 完整域名（API/CDN/认证/遥测/IP 段）
rules/chatgpt.list        OpenAI/ChatGPT 完整域名（含 sora/chat.com 等新域名）
rules/ai-misc.list        其他 AI 服务（Perplexity 等，后续新 AI 域名加这里）
rules/mirror/AI-VPSDance.list  AI 分流聚合（VPSDance，82 个 provider：Cursor/Devin/Midjourney 等）
rules/leak-test.list      IP/泄露检测站强制走代理（测试时看统一节点 IP）
rules/acg.list            二次元/漫画（Pixiv/Niconico/Bangumi/EH/拷贝漫画等）
rules/finance-proxy.list  港美股券商(富途/华盛)+加密交易所(币安/Gate)走代理
rules/finance-direct.list 境外银行(汇丰/众安)走直连
rules/emby.list           Emby 影音服务走代理（含自建 nijigem.by）
rules/docker.list         Docker 走代理（拉镜像更稳）
rules/apple-proxy.list    Apple 分区敏感服务（App Store/Apple ID/iCloud）走 🍎 Apple 组（美区 ID）
rules/custom-direct.list  个人直连（已迁移：PT 站、NTP、ddns、路由器、Steam CDN；含抖音 13 条）
rules/douyin-live.list    抖音客户端/直播直连（58 条字节系 CDN，修直播卡顿；仅 6 份主配置引用）
rules/custom-proxy.list   个人强制代理（已迁移：dpdns、暴雪、scholar）
rules/custom-reject.list  个人屏蔽（已迁移：YY 广告全家桶）
rules/stun.list           WebRTC/STUN 防泄露规则（Clash 版用）
rules/mirror/             社区规则镜像（上游 blackmatrix7，MANIFEST.txt 记录来源）
scripts/sync-mirror.py    镜像同步脚本（跨平台；让 Claude/agent 跑它即可更新规则）
scripts/sync-mirror.ps1   镜像同步脚本（Windows 一键版）
```

> ⚠️ **首次使用前必须先填充镜像**：仓库上传后立刻跑一次同步脚本（`python scripts/sync-mirror.py`，走代理时先设 `HTTPS_PROXY`），把 MANIFEST.txt 里登记的社区规则全部下载进 `rules/mirror/` 并提交推送——否则 ini 里的镜像链接是 404，转换会缺规则。以后想更新，对 Claude 说一句"按 MANIFEST 更新规则镜像"即可。

说明：6 个走代理的服务分组默认跟随「🔀机场or单个切换」总开关——在客户端切换这一处即可全局切换 机场↔自建；这个组末尾已展开全部节点，想固定某个单节点直接在里面选即可，服务组也能各自单独指定。已去掉自动测速组，节点保持订阅原始顺序（客户端若按延迟排序请关掉）。

三份配置共用同一套节点分组（机场/自建）和规则源，按客户端选一份即可：Clash 内核（桌面 Clash Verge / mihomo party / 软路由 OpenClash 通用）用 `sub-rules.ini`，想要极简用 `basic.ini`，iOS 上的 Shadowrocket 用 `shadowrocket.ini`。

## 节点分组机制

沿用你旧配置的正则，按**节点名关键字**区分来源：

- `✈️ 机场订阅`：节点名含 `机场订阅 / IEPL / 实验性 / 高级 / 标准` 任一关键字
- `🚀 遵纪守法小组`：其余所有节点（即自建节点）

> ⚠️ 换机场后如果节点命名风格变了，要同步修改 `config/sub-rules.ini` 里**两行**分组正则的关键字（正选和反选各一行）。
> ⚠️ 转换时只挂机场订阅、没有自建节点（或反过来）会产生空组，部分客户端会报错——两类节点至少各有一个时才用完整版，否则用精简版。

## 使用方法

在 sub-web-modify 前端（或任意 subconverter 前端）里：

- **订阅链接**：机场订阅和自建节点链接都填上（多条用 `|` 分隔）
- **远程配置**：
  完整版 `https://raw.githubusercontent.com/utopia0051/my-sub-rules/main/config/sub-rules.ini`
  精简版 `https://raw.githubusercontent.com/utopia0051/my-sub-rules/main/config/basic.ini`
- **目标类型**：Clash（mihomo / Clash Verge Rev / mihomo party 通用）
- 建议追加参数：`udp=true`（WebRTC 走代理和 Telegram 语音需要 UDP）

```
https://你的后端/sub?target=clash&udp=true&url=<URL编码的订阅>&config=<URL编码的远程配置>
```

raw 访问不稳可用 jsDelivr 加速：`https://cdn.jsdelivr.net/gh/utopia0051/my-sub-rules@main/config/sub-rules.ini`

> **后端必须支持新协议（重要）**：老版 subconverter（含 tindy2013 官方 v0.9.0 和大量公共后端）遇到 Hysteria2 / VLESS-REALITY 链接会直接返回 400，**整份订阅转换失败**（实测验证）。自建节点里有这两类协议的话，务必用内置 mihomo 解析内核、2026 年仍活跃维护的 [SubConverter-Extended](https://github.com/Aethersailor/SubConverter-Extended)（完全兼容本仓库的 ini 模板）：
> `docker run -d --restart=always --name subconverter -p 25500:25500 aethersailor/subconverter-extended:latest`
> 公共后端能看到你的订阅链接和自建节点信息，有记录风险：临时可用该项目演示站 `https://api.asailor.org`，长期强烈建议自建。

## 完整版分组一览

| 分组 | 默认 | 说明 |
|---|---|---|
| 🔀机场or单个切换 | 机场订阅 | **一键总开关**：切它=全局切换 机场↔自建；也可直接下拉选单个节点（末尾已展开全部节点）；下方服务组默认跟随 |
| ✈️ 机场订阅 | — | 机场节点池（按名字关键字筛选） |
| 🚀 遵纪守法小组 | — | 自建节点池（关键字取反） |
| 🌍 国外网站 | 🔀机场or单个切换 | 国外通用流量总开关（原 Proxies 的切换职责，但不再混入散节点） |
| 🤖 AI 服务 | 🔀机场or单个切换 | OpenAI/Claude/Gemini/Copilot；建议手动固定落地干净的那组 |
| 🍎 Apple | 🔀机场or单个切换 | App Store/Apple ID/iCloud/媒体商店——**美区 ID 手动选美国节点**；push/时间/系统更新仍直连 |
| 📺 流媒体 | 🔀机场or单个切换 | YouTube/Netflix/Disney+/HBO/巴哈姆特等合集 |
| 📲 Telegram | 🔀机场or单个切换 | 含 IP 段与进程规则 |
| 🔒 隐私防护 | REJECT | STUN/WebRTC 拦截，见防泄露说明 |
| 🛑 广告拦截 | REJECT | AdvertisingLite + 你的 YY 屏蔽包 |
| 🎯 全球直连 | DIRECT | 局域网/个人直连/国内域名/国内 IP |
| 🐟 漏网之鱼 | 🔀机场or单个切换 | 未匹配流量兜底 |
| GLOBAL | 🔀机场or单个切换 | 仅 Clash「全局模式」用；**已显式列出全部 12 个分组**（安卓 CMFA 的分组列表可见性依赖这个）+ 全部节点，可直接选任意单节点（规则模式不参与分流） |

> **关于 Clash「全局模式」**：全局模式是客户端左上角的模式切换（规则/全局/直连）。配置里已**显式定义 GLOBAL 组，成员为「全部 12 个分组 + 全部节点 + DIRECT」**，所以切到全局模式时能直接选任意单节点。但要注意：全局模式会让所有流量走 GLOBAL、**绕过这里全部分流与防泄露规则**，不建议日常用；且此时**不要选中 `🛑 广告拦截`**（该组只有 REJECT/DIRECT，选中等于全部流量被拦、直接断网）。想固定某个单节点又保留分流/防泄露，建议留在规则模式、在「🔀机场or单个切换」里选即可，效果等同。（Shadowrocket 是 Surge 格式，全局路由用 App 顶部的节点选择器、本就能选任意节点，不吃 GLOBAL 组，故未加。）

> **⚠️ 安卓 CMFA 必须把所有分组写进 GLOBAL**：Clash Meta for Android 的分组列表**只列 GLOBAL 成员里属于「组」的项**（`core/src/main/golang/native/tunnel/proxies.go` 的 `QueryProxyGroupNames`：取 `GLOBAL` 的成员逐个判断，非组的节点跳过），而不是列配置里定义的全部 `proxy-groups`。所以 GLOBAL 若只写 3 个组，其余服务组（🌍/🤖/🍎/📺/📲/🔒/🛑/🐟/🎯）在安卓端**全部不可见**，规则照常分流但没法手动切；桌面版 Clash Verge 不受影响（它直接读 `/proxies` API 列出所有组）。反直觉的一点：配置里**不写** GLOBAL 时 mihomo 会自动生成一个包含全部节点+全部组的 GLOBAL，CMFA 反而什么都能看到——手写 GLOBAL 才需要自己补全。`proxy_group_order` 只影响显示顺序，救不了这个。
>
> 当前各配置在 CMFA 的可见分组数（规则模式 / 全局模式）：`sub-rules.ini`、`sub-rules-adblock.ini` = 12 / 13；`jichang-rules.ini`、`dangevip-rules.ini` = 10 / 11；`basic.ini` = 2 / 3。全局模式多出的一项是 GLOBAL 自己。两份 `openclash*.ini` 只用于软路由，不进安卓客户端，故不在此列（它们的 GLOBAL 同样列全了分组，无害）。

规则优先级（自上而下）：局域网 → **个人自定义（直连/代理/屏蔽）** → STUN 防护 → AI → 广告拦截 → **抖音直播直连** → Telegram → 流媒体 → 国外合集 → 国内直连 → GEOIP CN → 兜底。个人规则永远最先匹配，社区规则误杀/漏杀都能在 `rules/` 里一票否决。

> 为什么抖音直播那张表排在广告拦截**之后**而不是最前面：`snssdk.com` 这个域下既有直播 API 和弹幕长连接，也有 25 条广告埋点子域（`i.` `log.` `mcs.` `pangolin.` `xlog.` `temai.` 等，见 `AdvertisingLite.list`）。整域直连若排在广告段之前，会把那 25 条一起放行。排在广告段之后，广告子域先被 REJECT，剩下的直播流量再落到直连，两边都不牺牲。
>
> 抖音规则为什么拆成两个文件：候选 70 条按「`geosite:cn` 是否已覆盖」二分。`geosite:cn` 已有的 58 条进 `douyin-live.list`，只给走 `China.list` 的 6 份配置引用；`geosite:cn` 也缺的 12 条（火山版 `hotsoon*`、`bytesyscdn` 等）进 `custom-direct.list`，因为那张表被全部 8 份配置共享，两份 `openclash*.ini` 靠它才拿得到。`bytednsdoc.com` 是第三种情况：`geosite:cn` 里有，但 `AI-VPSDance.list` 收了它的子域且 AI 段排得更早，只有 `custom-direct.list`（第 2 段）抢得回来，所以那张表的抖音段共 13 条。两个文件互斥不重叠：6 份主配置合起来仍是完整 71 条覆盖，而 `openclash.ini` 一行不改、只多拿它真正需要的 13 条，不必为 58 条冗余规则多下一张表。新增抖音域名时照此判据归类（`custom-direct.list` 排在广告段之前，放进去的域名必须与三张广告表零冲突，所以 `snssdk.com` 只能留在 `douyin-live.list`）。

精简版只有 `🚀 遵纪守法小组`（全部节点混在一起）和 `🔒 隐私防护` 两个组，其余规则直接落 DIRECT/REJECT，结构与旧 basic.ini 完全一致。

## Shadowrocket（iOS）专用说明

Shadowrocket 不是 Clash 内核，不吃 `sub-rules.ini` 那份 clash 配置（里面的 `dns`/`tun` 段是 mihomo 专用）。iOS 上单独用 `config/shadowrocket.ini`：

- **转换目标必须选 `Surge (ver 4)`**：实测老版 subconverter 后端不支持 `target=shadowrocket`（直接 400），而 Shadowrocket 原生兼容 Surge 配置格式，走 Surge 目标最稳。
- **远程配置**填 `https://raw.githubusercontent.com/utopia0051/my-sub-rules/main/config/shadowrocket.ini`
- 转换出来的订阅链接导入 Shadowrocket 即可；节点分组、机场/自建拆分、AI/流媒体/广告/隐私分流与 Clash 版完全一致。

**为什么 iOS 上防泄露反而更省事**：Shadowrocket 在 iOS 上本身就是全局 VPN（utun），所有流量含 UDP 天然走隧道——不需要像桌面那样纠结 TUN 开关，STUN 拦截规则直接生效。防 DNS 泄露靠 base 模板里的 DoH（`dns-server = https://...`）+ 关闭 IPv6，已配好。

两个与 Clash 版的技术差异（已在配置里处理好，仅供了解）：STUN 的端口规则在 Surge 的外部 RULE-SET 里会被丢弃，所以 `shadowrocket.ini` 把它们**内联**进规则段；社区规则集里的 IP-ASN/进程规则转 Surge 时也会被过滤（无害，覆盖略减）。

## OpenClash（软路由）专用说明

OpenClash 是 OpenWrt 上的 mihomo 内核插件。有三份配置可选：

- **性能够的软路由** → 直接用完整版 `config/sub-rules.ini`（和桌面同一份，规则最全）。
- **性能弱的软路由（推荐）** → 用软路由精简版 `config/openclash.ini`。它把 Global/China/AdvertisingLite 等大体量域名表换成 mihomo 的 **geosite/geoip 数据库**——`GEOSITE,geolocation-!cn` 一条规则顶 Global 的 3.4 万条，靠内核加载的二进制 geodata 匹配，**inline 规则量从几万条降到约几百条**，内存负担骤降。精华小表（AI 全套小表、金融/Emby/ACG、防泄露含 `STUN.list`、NTP/PT/远程桌面等特殊直连）全部保留，砍掉的只是大社区表、用 geosite 等效替代。节点全部 **select 手动选**（无自动测速组）。
  远程配置：`https://raw.githubusercontent.com/utopia0051/my-sub-rules/main/config/openclash.ini`
  代价：首次需下载 geodata 文件（geosite.dat ~4MB + geoip.dat ~17MB + ASN mmdb，OpenClash 本来也会下），之后匹配比 inline 大表更快更省内存。
- **弱软路由 + 只挂机场订阅（没有自建节点）** → 用 `config/openclash-jichang.ini`。分流规则与 `openclash.ini` 相同（同一套 geosite 精简规则、同样的防泄露），区别只在节点分组：去掉 `🔀机场or单个切换` 和 `🚀 遵纪守法小组`，只留一个 `✈️ 机场订阅` 组用 `.*` 收全部节点，共 **10 个分组**。
  远程配置：`https://raw.githubusercontent.com/utopia0051/my-sub-rules/main/config/openclash-jichang.ini`
  为什么需要单独一份：`openclash.ini` 的两个来源组靠**节点名关键字**（`机场订阅|IEPL|实验性|高级|标准`）互补切分，只挂机场订阅时必有一组匹配到 0 个节点，subconverter 不会删空组、而是塞一个 `DIRECT` 占位——面板里就多出一个「选中即直连」的壳组，误点等于全部流量裸奔。用 `.*` 全收则不筛关键字，换机场、机场改节点命名风格都不用动配置。

> `openclash-jichang.ini` 与其余配置一样是**独立的一份**，直接改它即可，没有生成脚本。它的规则段与 `openclash.ini` 内容相同、分组结构与 `jichang-rules.ini` 相同，但三份互不派生：改任一份都不会自动同步到另外两份。所以调整「所有 Clash 配置都该改」的东西（新增规则源、改优先级、换 base 模板）时，记得把同样的改动也过一遍其余同类配置。

填法：OpenClash → 配置订阅 → 添加订阅，地址填订阅转换链接，**弱路由请把远程配置指到 openclash.ini**（不要误用完整版）：
`.../sub?target=clash&udp=true&url=<订阅>&config=https://raw.githubusercontent.com/utopia0051/my-sub-rules/main/config/openclash.ini`

关键在 OpenClash 面板的几个开关，配对了防泄露 base 才生效（这是 OpenClash 版的"别让客户端覆盖配置 DNS"）：

1. **运行模式选 Fake-IP（增强模式）**——和 base 模板一致。
2. **让 OpenClash 用配置文件的 DNS**：在「插件设置 → DNS」里**关闭"自定义上游 DNS 服务器"**。开着它 OpenClash 会用自己的 DNS 顶掉我们 base 里的 fake-ip + DoH，防泄露就失效了。关掉后它遵循配置文件的 `dns` 段（加密 DoH + geosite 分流解析），DNS 泄露防护才成立。
3. **软路由是网关，全屋流量含 UDP 天然都过 OpenClash**——所以和 iOS 一样，防 WebRTC 泄露不用纠结 TUN 开关，🔒 隐私防护的 STUN 拦截直接生效。
4. base 里的 117 条 fake-ip-filter 会随配置生效；若 OpenClash 面板另有 fake-ip 过滤追加项，两者合并、不冲突（实测面板会追加一条 `rule-set:oc-cn-domain`，运行配置里共 118 条）。
5. **`allow-lan`**：共用 base 默认 `false`（桌面安全）；OpenClash 作网关时必须允许局域网访问。面板一般会强制改成 `true`——**不要关掉这项覆写**。（实测某台 OpenWrt 上 OpenClash 会整段重建监听配置：端口与绑定地址都由面板生成，base 里的 `mixed-port` / `allow-lan` 不参与。但这依赖 OpenClash 版本与面板设置，不保证所有环境一致，务必自行验证。）验证：`netstat -tlnp | grep -i clash`，绑定地址应为 `:::` 或 `0.0.0.0`；若是 `127.0.0.1` 则未覆写，局域网设备会连不上，需把生成配置里的 `allow-lan` 改为 `true`（用「严格跟随配置文件」时常见）。
6. **ASN 数据库**：`openclash.ini` 引用了含 `IP-ASN` 的 `AI-VPSDance.list` / `Copilot.list` / `OpenAI.list`（共 6 条），base 已写死 jsDelivr 的 `geox-url.asn`。（实测某台 OpenWrt 上，面板的数据库订阅只覆盖 `geosite` 与 `mmdb` 两个 URL——对应 UCI 的 `geosite_custom_url` / `geo_custom_url`，`asn` 与 `geoip` 保留配置文件的值。但这依赖 OpenClash 版本与面板设置，不保证所有环境一致，务必自行验证。）若面板确实覆盖了 `asn`，请一并改成同一 jsDelivr 地址，否则回落到 GitHub releases 直连，启动时代理未起、国内 TLS 超时、配置测试失败。验证：`grep -nA8 "geox-url" /etc/openclash/<你的配置>.yaml`。

验证同桌面：`dnsleaktest.com` 只出现落地节点 DNS，`browserleaks.com/webrtc` 不出现真实 IP。

## 防泄露使用须知（重要）

（以下针对**桌面 Clash 客户端**；iOS/Shadowrocket 见上一节，无需这些步骤。）

配置只解决一半，客户端上还要两步：

1. **开启 TUN 模式**（Clash Verge Rev / mihomo party 的 TUN/虚拟网卡开关）。WebRTC 走 UDP，只开"系统代理"时这些流量根本不进内核，谁也拦不住。模板已带好 TUN 参数（`auto-route` + `dns-hijack any:53` + `strict-route`）。
2. **不要在客户端里再开"DNS 覆写"**，避免覆盖模板里的防泄露 DNS（Clash Verge Rev：设置 → 关闭 DNS 覆写；mihomo party：使用配置自带 DNS）。

验证（开好 TUN 后逐项测）：

- DNS 泄露：`dnsleaktest.com` 扩展测试 → 只应出现落地节点地区的 DNS
- WebRTC 泄露：`browserleaks.com/webrtc`、`ipleak.net` → 不应出现真实公网 IP（这些检测站已在 `leak-test.list` 里强制走代理，看到的是统一节点 IP）
- IPv6：模板默认关闭（v6 直连绕过是常见泄露源），需要时在 base 里自行打开

**副作用**：拦 STUN 可能影响视频会议/语音（Meet、Discord、微信语音等）。会议连不上时把 `🔒 隐私防护` 切到节点组或 DIRECT，或在 `custom-direct.list` 里只为特定会议域名加白。

## 可选：硬核去广告配置 config/sub-rules-adblock.ini

平时用 `sub-rules.ini` 就够了（已有 AdvertisingLite + BanProgramAD + Hijacking 三层去广告）。如果哪天想要更狠的去广告，把前端远程配置换成 `config/sub-rules-adblock.ini` 即可——它就是完整版**多引用了一个** [Cats-Team/AdRules](https://github.com/Cats-Team/AdRules)（约 17 万条，中文区最激进的去广告规则之一），其余分组/防泄露/节点逻辑与 `sub-rules.ini` 完全一致。

- 远程配置：`https://raw.githubusercontent.com/utopia0051/my-sub-rules/main/config/sub-rules-adblock.ini`
- 代价：规则体量大（AdRules 约 6MB，内联后配置更大、mihomo 内存占用略高）、误杀率比 Lite 版高。被误杀的域名加进 `custom-direct.list` 放行即可。
- AdRules 已登记进 MANIFEST 的"可选镜像"区，首次同步会一并下载备好（防跑路）；主配置 `sub-rules.ini` **不引用**它，不受影响。
- 维护：`sub-rules-adblock.ini` 是 `sub-rules.ini` 的派生版（唯一区别是多一行 AdRules 引用）；主配置改动后如需同步，让 agent 重新生成即可。

> 🚧 **规则更新护栏（给未来的 agent 和我自己）**：凡是"拦截凶猛 / 误杀率高"的规则（AdRules 这类硬核去广告是典型），**必须经用户明确确认才能加进 `config/` 下的主配置**（sub-rules / basic / shadowrocket / openclash / openclash-jichang）。日常"更新规则镜像"只是刷新已登记镜像的内容，**绝不允许顺手把这类规则塞进主配置**。它们的正确归宿是独立的 `config/sub-rules-adblock.ini` 或 MANIFEST 的〔需用户确认〕清单。完整清单见 `rules/mirror/MANIFEST.txt` 末尾。

## 自定义规则维护

- 直连加白 → `rules/custom-direct.list`；强制代理 → `rules/custom-proxy.list`；屏蔽 → `rules/custom-reject.list`
- 一行一条 Clash classical 规则，`#` 注释；改完 push，客户端更新订阅即生效（转换时实时拉取）

## 致谢

社区规则来自 blackmatrix7、LM-Firefly、Loyalsoldier、ACL4SSR、Accademia、cmliu、[VPSDance/ai-proxy-rules](https://github.com/VPSDance/ai-proxy-rules)（AI 分流）等，完整来源见 rules/mirror/MANIFEST.txt。
