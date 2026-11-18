# GCP 团队说明与集成指南

## 1. 一句话解释我们在解决什么问题

今天的汽车/出行 App 是“人找货、人填表、人确认”；未来的个人 Agent 要“替人找货、替人判断适配、替人下单/预约”。通用 Agent 购物协议（Poppy/UCP/ACP）只解决“能不能买”，不解决汽车行业的“**买得对不对、安不安全、谁授权、出事怎么办**”。GCP 补的就是这一层：把车辆上下文、适配性、安全规则、授权额度、支付通道、异常恢复、证据链变成协议字段，让任何 Agent 都能安全地替用户买配件、买精品、约保养、买保险、约试驾/下订。

## 2. 对团队最有说服力的 5 个数字

| 指标 | 人工网页 | 通用 Agent | GCP |
|---|---|---|---|
| 任务成功率 | 64.5% | 69.4% | **92.2%** |
| 错买率 | 35.5% | 30.6% | **7.8%** |
| 异常恢复率 | 58.3% | 59.4% | **89.6%** |
| 座舱行驶中危险操作 | — | 47.9% | **0%** |
| 真实配件目录成功率 | — | 26.7% | **100%** |

补充：Stripe test-mode 授权实验（180 笔，180/180 对账）显示，限额委托把人工审批减少 70%，成功率不降。

## 3. GCP 是什么（对研发）

- 一套 HTTP/JSON + MCP/A2A 工具的开放协议；
- 核心对象：manifest、delegation credential、vehicle context、offer、cart/order、payment intent、booking、aftercare、evidence、typed error；
- 5 个一致性等级：L1 目录 → L2 购物车/结账 → L3 支付 → L4 服务/保险 → L5 安全/售后；
- 与 Poppy/UCP/ACP 的关系：Poppy 给身份/会话，UCP 给通用目录/购物车，ACP 给 Agent 支付；GCP 加汽车垂直语义，并标记 lossy 转换。

## 4. 三种角色的接入步骤

### A. 商家/经销商（4 步）
1. 发布 `/.well-known/gcp` manifest，声明能力、支付通道、服务区域、profile；
2. 实现 catalog、cart、checkout、payment intent、book、aftercare 端点；
3. 接入 PSP（支付宝/微信/银联/卡）和 VIN→fitment 服务；
4. 跑 conformance（`python3 conformance/run.py`），达到 L2/L3。

### B. OEM / 品牌方（5 步）
1. 部署 authorization vault：签发/撤销 delegation，执行 step-up，存证据；
2. 部署 vehicle context / fitment 服务：VIN→车型→配件/服务；
3. 发布安全规则与召回 feed；
4. 注册商家、设定授权阶梯与预算阈值；
5. 建立证据导出与审计（用户/监管）。

### C. PA 厂商（4 步）
1. 导入 GCP 工具 schema（MCP/A2A）：discover/catalog/cart/checkout/book/aftercare；
2. 接 Poppy 或 OAuth 做身份/会话；
3. 实现授权 UI（额度、商家、过期、step-up、撤销）与异常 UI；
4. 跑 conformance，接 OEM 沙箱。

### D. 座舱（2 条）
1. 行驶中只允许 L0/L1（浏览、加购、暂缓），L3+ 必须停车 + 生物识别；
2. 语音确认 + 分心约束；所有决定写 evidence。

## 5. 30 / 60 / 90 天落地计划

| 阶段 | 目标 | 交付 |
|---|---|---|
| 0–30 天 | 1 个 OEM App + 1 个经销商集团 + 1 个品类（精品/配件） | manifest、catalog、checkout、L2 conformance |
| 30–60 天 | 接 VIN→fitment、授权 vault、支付沙箱 | L3 测试、异常链路、对账 |
| 60–90 天 | 接入 1 个外部 PA（MCP）、座舱只读/加购 | 试点指标：成功率、错买率、审批次数、恢复率 |

## 6. 研发可以直接跑

```bash
python3 conformance/run.py                 # 13/13
python3 fitment/test_fitment.py            # VIN→fitment
export DASHSCOPE_API_KEY=...
python3 experiments/bench/runner.py --out experiments/results/acb.jsonl --tasks 60
```

## 7. 产品/商业价值

- 商家：Agent 带来的高质量流量、降低错买/退货/返修；
- OEM：保养留存、保险搭售、精品/配件增量、服务预约；
- PA：无需自建汽车供应链，即可安全上线“帮我买车品/约保养”；
- 支付/保险：新的分发入口；
- 协议开放免版税，价值在 gateway、认证、交易服务、导流。

## 8. 风险与边界

- 目前是 test-mode 支付，不是 live 资金；
- fitment 真实目录的兼容性字段是合成的；真实 VIN→配件数据需要 OEM/ACES/PIES/TecDoc 授权；
- 人类基线是校准模型，不是真人实验；
- 多 OEM、跨境税务/认证还需扩展；
- 安全关键件必须人工复核，协议不能替代法规。
