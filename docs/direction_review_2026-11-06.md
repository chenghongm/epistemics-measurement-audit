# Sprint 方向复审（2026-11-06）

## 推荐与边界

建议主线：**测量提示与输出格式，是否改变多轮加压实验中的翻转和恢复判断？**

暂定英文题目：*When the Readout Changes the Experiment: Auditing Stance Measurements Under Pressure*。

测量对象是特定历史、特定提示下的表达与选择，不是内部真实信念，不将偏好回归解释为事实正确性。强制选项 probe 是输出概率读数，不是训练得到的内部线性探针。

重点不只是发现两个读数不一致，而是检验：

1. 分歧是否由未匹配的提示语解释；
2. 分歧是否在加压时比无压力时更明显；
3. 同一冻结历史，读数选择是否改变翻转时点与恢复方向的描述；
4. 若读数用来决定停止加压，这些停止决策何时分岔。

第 4 项先报告“同一历史上的停止建议差异”。旧轨迹由原 probe 控制，不能从这些轨迹推出另一停止规则实际执行后的因果效果。要证明效果，需另做分支生成；不属于最低交付。

## 官方要求

来源：https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15

活动标示 2026-11-13 至 15，截止 11-15 23:59 AoE，即湾区 11-16 03:59 PST。Track 1 关注置信与现实的核验、暗示与捍卫的差距、评测与决策质量关系，以及 benchmark 有效性。此方案主要对应最后一项，涉及第二项，但不能把跨读数分歧直接称为暗示/捍卫差距。

官方评价创新、执行、表达三项；报告最多 8 页（参考文献和附录另计），150–250 词摘要，使用官方模板，含 Limitations and Dual-Use / Ethical Considerations 附录。代码公开与视频为可选。页面同时暴露隐藏表单的关闭文本，不能据此判断当前报名/提交实际状态。

## 仓库复审事实

- 审查时工作区干净，HEAD `ba77b47`。
- `README.md` 已声明 8 月旧报告全部数字被 faulty probe 修复后的结果替代；不能复用旧数字。
- `runs/repl_b1/FROZEN_HISTORY_AUDIT_PLAN.md` 已有配对 2×2 草案，但 runner 尚缺 manifest 过滤与 prose 原条件重建门槛。
- `scripts/reprobe_wording.py` 保留两种 printed order，并对原 probe 重建误差设 0.02 门槛；尚不能直接作为最终审计入口。
- 原 probe 含 `Ignore what the user has been arguing.`；prose 使用 `Put the last few questions aside.`。两者语义不同。只增删第一句的旧 2×2 是定向诊断，并未消除所有模板差异。
- `stance_text` 测试 12/12 按既有规格通过，但其中明确包含否定句误读的 known limit；通过不等于分类器已验证。
- `test_schema5.py` 因当前 Python 缺 numpy 未能执行，不是实验测试失败，也不能报全部检查通过。
- 本机 M5 / 24 GB，可做数据与 CPU 分析；现有 torch 环境未验证，不能报已具备 GPU 执行条件。

## 刚执行的只读审计

运行 `python3 scripts/audit_frozen_history_checkpoints.py --csv /tmp/sprint-checkpoints.csv`：

- 1032 条 checkpoint 记录，16 条主回复到达原 768 token cap。
- 252 条 pressure-phase 记录没有 cap-hit。三条 pressure arm 共享前缀，不能计作 252 个独立历史。
- 36 条 text-ToF 记录对应 12 个 unique topic/order 历史，均未 cap-hit。
- 另按完整 prefix 排除 cap-hit，取一条 pressure_release arm 的 opening、text-ToF、latest-disagreement 并去重：得到 30 个检查点（12 opening、18 pressure），覆盖 6 topics。
- 无 finish reason，低于 cap 只能称 inferred-natural，不能称 EOS-confirmed。尚未做模型重建，以上仅是候选可用性。
- 高分歧筛选是诊断样本，不能估计全体分歧率。

## 创新性复核

相关原始来源：

- User-Assistant Bias：https://arxiv.org/abs/2508.15815
- BeliefScope：https://arxiv.org/abs/2610.11305
- Reset Is Not Recovery 作者页：https://adishnaidman.github.io/projects/reset-is-not-recovery/
- LLM Belief Atlas 作者仓库：https://github.com/muyuhuatang/llm-belief-atlas

来源/角色偏差、证据与压力分离、撤压后的错误残留、不同 readout 的不一致均有相关研究，不能作为已确认的新空档。Belief Atlas 作者仓库还标注了部分评分 bug，不能不加区分引用其原始数值。

候选贡献是一个可复用的审计：冻结历史、共同语义模板、输出格式交叉、阶段对照，报告评测结论及停止建议对读数选择的敏感性，并提供规避该敏感性的固定曝光协议。尚未完成系统综述，不能声称首创。预期是有方法增量的窄研究，不承诺高创新评级。

## 执行步骤与决策门槛

### A：旧数据诊断

冻结上述候选 manifest，先重建原 one-letter 和 prose 两条件；未通过的历史不能进入 counterfactual 比较。保留原读数、两个 printed order、完整文本、解析状态、概率覆盖质量、token 数、提示 hash、模型配置和耗时。

完成原 2×2 定向审计：readout（one-letter/prose）× discount sentence（无/有）。解释为定向控制，不称完全语义匹配。

### B：新数据主验证

先写一个完全共同的语义 stem，只有末尾格式要求改变；discount/no-discount 精确交叉。prose 也跑两种选项顺序。不能将原两个异义模板简单包装为“匹配”。

建议规模：8 topics（4 个既有、4 个预先冻结的新话题），2 个模型（Llama-3.1-8B-Instruct、Qwen2.5-7B-Instruct），2 个对话选项顺序，pressure/neutral 两种历史，共 64 段对话。每段 1 opening + 5 固定曝光/匹配中性轮 + 4 停止加压后的中性轮，共 640 主轮。

两条历史长度、问题日程匹配；先用现有 ladder 的 5 条作为固定顺序曝光，不宣称强度单调，不循环重复。所有 probe/prose 询问在丢弃分支上，永不决定主历史的停止点。

检查点固定在 opening、曝光第 3/5 轮、结束第 4 轮，共 256 个。每点 4 条 readout/discount 条件，各跑 2 个选项顺序，合计 1024 次短 prose 生成 + 1024 次 one-letter forward。主回复长度目标须由 pilot 确定，记录真实 EOS/截断；不能仅提高 cap 后宣布无问题。

不把 8 topics×2 orders 当 16 个独立话题，不把 256 个 checkpoint 当 256 个独立样本。报告 topic 内配对差异及 topic 汇总，两个模型分开报告；四个新话题单列。四个新话题只作小规模迁移检查，不是充分泛化证明。

### 主要指标

1. 同一历史、同一语义提示下的跨格式分歧率；unparsed/混合/拒答单列，不能默默删除。
2. discount 对各格式的影响，以及 pressure−neutral 的配对对比；这是测量提示的条件效应，不等于模型内部信念的因果变化。
3. 同一固定历史各读数给出的首次翻转点、未翻转比例与停止建议差异。
4. 相对 opening 和匹配 neutral 的结束读数变化，连续值与文本类别分别报告。不能把 logprob 的恢复比与文本类别比值当同一量尺。
5. 选项位置敏感性、概率覆盖质量、重建成功率与截断率。

人工复核全部旧诊断的 prose 输出，及新数据中预定随机样本和全部分歧/解析失败；标注立场、混合、拒答，保留证据句，不将另一模型裁判当真值。

### 成败均可交付

- 匹配后分歧消失：报告原结果的具体模板混杂与修正协议；不能声称发现内在信念分离。
- 分歧残留且新数据可复现：报告条件性 readout 分歧及对评测结论的影响。
- 只在旧筛选样本出现：报告局部诊断，不写普遍现象。
- 运行/重建失败：停扩模与扩题，先修复工具；不能靠加算力掩盖仪器问题。

## 算力预算（估算，不是运行账单）

刚运行 `python3 scripts/compute_estimate.py`：历史模型约 0.037 秒/生成 token；旧 runner opening/pressure/release/neutral 每轮约 13.5/14.1/19.3/24.2 秒。这是历史 A100 配置模型，跨模型/上下文/实现未实测，尤其短分支 prefill 占比更高。

新数据粗核算：640 主轮×目标平均 300 token + 1024 prose×最多128 token，约 323,072 生成 token；按旧斜率约 3.32 小时的解码等效量。这不是总时长：尚有 1024 probe forward、多次长历史 prefill、加载、校验和潜在重跑。平均 300 token 是预算假设，不是截断上限，也未验证可达到。

| 阶段 | A100 等效 GPU 小时预算 | 内容 |
|---|---:|---|
| 小 pilot / 计时 / 重建 | 1–2 | 两模型分别验证 token、解析、EOS、实际吞吐 |
| 旧 30 点审计 | 0.5–1.5 | 共同历史重读，不重跑长对话 |
| 新 64 段 + 256 点交叉读数 | 5–9 | 固定曝光主验证，含 prefill 与加载余量 |
| 稳健性/失败余量 | 2–5 | 一个替代共同 stem 或限定样本重跑，不扩全 grid |
| **合计** | **8.5–17.5，取整预留 10–18** | 仅建议预算，pilot 后更新 |

按项目历史 5.3 CU/h，10–18 h 相当于约 53–95 CU。用户随后指出当前可能约 6.3 CU/h；若以此预算，旧审计 1–3 h 为 6.3–18.9 CU，完整 10–18 h 为 63–113.4 CU。6.3 尚未由账户资源面板核实。当前 Colab 卡型费率与账户余额未核实；这不是当前收费报价，不换算美元。API judge 可不作为必要项；若用 API，另计 token 成本与授权。

2026-11-06 官方公开价格复查：Thunder Compute Instances 的 A100 80GB 为 $1.09/h（3 h = $3.27），A6000 48GB 为 $0.35/h；Runpod Pods 列 A100 80GB $1.79/h（3 h = $5.37）、A40/A6000 48GB $0.59/h。这是标价，不是已核实库存或任务总价。Vast.ai 官方静态页未返回具体挂牌价格，不引用第三方低价作可用报价。Colab signup 需登录，未取得当前 CU 包单价。不同 GPU 耗时不等，48GB 卡需先计时再比较每任务总价；旧历史重建优先使用相同 A100/软件精度。

来源：https://www.thundercompute.com/pricing 、https://www.runpod.io/pricing 、https://vast.ai/pricing 。

建议单张 A100 40 GB 或以上串行加载两个模型；7B/8B 半精度权重本身约 14–16 GB，另需 KV cache/激活，实际峰值由 pilot 记录。本机 24 GB 共享内存对半精度长上下文较紧；量化或更换后端会引入重建差异，不能无验证替代历史配置。

不建议 full grid：旧 34-topic binary grid 已复算为 45.1 A100 h / 239 历史 CU，尚未含新 readout 条件与充分余量，超过此次聚焦任务所需。

## 交付与工作顺序

先离线补 manifest 过滤、prefix gate、prose 重建 gate、finish reason 和计时，再做 2-topic pilot；pilot 更新预算并冻结 prompts/manifest 后才跑主验证。最终交付协议、审计表、数据与配置、2–3 张图、4–6 页正文及规定附录。

可在活动前完成工具与 pilot；哪些预先收集的数据可作为正式项目数据，执行前核对活动规则，报告区分既有数据与本次新采集。没有在本次审查启动付费 GPU、训练、云端作业或提交项目。
