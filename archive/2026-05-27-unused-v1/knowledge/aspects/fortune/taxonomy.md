# Fortune Taxonomy

## Allowed levels

- `运势起势很顺`
- `运势整体可走`
- `有起伏，但还能借势`
- `运势波动偏明显`
- `当前不宜硬扛运势`

## Allowed types

- `顺流承接型`
- `平台放大型`
- `前通后滞型`
- `关系牵动型`
- `风险回拉型`
- `消耗承压型`
- `外放起伏型`
- `低开反复型`

## Taxonomy rule

- `level / type` 由代码层锁定。
- 大模型只负责解释，不负责改 taxonomy。
- 如遇 evidence 互相重叠，只解释主矛盾，不改档位。
