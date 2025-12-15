import os
from pathlib import Path
from typing import List

class ContentSaver:
    def __init__(self, save_paths: dict):
        self.save_paths = save_paths
        # 创建保存目录
        for path in save_paths.values():
            os.makedirs(path, exist_ok=True)
    
    def save_pictures(self, topic_title: str, images: List[str], request_handler) -> int:
        """保存图片到指定目录"""
        # 清理标题中的非法字符
        safe_title = self._sanitize_filename(topic_title)
        # 创建帖子目录
        topic_dir = os.path.join(self.save_paths['picture'], safe_title)
        os.makedirs(topic_dir, exist_ok=True)
        
        saved_count = 0
        for i, img_url in enumerate(images):
            try:
                # 获取图片扩展名
                ext = img_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                    ext = 'jpg'  # 默认扩展名
                
                # 构建保存路径
                img_name = f'image_{i+1}.{ext}'
                save_path = os.path.join(topic_dir, img_name)
                
                # 下载图片
                if request_handler.download_file(img_url, save_path):
                    saved_count += 1
                    print(f"已保存图片: {save_path}")
            except Exception as e:
                print(f"保存图片失败 {img_url}: {e}")
                continue
        
        return saved_count
    
    def save_novel(self, topic_title: str, content: str) -> bool:
        """保存小说内容到文本文件"""
        # 清理标题中的非法字符
        safe_title = self._sanitize_filename(topic_title)
        # 构建保存路径
        save_path = os.path.join(self.save_paths['novel'], f'{safe_title}.txt')
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已保存小说: {save_path}")
            return True
        except Exception as e:
            print(f"保存小说失败: {e}")
            return False
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """清理文件名中的非法字符"""
        # Windows 非法字符
        invalid_chars = '<>:"/\\|?*'
        # 替换非法字符为下划线
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # 移除不可打印字符
        filename = ''.join(c for c in filename if c.isprintable())
        # 截断过长的文件名
        return filename[:255]