# Secondary Loop Temperature Differential Analysis App

## 概述

这是一个用于分析热水系统二次循环供回水温差应用程序。它可以：
- 自动检测 Brick 模型中是否有必需温度传感器
- 加载和分析时序数据
- 生成统计摘要和可视化图表
- 识别异常温差情况

## 功能特点

✅ **自动点位检测**: 检查 Brick 模型是否包含所需供水和回水温度传感器  
✅ **灵活配置**: 支持自定义时间范围、阈值和输出格式  
✅ **多种传感器类型支持**: 自动识别etc.效传感器类型  
✅ **丰富统计分析**: 计算平均值、标准差、分位数etc.  
✅ **可视化图表**: 自动Generated time序Columns图、分布图和按小时统计图  
✅ **异常检测**: 识别超出正常范围温差值  

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- pandas
- numpy
- matplotlib
- seaborn
- rdflib
- brickschema
- pyyaml

## 快速开始

### 1. 检查建筑是否符合分析条件

```bash
python -m hhw_brick.analytics.apps.secondary_loop_temp_diff.checker \
    path/to/brick_model.ttl
```

### 2. 运行基本分析

```bash
python -m hhw_brick.analytics.apps.secondary_loop_temp_diff.app \
    path/to/brick_model.ttl \
    path/to/timeseries_data.csv
```

### 3. use自定义配置

```bash
python -m hhw_brick.analytics.apps.secondary_loop_temp_diff.app \
    path/to/brick_model.ttl \
    path/to/timeseries_data.csv \
    --config config.yaml
```

## Python API use

### 最简单方式

```python
from hhw_brick.analytics.apps.secondary_loop_temp_diff.app import SecondaryLoopTempDiffApp

# 创建应用实例
app = SecondaryLoopTempDiffApp(
    brick_model_path="path/to/brick_model.ttl",
    timeseries_data_path="path/to/timeseries_data.csv"
)

# 运行分析
results = app.run()

# 打印摘要
if results['status'] == 'success':
    app.print_summary()
```

### use自定义配置

```python
config = {
    'time_range': {
        'start_time': '2018-01-01',
        'end_time': '2018-12-31',
    },
    'analysis': {
        'threshold_min_delta': 1.0,  # 最小温差阈值 (°C)
        'threshold_max_delta': 10.0,  # 最大温差阈值 (°C)
    },
    'output': {
        'save_results': True,
        'output_dir': './results',
        'export_format': 'csv',  # 'csv' or 'json'
        'generate_plots': True,
        'plot_format': 'png',  # 'png', 'pdf', 'svg'
    }
}

app = SecondaryLoopTempDiffApp(
    brick_model_path="path/to/brick_model.ttl",
    timeseries_data_path="path/to/timeseries_data.csv",
    config=config
)

results = app.run()
```

### 仅检查点位

```python
from hhw_brick.analytics.apps.secondary_loop_temp_diff.checker import SecondaryLoopTempDiffChecker

checker = SecondaryLoopTempDiffChecker("path/to/brick_model.ttl")
is_qualified = checker.qualify()

if is_qualified:
    print("✅ 该建筑可以运行此分析")
else:
    print("❌ 该建筑缺少必需传感器")
```

## 输入要求

### Brick 模型 (.ttl)

必须包含以下类型传感器之一：

**供水温度传感器 (任一):**
- `Supply_Water_Temperature_Sensor`
- `Leaving_Hot_Water_Temperature_Sensor`
- `Hot_Water_Supply_Temperature_Sensor`

**回水温度传感器 (任一):**
- `Return_Water_Temperature_Sensor`
- `Entering_Hot_Water_Temperature_Sensor`
- `Hot_Water_Return_Temperature_Sensor`

### 时序数据 (.csv)

必须包含以下Columns：
- `datetime_UTC`: 时间戳（ISO格式）
- `sup`: 供水温度（°C）
- `ret`: 回水温度（°C）

示例：
```csv
datetime_UTC,sup,ret,flow,hw
2018-01-01T08:00:00Z,58.9,57.7,17.9,91854.7
2018-01-01T09:00:00Z,59.2,57.9,17.9,100117.1
```

## 输出结果

### 统计文件 (CSV/JSON)

包含以下统计指标：
- `count`: 有效数据点数量
- `mean_temp_diff`: 平均温差
- `std_temp_diff`: 温差标准差
- `min_temp_diff`, `max_temp_diff`: 温差范围
- `median_temp_diff`: 中位数温差
- `q25_temp_diff`, `q75_temp_diff`: 第25和第75百分位数
- `mean_supply_temp`: 平均供水温度
- `mean_return_temp`: 平均回水温度
- `anomalies_below_threshold`: 低于阈值异常数量
- `anomalies_above_threshold`: 高于阈值异常数量
- `anomaly_rate`: 异常率（%）

### 时间序Columns文件 (CSV/JSON)

包含all时间点：
- 供水温度 (`sup`)
- 回水温度 (`ret`)
- 温差 (`temp_diff`)
- 小时、星期、月份etc.时间特征

### 可视化图表 (PNG/PDF/SVG)

1. **时间序Columns图**: 显示供水温度、回水温度和温差随时间变化
2. **分布图**: 温差直方图和箱线图
3. **按小时统计图**: 每小时平均温差柱状图

## 配置文件示例 (config.yaml)

```yaml
time_range:
  start_time: "2018-01-01"
  end_time: "2018-12-31"

analysis:
  resolution: "1H"
  threshold_min_delta: 1.0
  threshold_max_delta: 10.0

output:
  save_results: true
  output_dir: "./results"
  export_format: "csv"
  generate_plots: true
  plot_format: "png"
```

## 运行演示

我们提供了完整演示脚本：

```bash
python run_demo.py
```

这Map展示：
1. 最简单use方式
2. use自定义配置
3. 仅运行点位检测
4. 命令行use方式

## 运行测试

运行完整测试套件：

```bash
python test_app.py
```

测试包括：
- ✅ 点位检测功能
- ✅ 基本应用运行
- ✅ 输出文件生成
- ✅ 数据完整性验证
- ✅ 完整数据范围分析

## 目录结构

```
hhw_brick/
└── analytics/
    ├── core/
    │   ├── base_checker.py      # 基础点位检测器
    │   └── data_loader.py       # 数据加载器
    └── apps/
        └── secondary_loop_temp_diff/
            ├── app.py           # 主应用程序
            ├── checker.py       # 点位检测器
            ├── config.yaml      # 配置示例
            ├── README.md        # 本文档
            └── requirements.txt # 依赖Columns表
```

## 示例输出

```
============================================================
Secondary Loop Temperature Differential Analysis
Building ID: 29
============================================================
Total Data Points: 713
Mean Temperature Differential: 2.01 °C
Std Dev: 0.48 °C
Min: 0.89 °C
Max: 2.89 °C
Median: 2.22 °C

Mean Supply Temperature: 49.57 °C
Mean Return Temperature: 47.55 °C

Anomalies Below Threshold: 0
Anomalies Above Threshold: 0
Anomaly Rate: 0.00%
============================================================
```

## 故障排除

### 问题：找不to必需传感器

**解决方案**: 
- 确认 Brick 模型中包含供水和回水温度传感器
- 运行 checker 查看具体缺少哪些传感器
- 检查传感器类型是否在支持Columns表中

### 问题：时间范围过滤失败

**解决方案**:
- 确保时间格式为 ISO 格式（如 "2018-01-01"）
- 检查数据文件中时间Columns名是否为 `datetime_UTC`
- 确认时间范围在数据集范围内

### 问题：生成图表为空

**解决方案**:
- 检查过滤后数据是否为空
- 确认 `sup` 和 `ret` Columns包含有效数据
- 查看日志输出了解具体错误

## 许可证

与主项目相同

## 联系方式

如有问题or建议, 请联系项目维护者。

---

最后更新: 2025-10-23

