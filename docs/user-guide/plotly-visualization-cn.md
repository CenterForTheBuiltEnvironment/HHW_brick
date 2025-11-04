# Plotly 交互式可视化功能

## 功能概述

HHW Brick 框架现已支持使用 **Plotly 生成交互式 HTML 可视化**，除了传统的静态 matplotlib 图表之外，还提供了更加强大的交互式数据探索能力。

## 主要特性

✨ **4 种交互式可视化类型**：
1. **综合仪表板** - 包含 6 个子图的多面板展示
2. **详细时间序列** - 双 Y 轴温度分析图
3. **热力图** - 小时 vs 星期的模式分析
4. **箱线图** - 统计分布分析

🎯 **交互功能**：
- 缩放和平移数据
- 悬停显示详细信息
- 点击图例切换显示/隐藏
- 导出高质量图片
- 以独立 HTML 文件分享

## 快速开始

### 1. 启用 Plotly 可视化

在配置文件 `config.yaml` 中：

```yaml
output:
  generate_plotly_html: true  # 启用 Plotly
  output_dir: "./results"     # 输出目录
```

### 2. Python 代码使用

```python
from hhw_brick.applications.primary_loop_temp_diff.app import analyze, load_config

# 加载配置
config = load_config()
config["output"]["generate_plotly_html"] = True  # 启用 Plotly

# 运行分析
results = analyze(
    "brick_model.ttl",
    "timeseries.csv",
    config
)
```

### 3. 命令行使用

```bash
# 运行主循环分析（自动生成 Plotly 可视化）
python -m hhw_brick.applications.primary_loop_temp_diff.app \
    brick_model.ttl \
    timeseries.csv \
    --output-dir ./results
```

### 4. 使用示例脚本

```bash
cd examples
python 09_plotly_visualization.py
```

## 生成的文件

运行分析后，会在输出目录生成以下文件：

```
results/
├── primary_loop_interactive_dashboard.html      # 📊 综合仪表板
├── primary_loop_timeseries_interactive.html     # 📈 详细时间序列
├── primary_loop_heatmap_interactive.html        # 🔥 模式热力图
├── primary_loop_boxplot_interactive.html        # 📦 分布箱线图
└── [其他 CSV 和 PNG 文件]
```

## 可视化详情

### 1. 综合仪表板（Dashboard）

包含 6 个子图：
- **供水和回水温度** - 时间序列对比
- **温差变化** - 温度差异趋势，带平均线
- **分布直方图** - 温差分布统计
- **供水 vs 回水散点图** - 相关性分析
- **小时模式** - 按小时统计的温差均值
- **星期模式** - 按星期统计的温差均值

**特点**：一次查看所有关键指标

### 2. 详细时间序列（Timeseries）

双 Y 轴设计：
- **左轴**：供水温度（红色）和回水温度（蓝色）
- **右轴**：温度差异（紫色）
- **阈值线**：最小和最大阈值标记

**特点**：可以同时观察温度和温差的变化趋势

### 3. 热力图（Heatmap）

二维模式分析：
- **X 轴**：星期（周一到周日）
- **Y 轴**：小时（0-23）
- **颜色**：平均温差值

**特点**：快速识别时间模式和异常时段

### 4. 箱线图（Box Plot）

统计分布展示：
- 四分位数
- 中位数和均值
- 异常值标记
- 标准差范围

**特点**：理解数据分布和离散程度

## 交互操作

### 基本操作
- **平移**：点击并拖动图表
- **缩放**：滚轮放大/缩小
- **重置**：双击图表
- **切换**：点击图例隐藏/显示数据系列
- **悬停**：鼠标移到数据点查看详情
- **下载**：点击相机图标保存为 PNG

### 高级功能
- **框选缩放**：工具栏选择框选工具
- **自动缩放**：工具栏的 Autoscale 按钮
- **比较模式**：显示多个数据系列进行对比

## 配置选项

### 只生成 Plotly（不生成 matplotlib）

```python
config = load_config()
config["output"]["generate_plots"] = False        # 禁用 matplotlib
config["output"]["generate_plotly_html"] = True   # 只用 Plotly
```

### 自定义输出目录

```python
config["output"]["output_dir"] = "./my_results"
```

### 自定义数据格式

```python
config["output"]["export_format"] = "json"  # 或 "csv"
```

## 应用支持

当前支持 Plotly 可视化的应用：

1. ✅ **primary_loop_temp_diff** - 主循环温差分析
2. ✅ **secondary_loop_temp_diff** - 次循环温差分析

所有新的分析应用都将默认支持 Plotly 可视化。

## 优势

### 📊 数据探索
- 快速缩放到特定时间段
- 悬停查看精确数值
- 轻松识别异常值

### 🎨 专业展示
- 现代化、美观的可视化
- 无需 PowerPoint，直接在浏览器中展示
- 演示过程中实时交互

### 📄 报告集成
- 嵌入到 HTML 报告中
- 独立文件，无外部依赖
- 任何设备和浏览器都能查看

### 👥 协作共享
- 通过邮件或云存储轻松分享
- 无需安装 Python 即可查看
- 团队成员可以交互式探索数据

## 性能提示

- **大数据集**：Plotly 可以处理约 10 万个数据点。更大的数据集建议降采样
- **文件大小**：HTML 文件通常在 500KB - 5MB 之间
- **加载时间**：典型数据集的初始加载时间为 1-3 秒

## 示例代码

查看完整示例：

```bash
examples/09_plotly_visualization.py  # Plotly 专用示例
examples/07_run_application.py       # 程序化运行应用
```

## 文档

详细文档请参考：
- `docs/user-guide/plotly-visualization.md` - 完整英文文档

## 依赖

```bash
# 自动包含在 requirements.txt 中
plotly>=5.0.0
```

## 技术支持

如有问题，请查看：
1. 生成的 HTML 文件中的交互式帮助
2. 文档中的故障排除部分
3. Plotly 官方文档：https://plotly.com/python/

---

**提示**：Plotly 可视化默认启用，无需额外配置即可使用！
