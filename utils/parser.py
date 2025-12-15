from bs4 import BeautifulSoup
from typing import List, Dict, Any

class HtmlParser:
    def parse_forum_page(self, html: str, site_domain: str = 'wm.wmhuu.com') -> List[Dict[str, str]]:
        """解析版块页面，提取帖子列表"""
        posts = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找帖子列表项 - 优化选择器，适配常见论坛结构
        post_items = []
        
        # 尝试多种常见的帖子列表选择器
        selectors = [
            '.forumbg li.row',  # phpBB论坛常见结构
            '.thread_list li',   # 常见线程列表
            '.topiclist.topics li',  # phpBB主题列表
            '#threadslist li',   # 另一种线程列表
            '.list_thread li',   # 列表线程结构
            'ul.topics li',      # 无序列表主题
            'table.forum-table tr',  # 表格结构
        ]
        
        for selector in selectors:
            items = soup.select(selector)
            if items:
                post_items = items
                break
        
        # 如果仍然没有找到，尝试查找所有包含标题链接的元素
        if not post_items:
            print("未找到标准帖子列表，尝试查找所有标题链接...")
            # 查找所有包含/viewtopic/的链接
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                if '/viewtopic/' in href:
                    title = link.get_text(strip=True)
                    if title and len(title) > 5:  # 过滤掉太短的标题
                        posts.append({
                            'title': title,
                            'url': href if href.startswith('http') else f'https://{site_domain}{href}'
                        })
            return posts
        
        for item in post_items:
            try:
                # 查找标题链接 - 优化选择器
                title_selectors = [
                    'a.topictitle',  # phpBB常见标题类
                    'a.threadtitle',  # 线程标题
                    'a[href*="viewtopic"]',  # 包含viewtopic的链接
                    '.topic-title a',  # 主题标题内的链接
                    '.thread-title a',  # 线程标题内的链接
                    'h3 a',  # h3标签内的链接
                    'h2 a',  # h2标签内的链接
                ]
                
                title_elem = None
                for selector in title_selectors:
                    elem = item.select_one(selector)
                    if elem:
                        title_elem = elem
                        break
                
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href')
                
                if url and title and '/viewtopic/' in url:
                    # 确保URL是完整的
                    if not url.startswith('http'):
                        url = f'https://{site_domain}{url}'
                    
                    posts.append({
                        'title': title,
                        'url': url
                    })
            except Exception as e:
                print(f"解析帖子项失败: {e}")
                continue
        
        return posts
    
    def parse_topic_page(self, html: str, crawl_mode: str, site_domain: str = 'wm.wmhuu.com') -> Dict[str, Any]:
        """解析帖子详情页，提取内容"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'content': '',
            'images': []
        }
        
        if crawl_mode == 'picture':
            # 图片模式：提取所有图片
            img_tags = []
            
            # 尝试多种图片选择器，优先选择帖子内容区域的图片
            content_selectors = [
                '.content',  # 常见内容区域
                '.postbody',  # phpBB帖子内容
                '.topic-content',  # 主题内容
                '.post-content',  # 帖子内容
                '.thread-content',  # 线程内容
                '#post_content',  # 帖子内容ID
                '.message-content',  # 消息内容
            ]
            
            content_found = False
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    img_tags = content_elem.find_all('img')
                    content_found = True
                    break
            
            # 如果没有找到特定内容区域，提取所有图片
            if not content_found:
                img_tags = soup.find_all('img')
            
            for img in img_tags:
                img_url = img.get('src')
                if img_url:
                    # 确保URL是完整的
                    if not img_url.startswith('http'):
                        if img_url.startswith('/'):
                            img_url = f'https://{site_domain}{img_url}'
                        else:
                            continue  # 跳过相对路径的图片
                    
                    # 过滤掉广告和小图标
                    if 'avatar' not in img_url.lower() and 'smiley' not in img_url.lower() and 'icon' not in img_url.lower():
                        result['images'].append(img_url)
        
        elif crawl_mode == 'novel':
            # 小说模式：提取正文内容
            content_elem = None
            
            # 尝试多种常见的内容选择器
            content_selectors = [
                '.postbody',  # phpBB帖子内容
                '.content',  # 常见内容区域
                '.topic-content',  # 主题内容
                '.post-content',  # 帖子内容
                '.thread-content',  # 线程内容
                '#post_content',  # 帖子内容ID
                '.message-content',  # 消息内容
                '.entry-content',  # 条目内容
                '.post-text',  # 帖子文本
                '.text',  # 文本内容
                '.message',  # 消息
            ]
            
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    content_elem = elem
                    break
            
            # 如果仍然没有找到，尝试查找包含大量文本的元素
            if not content_elem:
                print("未找到标准内容区域，尝试查找包含大量文本的元素...")
                # 查找所有段落和div元素，选择文本最多的那个
                candidates = soup.find_all(['div', 'p'])
                max_text_len = 0
                for candidate in candidates:
                    text = candidate.get_text(strip=True)
                    if len(text) > max_text_len and len(text) > 100:  # 至少100个字符
                        max_text_len = len(text)
                        content_elem = candidate
            
            if content_elem:
                # 移除图片等不需要的元素
                for img in content_elem.find_all('img'):
                    img.decompose()
                for script in content_elem.find_all('script'):
                    script.decompose()
                for style in content_elem.find_all('style'):
                    style.decompose()
                for ad in content_elem.find_all(['div', 'span'], class_=['ad', 'advertisement', 'ads']):
                    ad.decompose()
                
                content = content_elem.get_text(separator='\n', strip=True)
                result['content'] = content
        
        return result
    
    def has_next_page(self, html: str) -> bool:
        """检查是否有下一页"""
        soup = BeautifulSoup(html, 'html.parser')
        # 查找下一页按钮 - 优化选择器，适配多种分页结构
        next_page_selectors = [
            'a[rel="next"]',  # 标准rel属性
            '.next a',  # 下一页链接
            '.pagination a.next',  # 分页控件的下一页
            '.paging a.next',  # 另一种分页控件
            'a:contains(下一页)',  # 包含"下一页"文本的链接
            'a:contains(Next)',  # 英文下一页
            'a[href*="start="]',  # 包含start参数的链接
            'a[href*="page="]',  # 包含page参数的链接
        ]
        
        for selector in next_page_selectors:
            try:
                # 使用CSS选择器查找
                if 'contains' in selector:
                    # 处理:contains选择器（BeautifulSoup不直接支持）
                    text = selector.split(':contains(')[1].strip(')"\'')
                    next_links = soup.find_all('a', string=lambda s: text in s if s else False)
                    if next_links:
                        return True
                else:
                    next_page = soup.select_one(selector)
                    if next_page:
                        return True
            except Exception as e:
                continue
        
        return False
    
    def get_next_page_url(self, current_url: str, html: str, site_domain: str = 'wm.wmhuu.com') -> str:
        """获取下一页URL"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 尝试多种下一页选择器
        next_page_selectors = [
            'a[rel="next"]',  # 标准rel属性
            '.next a',  # 下一页链接
            '.pagination a.next',  # 分页控件的下一页
            '.paging a.next',  # 另一种分页控件
            'a:contains(下一页)',  # 包含"下一页"文本的链接
            'a:contains(Next)',  # 英文下一页
        ]
        
        next_page = None
        for selector in next_page_selectors:
            try:
                if 'contains' in selector:
                    # 处理:contains选择器（BeautifulSoup不直接支持）
                    text = selector.split(':contains(')[1].strip(')"\'')
                    next_links = soup.find_all('a', string=lambda s: text in s if s else False)
                    if next_links:
                        next_page = next_links[0]
                        break
                else:
                    next_page = soup.select_one(selector)
                    if next_page:
                        break
            except Exception as e:
                continue
        
        # 如果没有找到，尝试查找包含分页参数的链接
        if not next_page:
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href')
                if '/viewforum/' in href and ('start=' in href or 'page=' in href):
                    next_page = link
                    break
        
        if next_page:
            next_url = next_page.get('href')
            if next_url:
                # 确保URL是完整的
                if not next_url.startswith('http'):
                    if next_url.startswith('/'):
                        next_url = f'https://{site_domain}{next_url}'
                    else:
                        # 相对路径，基于当前URL构建
                        from urllib.parse import urljoin
                        next_url = urljoin(current_url, next_url)
                return next_url
        
        return ''