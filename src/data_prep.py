"""
数据预处理和统计工具
"""

import os
import csv
import json
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from collections import Counter


def load_annotations(csv_file):
    """加载标注数据"""
    annotations = []
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            annotations = list(reader)
    return annotations


def show_statistics(csv_file):
    """显示标注统计信息"""
    annotations = load_annotations(csv_file)

    if not annotations:
        print("没有找到标注数据")
        return

    # 统计类别分布
    labels = [ann['label'] for ann in annotations]
    label_counts = Counter(labels)
    total = len(annotations)

    print("=== 标注统计 ===")
    print(f"总图片数: {total}")

    for label, count in label_counts.items():
        percentage = count / total * 100
        print(f"{label}: {count} 张 ({percentage:.1f}%)")

    # 时间分布（按日期）
    dates = [ann['timestamp'][:10] for ann in annotations if 'timestamp' in ann]  # 取日期部分
    date_counts = Counter(dates)

    if date_counts:
        print(f"\n=== 标注进度（按日期） ===")
        for date, count in sorted(date_counts.items()):
            print(f"{date}: {count} 张")


def convert_to_json(csv_file, json_file):
    """转换为JSON格式"""
    annotations = load_annotations(csv_file)

    data = {
        "info": {
            "description": "猫狗分类标注数据",
            "version": "1.0",
            "contributor": "数据标注师"
        },
        "categories": [
            {"id": 0, "name": "cat"},
            {"id": 1, "name": "dog"}
        ],
        "images": [],
        "annotations": []
    }

    for i, ann in enumerate(annotations):
        # 图片信息
        image_info = {
            "id": i,
            "file_name": ann['filename'],
            "timestamp": ann.get('timestamp', '')
        }
        data["images"].append(image_info)

        # 标注信息
        category_id = 0 if ann['label'] == 'cat' else 1
        annotation = {
            "id": i,
            "image_id": i,
            "category_id": category_id
        }
        data["annotations"].append(annotation)

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"已转换为JSON格式: {json_file}")


def split_dataset(csv_file, train_ratio=0.8, val_ratio=0.1):
    """划分训练/验证/测试集"""
    annotations = load_annotations(csv_file)

    if not annotations:
        print("没有标注数据可以划分")
        return

    # 按类别分组
    cats = [ann for ann in annotations if ann['label'] == 'cat']
    dogs = [ann for ann in annotations if ann['label'] == 'dog']

    import random
    random.shuffle(cats)
    random.shuffle(dogs)

    # 计算划分点
    def split_data(data, train_r, val_r):
        n = len(data)
        train_n = int(n * train_r)
        val_n = int(n * val_r)

        return {
            'train': data[:train_n],
            'val': data[train_n:train_n + val_n],
            'test': data[train_n + val_n:]
        }

    cat_splits = split_data(cats, train_ratio, val_ratio)
    dog_splits = split_data(dogs, train_ratio, val_ratio)

    # 合并并保存
    splits = {}
    for split_name in ['train', 'val', 'test']:
        splits[split_name] = cat_splits[split_name] + dog_splits[split_name]
        random.shuffle(splits[split_name])

        # 保存到CSV
        output_file = f"./data/{split_name}.csv"
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if splits[split_name]:
                writer = csv.DictWriter(f, fieldnames=splits[split_name][0].keys())
                writer.writeheader()
                writer.writerows(splits[split_name])

        cat_count = len([x for x in splits[split_name] if x['label'] == 'cat'])
        dog_count = len([x for x in splits[split_name] if x['label'] == 'dog'])

        print(f"{split_name}: {len(splits[split_name])} 张 (猫:{cat_count}, 狗:{dog_count})")

    print("数据集划分完成！")


def generate_report(csv_file):
    """生成详细报告"""
    annotations = load_annotations(csv_file)

    if not annotations:
        print("没有数据生成报告")
        return

    report = {
        "总体统计": {},
        "类别分布": {},
        "时间分析": {}
    }

    # 总体统计
    total = len(annotations)
    labels = [ann['label'] for ann in annotations]
    label_counts = Counter(labels)

    report["总体统计"] = {
        "总图片数": total,
        "类别数": len(label_counts),
        "标注时间跨度": "待分析"
    }

    # 类别分布
    for label, count in label_counts.items():
        report["类别分布"][label] = {
            "数量": count,
            "占比": f"{count / total * 100:.1f}%"
        }

    # 保存报告
    with open("./data/annotation_report.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("报告已生成: ./data/annotation_report.json")

    # 打印摘要
    print("\n=== 项目摘要 ===")
    print(f"✅ 完成标注: {total} 张图片")
    print(f"📊 类别分布: ", end="")
    for label, count in label_counts.items():
        print(f"{label}({count}张) ", end="")
    print()


def main():
    parser = argparse.ArgumentParser(description="数据预处理工具")
    parser.add_argument("--input", default="./data/labels.csv", help="输入CSV文件")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--json", help="转换为JSON格式")
    parser.add_argument("--split", action="store_true", help="划分数据集")
    parser.add_argument("--report", action="store_true", help="生成报告")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"输入文件不存在: {args.input}")
        return

    if args.stats:
        show_statistics(args.input)

    if args.json:
        convert_to_json(args.input, args.json)

    if args.split:
        split_dataset(args.input)

    if args.report:
        generate_report(args.input)


if __name__ == "__main__":
    main()