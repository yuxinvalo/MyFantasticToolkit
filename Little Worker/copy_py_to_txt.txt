#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复制项目中的.py文件到Little Worker目录，并将后缀改为.txt
"""

import os
import shutil
from pathlib import Path

def copy_py_files_to_txt():
    """复制.py文件到Little Worker目录并改为.txt后缀"""
    # 源目录和目标目录
    source_dir = Path("d:/PycharmProjects/HSBCLittleWorker")
    target_dir = Path("d:/PycharmProjects/HSBCLittleWorker/Little Worker")
    
    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 需要排除的目录
    exclude_dirs = {
        "Little Worker",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "logs",
        "csv_data",
        "utils" # Little Worker目录下的utils已存在
    }
    
    copied_files = []
    
    def copy_py_files(src_path, dst_path):
        """递归复制.py文件"""
        for item in src_path.iterdir():
            if item.is_file() and item.suffix == '.py':
                # 创建对应的.txt文件
                relative_path = item.relative_to(source_dir)
                txt_file = dst_path / relative_path.with_suffix('.txt')
                
                # 确保目标目录存在
                txt_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件内容
                shutil.copy2(item, txt_file)
                copied_files.append(f"{relative_path} -> {txt_file.relative_to(target_dir)}")
                print(f"复制: {relative_path} -> {txt_file.relative_to(target_dir)}")
                
            elif item.is_dir() and item.name not in exclude_dirs:
                # 递归处理子目录
                copy_py_files(item, dst_path)
    
    print("开始复制.py文件到Little Worker目录...")
    copy_py_files(source_dir, target_dir)
    
    print(f"\n复制完成！共复制了 {len(copied_files)} 个文件:")
    for file_info in copied_files:
        print(f"  {file_info}")

import random

import time

def generate_custom_id():
    timestamp_hex = hex(int(time.time()))[2:]
    random_hex = ''.join([hex(random.randint(0, 15))[2:] for _ in range(20)])
    # 按特定格式组合
    return f"{timestamp_hex[:7]}_{random_hex[:4]}_{random_hex[4:8]}_{random_hex[8:]}"

if __name__ == "__main__":
    copy_py_files_to_txt()
    # custom_id = generate_custom_id()
    # print(custom_id)
