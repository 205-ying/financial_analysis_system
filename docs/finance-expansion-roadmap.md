# 财务系统扩展功能清单

本文档基于当前项目能力、餐饮经营场景，以及主流财务系统公开能力说明整理。当前已实现“财务运营中心”，用于把现有订单、费用、预算、导入任务和审计数据转成现金流、往来款、预算控制、关账准备和能力成熟度视图。

## 依据来源

- [Oracle NetSuite Financial Management](https://www.netsuite.com/portal/products/erp/financial-management.shtml): financial close, compliance, reporting and real-time financial visibility.
- [NetSuite Cloud Accounting Software](https://www.netsuite.com/portal/products/erp/financial-management/finance-accounting.shtml): recording transactions, managing payables and receivables, closing the books, fixed assets, taxes and cash positions.
- [Microsoft Business Central Financial Management](https://learn.microsoft.com/en-us/dynamics365/business-central/finance): receivables, payables, transaction registration, bank reconciliation, vendor payment, customer payment and employee expense reimbursement.
- [Microsoft Dynamics 365 Finance documentation](https://learn.microsoft.com/en-us/dynamics365/finance/): real-time financial operation monitoring, outcome prediction and data-driven finance decisions.
- [Microsoft ledger and subledger accounting overview](https://learn.microsoft.com/en-us/dynamics365/finance/general-ledger/ledger-subledger): AP, AR, inventory, fixed assets, tax and production as finance subledgers.

## 已落地能力

| 能力 | 当前状态 | 项目实现 |
| --- | --- | --- |
| 现金流监控 | 已落地 | `GET /api/v1/finance/operations-overview` 汇总订单净额与已审批/已支付费用，前端展示现金流曲线。 |
| 应收应付与结算 | 部分支持 | 从未完结订单、未记录收款时间订单、待付款费用估算往来款风险。 |
| 预算控制 | 已落地 | 按费用科目输出预算、实际、差异、执行率和控制状态。 |
| 经营行动清单 | 已落地 | 根据负现金流、超预算、往来款风险自动生成优先行动。 |
| 关账准备 | 已落地 | `GET /api/v1/finance/close-readiness` 输出收入确认、费用审批、付款截止、预算覆盖和审计留痕检查清单。 |
| 银行对账准备 | 部分支持 | 按收款/付款通道汇总应对账金额、缺口笔数和缺口金额，为后续银行流水核销做前置检查。 |
| 总账底稿准备 | 部分支持 | 基于订单、费用、预算和审计日志输出收入/费用/预算/审计底稿覆盖率；尚未生成正式凭证。 |
| 财务能力成熟度 | 已落地 | 页面展示现金流、往来、预算、总账、资产、税务等能力成熟度。 |
| 财务核算中心 | 已落地 | `GET /api/v1/finance/suite-overview` 一次性聚合总账、银行对账、应收应付、预算审批、固定资产、税务发票、关账合并七个剩余功能模块。 |

## 下一阶段建议

| 优先级 | 功能 | 说明 |
| --- | --- | --- |
| P0 | 总账与会计期间 | 一期已接入科目映射、会计期间和凭证预览；后续升级为正式凭证、科目余额、期间关账/反关账。 |
| P0 | 银行流水与对账 | 一期已接入收付款通道对账账户；后续增加银行账户、流水导入、订单收款核销、费用付款核销。 |
| P1 | 应收应付台账 | 一期已从未完结订单和待付款费用生成往来台账；后续引入客户/供应商账期、发票状态、账龄、催收和排款清单。 |
| P1 | 预算版本与超预算审批 | 一期已按费用科目生成滚动预算版本和审批状态；后续支持版本调整记录、审批流节点和责任人流转。 |
| P1 | 固定资产 | 一期已从设备/装修/资产类费用提取资产卡片线索并测算折旧；后续建设正式资产卡片、盘点、调拨、处置和折旧凭证。 |
| P2 | 税务与发票 | 一期已建立销项/进项税额测算和缺票检查；后续建设发票台账、税率规则、勾稽和申报辅助报表。 |
| P2 | 财务关账与合并 | 一期已建立多门店合并预览和阻断项检查；后续增加正式关账状态、合并抵消分录和留痕审批。 |

## 本次实现入口

- 后端: `services/api/app/api/v1/finance.py`
- 服务: `services/api/app/services/finance_service.py`
- 前端页面: `apps/web/src/views/finance-center/index.vue`
- 前端核算中心: `apps/web/src/views/finance-suite/index.vue`
- 前端接口: `apps/web/src/api/finance.ts`

## 关账准备口径

当前关账准备功能是只读预检查，不写入会计凭证或关账状态：

- 收入口径: 有效订单、订单状态、支付方式、收款时间和订单净额。
- 费用口径: 费用状态、费用科目、供应商、发票号、支付方式和付款账户。
- 对账口径: 按收款/付款通道汇总应对账金额，并标记缺少收付款时间、支付账户或已审批未支付的记录。
- 底稿口径: 通过收入、费用、预算、审计日志覆盖率判断是否具备进入总账建模的基础。

## 财务核算中心口径

`/finance-suite` 是剩余功能的一期统一工作台，当前不替代正式会计引擎：

- 总账与会计期间: 建立科目映射、期间状态和凭证预览，不执行正式过账。
- 银行流水与对账: 以支付方式、支付账户和收付款状态形成对账账户视图。
- 应收应付台账: 以未完结订单、未记录收款时间订单、已提交/已审批费用形成往来台账。
- 预算版本与审批: 基于预算和实际费用生成滚动预算版本、差异和审批需求。
- 固定资产: 从设备、装修、资产类费用中提取资产卡片线索并按 36 个月测算折旧。
- 税务与发票: 基于订单收入和费用记录做税额测算，并标记缺票风险。
- 关账与合并: 以门店为单位生成收入、费用、利润、阻断项和合并口径预览。
