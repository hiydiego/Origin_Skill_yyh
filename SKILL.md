---
name: origin-csv-plot
description: 在 Origin 中批量绘制文件夹及子文件夹内的 CSV 数值曲线，输出可编辑 OPJU 工程和 PNG，并使用统一的 Times New Roman 黑色粗体、四边框和虚线网格样式。用于 Origin CSV 批量绘图或修改该流程的样式；不用于统计分析或非数值 X 轴数据。
---

# Origin CSV 批量绘图

使用随附的 [scripts/batch_csv_origin.py](scripts/batch_csv_origin.py)，不要用 matplotlib 图片代替 Origin 原生曲线。

## 运行

目标环境是 Windows 上 Origin 2021+ 的内置 Python，需提供 `originpro` 和 tkinter。脚本运行后弹出文件夹选择框，默认从当前工作目录开始；递归搜索所选文件夹全部 CSV（扩展名不区分大小写）。用户取消选择时不做修改。需要固定目录时只改脚本开头的 `DATA_FOLDER`；关闭子文件夹搜索时设 `RECURSIVE=False`。

在 Origin 的 Python 控制台（提示符 `>>>`）中，提供下面的一整行，路径替换成用户实际存放脚本的位置：

```python
__import__('runpy').run_path(r'D:\path\batch_csv_origin.py', run_name='__main__')
```

控制台一次只接收一条语句，不要让用户一次粘贴多行。不要在 `>>>` 中使用 LabTalk 的 `run -pyf`，该命令属于 Script Window。脚本可以单独复制到任意位置，不依赖本 Skill 的路径或原项目数据目录。

## 数据与输出

- 每个 CSV 生成一个工作表和一张图。第一列必须是数值 X，后面的数值列是 Y；多条 Y 曲线绘在同一图中。日期、分类 X、多层表头或混合单位需要先检查并适配，不应猜测解释。
- 支持 UTF-8、GB18030、UTF-16 以及逗号、分号、制表符。根据第一列首个值是否为数值判断有无表头，这是启发式判断，应对不常规表头进行核对。
- 保留原始数据顺序、全部数据行和缺失值，不平滑、不插值、不抽样；非数值单元格转缺失，全空/无有效 X-Y 配对的 Y 列不画。非数值文字列在数值工作表中不保留原文字，若需要保留应单独导入文本列。
- 将 PNG、包含原生图和工作表的 `CSV_plots.opju`、逐文件结果 `run_log.txt` 写入所选目录下独立的 `Origin_Plots_时间戳` 文件夹。已有结果文件夹不参与搜索。
- 单个文件失败记录错误并继续，不把部分成功报告为全部成功。大文件可能需要较多内存与时间，不静默抽样。脚本保留当前 Origin 会话，新 OPJU 副本也会包含当前会话已有内容；推荐在空工程运行，先保存已有工程。

## 默认样式

用户的新要求优先于这些可修改默认值：

| 元素 | 设置 |
|---|---|
| 曲线 | 4 pt，按不同颜色区分 |
| 四边轴框 | 5 pt |
| 主/次刻度 | 1.6 / 1 pt，向内 |
| 上轴、右轴 | 仅边框，无刻度和数字 |
| 坐标轴标题 | Times New Roman，23 pt，黑色粗体 |
| 刻度数字 | Times New Roman，23 pt，黑色粗体 |
| 图例 | Times New Roman，19 pt，黑色粗体，带框，绘图区内部右上角 |
| 主/次网格 | 灰色/浅灰虚线，0.8 / 0.4 pt |
| 页面 | 紧凑裁切，横轴使用有效数据范围 |

## 接口注意与检查

- **不要使用 `plot.width = ...`**：它不控制 Origin 实际曲线线宽。使用 `plot.set_cmd('-w 2000')` 设置 4 pt；`-w` 的换算为 **每 pt 500 单位**。
- 图例的每一行分别使用 `\b(...)` 加粗，不能只给多行文本的外层加一次标记，否则可能只有第一行生效。保持各条图例样线颜色，只将文字设黑色。生成图例后再计算右上角位置，最后紧凑裁切。
- 保持坐标标题、刻度、图例字号分别设置；不能把坐标轴粗细和曲线粗细混用。
- 提供脚本时检查 Python 语法和 CSV 解析；未实际运行 Origin 时明确说明，不声称显示效果已经验证。实际可运行时检查所有图例行、刻度/轴框、虚线网格、文字是否裁切及是否遮住曲线。图例与曲线冲突时调整布局，而不删除观测值。

接口来源：[Plot.set_cmd](https://docs.originlab.com/originpro/classoriginpro_1_1graph_1_1Plot.html)、[线宽单位示例](https://docs.originlab.com/labtalk/guide/formatting-graphs/)、[网格属性](https://docs.originlab.com/labtalk/ref/layer-axis-grid-obj/)。
