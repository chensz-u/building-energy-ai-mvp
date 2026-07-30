# Building Energy AI MVP (个人复现)

这是一个独立的、可运行的个人复现 MVP，用于展示建筑能耗数据如何经过 PostgreSQL 分析工具后，被一个工具优先的问答代理转换为带数据依据的回答。它**不是**原 `Building-Energy-Intelligent-MOS` 比赛项目的完整源码恢复，也不包含原比赛 PPT、视频、图片、私有/大规模数据或任何未公开材料。

## 问题与个人负责范围

我负责此仓库中的 Python MVP：脱敏小样本入库、PostgreSQL 查询、三个可验证分析工具、工具优先问答 API 与固定评测集。原比赛材料中描述的 Java/React、RAG、MCP、鉴权、生产性能和 4,880 万条数据能力不在本仓库实现范围内，因此不作此类声明。

```text
脱敏 CSV -> PostgreSQL energy_readings -> 三个分析工具 -> ToolFirstAgent -> /v1/ask（回答 + 工具调用 + 证据）
```

## 可运行能力

| 工具 | 实际计算 | 结果证据 |
| --- | --- | --- |
| `energy_trend` | 按日聚合能耗 | 样本数、总 kWh、日聚合点 |
| `locate_anomalies` | 均值 + 1.5 倍总体标准差阈值定位高值 | 基线均值、阈值、异常时刻 |
| `weather_energy_correlation` | 温度与能耗 Pearson 相关系数 | 样本数、温度/能耗取值范围 |

问答路由会先执行以上其中一个工具，再返回工具调用和 `evidence`。它是确定性的工具优先路由，不使用 LLM、RAG 或 MCP。

## 数据说明

`data/energy_readings_sample.csv` 是 12 条人工构造的脱敏演示数据（两栋虚拟建筑、三天小时级读数），仅用于复现实验和接口演示；与比赛材料提到的原始大规模数据没有派生关系。

## 启动与演示

```bash
docker compose up -d --build
docker compose exec app python scripts/seed_data.py
curl http://localhost:8081/health
curl -X POST http://localhost:8081/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"定位 B-01 的能耗异常","building_id":"B-01"}'
docker compose exec app python scripts/run_evaluation.py
docker compose down
```

返回内容包括自然语言结论、实际调用的工具、输入参数、工具原始结果与数据证据。API 仅分析，不控制设备或生成节能承诺。

## 验证口径

```bash
python -m pytest -q
docker compose config --quiet
```

`evaluation/questions_v1.jsonl` 包含 20 条问题。评测记录每题预期工具是否实际调用、回答是否带证据，以及执行失败原因；它不被解释为模型准确率、节能效果或生产性能指标。

## 限制与后续

- 样本量很小，只用于复现工具调用与证据链，不能外推到真实园区。
- 异常规则是演示用统计阈值，需要由领域人员结合季节、工况与设备状态校准。
- 当前没有 RAG、LLM、MCP、前端或生产鉴权实现；这些都不应写入简历成果。

