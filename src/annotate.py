#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的猫狗分类标注工具
"""

import os
import csv
import cv2
import argparse
from pathlib import Path
import shutil


class SimpleAnnotator:
    def __init__(self, input_dir, output_csv):
        self.input_dir = Path(input_dir)
        self.output_csv = output_csv
        self.images = []
        self.annotations = []
        self.current_idx = 0

        # 获取项目根目录
        project_root = Path(__file__).parent.parent

        self.cats_dir = project_root / "data" / "cats"
        self.dogs_dir = project_root / "data" / "dogs"
        os.makedirs(self.cats_dir, exist_ok=True)
        os.makedirs(self.dogs_dir, exist_ok=True)

        # 加载图片
        self.load_images()

        # 加载已有标注
        self.load_existing_labels()

    def load_images(self):
        """加载图片文件"""
        extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        for ext in extensions:
            self.images.extend(list(self.input_dir.glob(f'*{ext}')))

        self.images = list(set(self.images))  # 去重
        self.images.sort()
        print(f"找到 {len(self.images)} 张图片")

    def load_existing_labels(self):
        """加载已有的标注文件"""
        if os.path.exists(self.output_csv):
            try:
                with open(self.output_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing = {row['filename']: row.get('label', '') for row in reader}
                    print(f"加载了 {len(existing)} 个已有标注")

                    # 过滤掉已标注的图片
                    self.images = [img for img in self.images if img.name not in existing]
                    print(f"剩余 {len(self.images)} 张待标注")
            except Exception as e:
                print(f"加载标注文件出错: {e}")

    def show_image(self, image_path):
        """显示图片"""
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"无法读取图片: {image_path}")
            return False

        # 调整图片大小
        height, width = img.shape[:2]
        max_height = 800
        if height > max_height:
            scale = max_height / height
            new_width = int(width * scale)
            img = cv2.resize(img, (new_width, max_height))

        cv2.namedWindow('Cat-Dog Annotation Tool')
        cv2.imshow('Cat-Dog Annotation Tool', img)
        cv2.waitKey(1)
        return True

    def delete_annotation(self, filename):
        """删除指定文件的标注和复制的图片"""
        if not os.path.exists(self.output_csv):
            return

        # 读取所有标注，过滤掉要删除的
        rows = []
        deleted_label = None
        with open(self.output_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['filename'] != filename:
                    rows.append(row)
                else:
                    deleted_label = row.get('label')

        # 重新写入CSV
        if rows:
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['filename', 'label', 'timestamp'])
                writer.writeheader()
                writer.writerows(rows)
        else:
            # 如果没有剩余数据，删除文件
            os.remove(self.output_csv)

        # 删除复制的图片
        if deleted_label:
            target_dir = self.cats_dir if deleted_label == 'cat' else self.dogs_dir
            img_path = target_dir / filename

            if img_path.exists():
                os.remove(img_path)
                print(f"已删除标注和图片: {filename}")

    def save_annotation(self, filename, label):
        """保存单个标注"""
        # 添加到CSV
        file_exists = os.path.exists(self.output_csv)
        with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['filename', 'label', 'timestamp'])

            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow([filename, label, timestamp])

        # 复制图片到对应目录
        source = self.input_dir / filename
        if label == 'cat':
            dest = self.cats_dir / filename
            shutil.copy2(source, dest)
        elif label == 'dog':
            dest = self.dogs_dir / filename
            shutil.copy2(source, dest)

        print(f"已标注: {filename} -> {label}")

    def start_annotation(self):
        """开始标注过程"""
        if not self.images:
            print("没有图片需要标注！")
            return

        print("开始标注...")
        print("操作说明:")
        print("  c - 标记为猫")
        print("  d - 标记为狗")
        print("  s - 跳过这张图片")
        print("  q - 退出标注")
        print("  a - 上一张")
        print()

        self.current_idx = 0

        while self.current_idx < len(self.images):
            current_image = self.images[self.current_idx]
            print(f"\n进度: {self.current_idx + 1}/{len(self.images)}")
            print(f"当前图片: {current_image.name}")

            if not self.show_image(current_image):
                self.current_idx += 1
                continue

            # 等待按键
            key = cv2.waitKey(0) & 0xFF

            if key == ord('c'):
                self.save_annotation(current_image.name, 'cat')
                self.current_idx += 1
            elif key == ord('d'):
                self.save_annotation(current_image.name, 'dog')
                self.current_idx += 1
            elif key == ord('s'):
                print(f"跳过: {current_image.name}")
                self.current_idx += 1
            elif key == ord('a') and self.current_idx > 0:
                # 返回上一张并删除标注
                self.current_idx -= 1
                prev_image = self.images[self.current_idx]
                self.delete_annotation(prev_image.name)
                print(f"已撤销: {prev_image.name}")
            elif key == ord('q'):
                break

        cv2.destroyAllWindows()
        print(f"\n标注完成！共处理 {self.current_idx} 张图片")
        self.show_stats()

    def show_stats(self):
        """显示标注统计"""
        if not os.path.exists(self.output_csv):
            return

        cat_count = dog_count = 0
        with open(self.output_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 打印一下看看实际的列名
                if cat_count == 0 and dog_count == 0:
                    print("CSV列名:", list(row.keys()))

                label = row.get('label', row.get('Label', ''))  # 兼容不同大小写
                if label == 'cat':
                    cat_count += 1
                elif label == 'dog':
                    dog_count += 1

        total = cat_count + dog_count
        print(f"\n=== 标注统计 ===")
        print(f"猫: {cat_count} 张 ({cat_count / total * 100:.1f}%)" if total > 0 else "猫: 0 张")
        print(f"狗: {dog_count} 张 ({dog_count / total * 100:.1f}%)" if total > 0 else "狗: 0 张")
        print(f"总计: {total} 张")


def main():
    parser = argparse.ArgumentParser(description="简单猫狗分类标注工具")
    parser.add_argument("--input", default="./data/raw_images", help="输入图片目录")
    parser.add_argument("--output", default="./data/labels.csv", help="输出CSV文件")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"输入目录不存在: {args.input}")
        return

    annotator = SimpleAnnotator(args.input, args.output)
    annotator.start_annotation()


if __name__ == "__main__":
    main()