猫狗图像分类标注项目

简单实用的猫狗二分类图像标注工具，支持快捷键操作、数据统计和格式转换。

项目结构
cat-dog-classification/
├── README.md
├── data/
│   ├── raw_images/      # 【放原始图片到这里】
│   ├── cats/            # 标注后的猫图片
│   ├── dogs/            # 标注后的狗图片
│   └── labels.csv       # 标注结果
└── src/
    ├── annotate.py      # 标注工具源码
    └── data_prep.py     # 数据处理源码

1. 准备图片

把要标注的图片放到 `data/raw_images/` 目录

2. 开始标注

python src/annotate.py

**操作说明**：
C 标记为猫
D 标记为狗
S 跳过当前图片
A 返回上一张（会撤销标注）
Q 退出程序

3. 查看统计
python src/data_prep.py --stats

功能特性

快捷键标注：单键操作，效率高
撤销功能：支持返回修改
数据统计：实时查看标注进度
格式转换：支持CSV、JSON格式
数据集划分：自动划分训练/验证/测试集

高级功能

转换为JSON格式

python src/data_prep.py --json data/labels.json

划分数据集

python src/data_prep.py --split
生成 train.csv, val.csv, test.csv（8:1:1比例）

生成详细报告

python src/data_prep.py --report
生成 annotation_report.json

项目特点

简单易用：界面直观，操作方便
质量保证：支持撤销修改，避免误操作
数据规范：标准CSV格式，便于后续使用
功能完整：标注、统计、转换一站式解决

技术栈

Python 3.x
OpenCV：图像显示和处理
Pandas：数据处理
CSV：数据存储

标注示例

当前进度：15/20
文件名：cat_001.jpg
按 C 标记为猫 ✓
图片自动移动到 data/cats/ 目录


常见问题
Q: 标注错了怎么办?
A: 按 A 键返回上一张，会自动撤销标注

Q: 支持哪些图片格式？
A: 支持 .jpg, .jpeg, .png, .bmp

Q: 数据保存在哪？
A: 标注结果保存在 `data/labels.csv`，图片分类保存在 `data/cats/` 和 `data/dogs/`

项目亮点

效率提升：键盘快捷操作，比手工分类快3倍以上
数据完整：包含文件名、标签、时间戳等信息
灵活导出：支持多种数据格式转换
用户友好：支持撤销、跳过等人性化功能