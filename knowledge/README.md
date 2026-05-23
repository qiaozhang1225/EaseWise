# Knowledge Base

这是给 `技能路径` 和 `产品路径` 共用的一套知识底座。

## 设计原则

1. `knowledge/` 是知识的单一事实源。
2. 技能路径和产品路径都只读取它，不各自复制知识。
3. 知识更新时，优先改这里，不优先改路径代码。
4. 路径代码负责“怎么调用”，知识底座负责“怎么判断、怎么表达、边界在哪里”。

## 目录结构

- `shared/`：多方面共用的基础知识
- `aspects/product/backend/career/`：事业专属知识
- `aspects/product/backend/stability/`：稳定性专属知识
- `aspects/product/backend/fortune/`：运势专属知识
- `aspects/product/backend/health/`：健康专属知识
- `aspects/product/backend/relationship/`：人际感情专属知识
- `aspects/product/backend/learning/`：学习专属知识
- `aspects/product/backend/suitable_job/`：适合职业专属知识
- `sections/product/backend/board_description/`：盘面解释专属知识

后续其他方面也按同样方式继续扩展。
