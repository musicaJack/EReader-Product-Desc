#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片优化脚本 - 用于移动端快速加载
优化imgs目录下的所有图片，压缩文件大小同时保持可接受的视觉质量
"""

import os
from PIL import Image
import sys

def optimize_image(input_path, output_path=None, max_width=1200, jpeg_quality=85, png_optimize=True):
    """
    优化单张图片
    
    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径（如果为None，则覆盖原文件）
        max_width: 最大宽度（像素），超过此宽度会按比例缩小
        jpeg_quality: JPEG质量（1-100，85为推荐值）
        png_optimize: 是否优化PNG（会稍微增加处理时间）
    
    返回:
        (success, original_size, new_size) 元组
    """
    try:
        # 在打开前记录原始大小
        original_size = os.path.getsize(input_path)
        original_width, original_height = Image.open(input_path).size
        
        # 打开图片
        img = Image.open(input_path)
        original_format = img.format
        
        # 转换为RGB模式（如果不是的话）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 如果有透明通道，需要特殊处理
            if img.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
                img = background
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 如果图片宽度超过max_width，按比例缩小
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            print(f"  尺寸调整: {img.width}x{img.height} (原始: {original_width}x{original_height})")
        
        # 确定输出路径
        if output_path is None:
            output_path = input_path
        
        # 确定输出格式
        if output_path.lower().endswith('.png'):
            output_format = 'PNG'
            # PNG优化
            if png_optimize:
                # 转换为RGB（PNG通常更大，转为JPEG会更小）
                # 但这里保持PNG格式
                img.save(output_path, 'PNG', optimize=True, compress_level=9)
            else:
                img.save(output_path, 'PNG')
        else:
            # 默认保存为JPEG（文件更小）
            if not output_path.lower().endswith(('.jpg', '.jpeg')):
                output_path = os.path.splitext(output_path)[0] + '.jpg'
            output_format = 'JPEG'
            img.save(output_path, 'JPEG', quality=jpeg_quality, optimize=True)
        
        new_size = os.path.getsize(output_path)
        compression_ratio = (1 - new_size / original_size) * 100 if original_size > 0 else 0
        
        print(f"  ✓ 优化完成: {os.path.basename(output_path)}")
        print(f"    格式: {output_format}")
        print(f"    原始大小: {original_size / 1024:.2f} KB")
        print(f"    优化后: {new_size / 1024:.2f} KB")
        print(f"    压缩率: {compression_ratio:.1f}%")
        
        return True, original_size, new_size
        
    except Exception as e:
        print(f"  ✗ 处理失败: {str(e)}")
        return False, 0, 0

def optimize_directory(directory='imgs', output_dir=None, max_width=1200, jpeg_quality=85, png_optimize=True):
    """
    优化目录下的所有图片
    
    参数:
        directory: 图片目录路径
        output_dir: 输出目录（如果为None，则覆盖原文件）
        max_width: 最大宽度（像素）
        jpeg_quality: JPEG质量
        png_optimize: 是否优化PNG
    """
    if not os.path.exists(directory):
        print(f"错误: 目录 '{directory}' 不存在")
        return
    
    # 支持的图片格式
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
    
    # 获取所有图片文件
    image_files = [f for f in os.listdir(directory) 
                   if os.path.isfile(os.path.join(directory, f)) 
                   and f.lower().endswith(supported_formats)]
    
    if not image_files:
        print(f"在目录 '{directory}' 中未找到图片文件")
        return
    
    print(f"找到 {len(image_files)} 张图片，开始优化...")
    print(f"设置: 最大宽度={max_width}px, JPEG质量={jpeg_quality}, PNG优化={'开启' if png_optimize else '关闭'}")
    print("-" * 60)
    
    success_count = 0
    total_original_size = 0
    total_new_size = 0
    
    for image_file in image_files:
        input_path = os.path.join(directory, image_file)
        print(f"\n处理: {image_file}")
        
        # 在优化前记录原始大小
        original_size = os.path.getsize(input_path)
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, image_file)
        else:
            output_path = None  # 覆盖原文件
        
        result = optimize_image(input_path, output_path, max_width, jpeg_quality, png_optimize)
        if result[0]:  # success
            success_count += 1
            total_original_size += result[1]  # original_size
            total_new_size += result[2]  # new_size
    
    print("\n" + "=" * 60)
    print(f"优化完成!")
    print(f"成功处理: {success_count}/{len(image_files)} 张图片")
    if success_count > 0:
        total_saved = total_original_size - total_new_size
        total_compression = (1 - total_new_size / total_original_size) * 100 if total_original_size > 0 else 0
        print(f"总大小: {total_original_size / 1024 / 1024:.2f} MB → {total_new_size / 1024 / 1024:.2f} MB")
        print(f"节省空间: {total_saved / 1024 / 1024:.2f} MB ({total_compression:.1f}%)")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='优化图片以适合移动端快速加载')
    parser.add_argument('--dir', '-d', default='imgs', help='图片目录路径（默认: imgs）')
    parser.add_argument('--output', '-o', default=None, help='输出目录（默认: 覆盖原文件）')
    parser.add_argument('--max-width', '-w', type=int, default=1200, help='最大宽度（像素，默认: 1200）')
    parser.add_argument('--quality', '-q', type=int, default=85, help='JPEG质量 1-100（默认: 85）')
    parser.add_argument('--no-png-optimize', action='store_true', help='禁用PNG优化')
    
    args = parser.parse_args()
    
    # 验证参数
    if not (1 <= args.quality <= 100):
        print("错误: JPEG质量必须在1-100之间")
        sys.exit(1)
    
    optimize_directory(
        directory=args.dir,
        output_dir=args.output,
        max_width=args.max_width,
        jpeg_quality=args.quality,
        png_optimize=not args.no_png_optimize
    )

if __name__ == '__main__':
    main()

