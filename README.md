# Origin_Skill_yyh

Origin 2021+ 内置 Python 批量 CSV 绘图 Skill。

下载 scripts/batch_csv_origin.py，复制到任意目录。在 Origin Python 控制台（提示符 >>>）运行以下一整行，将路径替换为实际位置：

```python
__import__('runpy').run_path(r'D:\path\batch_csv_origin.py', run_name='__main__')
```

选择文件夹后，递归查找 CSV。第一列为数值 X，后续数值列为 Y，每个文件一张原生可编辑图。结果保存在所选目录下 Origin_Plots_时间戳 文件夹，包括 PNG、CSV_plots.opju 和 run_log.txt。建议保存当前工程后，在空工程运行。

默认样式：Times New Roman 黑色粗体；坐标标题和刻度 23 pt，图例 19 pt；曲线 4 pt；四边轴框 5 pt；主/次刻度 1.6/1 pt。上右轴无刻度和数字，图例在框内右上角，每行分别加粗；主次网格为 0.8/0.4 pt 灰色虚线。紧凑裁切留白。

[下载 Skill ZIP](Origin_Skill_yyh.zip) · [Skill 说明](SKILL.md)

不平滑、不插值、不抽样；非数值单元格转缺失，单文件失败记录日志并继续。日期或分类 X、多层表头、混合单位需要先适配。当前工程已有内容会包含在另存的 OPJU 中。

已通过 Skill 格式、Python 语法及基础 CSV 解析检查，尚未完成 Origin 渲染实测。
