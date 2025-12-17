import yaml
import argparse
import os
from utils.request import RequestHandler
from utils.parser import HtmlParser
from utils.saver import ContentSaver
from utils.git import GitManager

import threading
import time

def get_fastest_domain(domains):
    """简化版域名选择，直接返回第一个域名"""
    if not domains:
        return None
    
    # 简化处理，直接返回第一个域名，避免复杂的测速逻辑
    # 由于当前环境存在代理问题，暂时不进行域名测速
    fastest_domain = domains[0]
    print(f"\n使用配置的第一个域名: {fastest_domain}")
    return fastest_domain

def load_config(config_path: str = 'config.yaml') -> dict:
    """加载配置文件，从site_domain.yaml读取多个域名，选择最快的一个"""
    # 加载主配置文件
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 设置默认域名，防止config.yaml中没有配置
    default_domain = 'wm.wmhuu.com'
    if 'site_domain' not in config or config['site_domain'] is None:
        config['site_domain'] = default_domain
    
    # 尝试从site_domain.yaml读取多个域名
    try:
        with open('site_domain.yaml', 'r', encoding='utf-8') as f:
            site_config = yaml.safe_load(f)
        
        if site_config and 'site_domains' in site_config:
            domains = site_config['site_domains']
            # 选择最快的域名
            fastest_domain = get_fastest_domain(domains)
            
            if fastest_domain:
                # 更新config.yaml文件
                config['site_domain'] = fastest_domain
                print(f"更新config.yaml中的域名: {fastest_domain}")
                # 保存更新后的配置到文件
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            else:
                # 所有域名测试失败，使用默认域名
                print(f"所有域名测试失败，使用默认域名: {config['site_domain']}")
        elif site_config and 'site_domain' in site_config:
            # 兼容旧格式，单个域名
            config['site_domain'] = site_config['site_domain']
            print(f"从site_domain.yaml加载单个域名: {site_config['site_domain']}")
        else:
            # 没有找到域名配置，使用config.yaml中的域名
            print(f"使用config.yaml中的域名: {config['site_domain']}")
    except FileNotFoundError:
        # site_domain.yaml不存在，使用config.yaml中的域名
        print(f"site_domain.yaml不存在，使用config.yaml中的域名: {config['site_domain']}")
    except Exception as e:
        print(f"读取site_domain.yaml失败: {e}")
        print(f"使用config.yaml中的域名: {config['site_domain']}")
    
    return config

def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='wm.wmhuu.com爬虫程序')
    parser.add_argument('--mode', type=str, choices=['picture', 'novel', 'all'], default='all', help='采集模式：picture(图片)、novel(小说)或all(全部)')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    parser.add_argument('--daily', action='store_true', help='仅采集当日数据')
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 加载配置文件
    config = load_config(args.config)
    
    # 命令行参数覆盖配置
    if args.mode:
        config['crawl_mode'] = args.mode
    
    # 获取采集模式
    crawl_mode = config['crawl_mode']
    daily_mode = args.daily
    
    # 处理保存路径
    save_paths = config['save_paths'].copy()
    if daily_mode:
        # 生成当日日期目录名，格式：daily_YYYY-MM-DD
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')
        daily_prefix = f'daily_{current_date}'
        
        # 更新保存路径
        save_paths['picture'] = os.path.join(save_paths['picture'], daily_prefix)
        save_paths['novel'] = os.path.join(save_paths['novel'], daily_prefix)
    
    # 初始化组件
    request_handler = RequestHandler(
        headers=config['request']['headers'],
        timeout=config['request']['timeout'],
        delay=config['request']['delay'],
        retry_times=config['crawl']['retry_times'],
        proxies=config['request']['proxies']
    )
    
    parser = HtmlParser()
    saver = ContentSaver(save_paths)
    
    # 导入日期处理模块
    from datetime import datetime
    
    # 获取当前日期，格式：MM-DD
    current_date = datetime.now().strftime('%m-%d')
    
    def is_today_post(title):
        """判断帖子标题是否为当日发布"""
        import re
        # 匹配标题中的日期格式：[MM-DD]
        match = re.search(r'\[(\d{2}-\d{2})\]', title)
        if match:
            post_date = match.group(1)
            return post_date == current_date
        return False
    
    # 定义爬取单个模式的函数
    def crawl_single_mode(mode):
        """爬取单个模式"""
        print(f"\n===== 开始采集 {mode} 模式{'，仅采集当日数据' if daily_mode else ''} =====")
        print(f"当前日期：{current_date}")
        
        # 选择要爬取的版块
        if mode == 'picture':
            forums = config['picture_forums']
        else:
            forums = config['novel_forums']
        
        mode_topics = 0
        mode_saved = 0
        
        # 遍历每个版块
        for forum in forums:
            forum_id = forum['id']
            forum_name = forum['name']
            print(f"\n=== 开始爬取版块：{forum_name} (ID: {forum_id}) ===")
            
            # 使用配置文件中的域名
            site_domain = config['site_domain']
            forum_url = f'https://{site_domain}/viewforum/{forum_id}'
            current_page = 1
            
            # 遍历版块的所有页面
            while current_page <= config['crawl']['max_pages']:
                print(f"\n--- 第 {current_page} 页 ---")
                
                # 发送请求获取页面内容
                page_html = request_handler.get(forum_url)
                if not page_html:
                    print(f"获取页面失败：{forum_url}")
                    break
                
                # 解析帖子列表
                topics = parser.parse_forum_page(page_html, site_domain=site_domain)
                if not topics:
                    print(f"未找到帖子：{forum_url}")
                    break
                
                # 过滤当日帖子（如果是daily模式）
                if daily_mode:
                    filtered_topics = [topic for topic in topics if is_today_post(topic['title'])]
                    print(f"找到 {len(topics)} 个帖子，其中当日帖子 {len(filtered_topics)} 个")
                    topics = filtered_topics
                    if not topics:
                        print(f"本页没有当日帖子，继续下一页")
                        break
                else:
                    print(f"找到 {len(topics)} 个帖子")
                
                # 遍历每个帖子
                for topic in topics:
                    mode_topics += 1
                    print(f"\n处理帖子：{topic['title']}")
                    
                    # 获取帖子详情页内容
                    topic_html = request_handler.get(topic['url'])
                    if not topic_html:
                        print(f"获取帖子详情失败：{topic['url']}")
                        continue
                    
                    # 解析帖子内容
                    topic_content = parser.parse_topic_page(topic_html, mode, site_domain=site_domain)
                    
                    # 保存内容
                    if mode == 'picture':
                        # 保存图片
                        if topic_content['images']:
                            saved_count = saver.save_pictures(topic['title'], topic_content['images'], request_handler)
                            mode_saved += saved_count
                            print(f"帖子 {topic['title']} 保存了 {saved_count} 张图片")
                        else:
                            print(f"帖子 {topic['title']} 没有找到图片")
                    else:
                        # 保存小说
                        if topic_content['content']:
                            if saver.save_novel(topic['title'], topic_content['content']):
                                mode_saved += 1
                                print(f"小说 {topic['title']} 保存成功")
                            else:
                                print(f"小说 {topic['title']} 保存失败")
                        else:
                            print(f"帖子 {topic['title']} 没有找到小说内容")
                
                # 检查是否有下一页
                if parser.has_next_page(page_html):
                    next_url = parser.get_next_page_url(forum_url, page_html, site_domain=site_domain)
                    if next_url:
                        forum_url = next_url
                        current_page += 1
                    else:
                        break
                else:
                    break
        
        print(f"\n===== {mode} 模式采集完成 =====")
        print(f"{mode} 模式处理帖子：{mode_topics} 个")
        print(f"{mode} 模式保存内容：{mode_saved} 项")
        
        return mode_topics, mode_saved
    
    total_topics = 0
    total_saved = 0
    
    # 根据采集模式执行爬取
    if crawl_mode == 'all':
        # 爬取所有模式
        print(f"开始采集，模式：all{'，仅采集当日数据' if daily_mode else ''}")
        print(f"当日数据保存路径：{save_paths}")
        
        # 先爬取图片模式
        pic_topics, pic_saved = crawl_single_mode('picture')
        total_topics += pic_topics
        total_saved += pic_saved
        
        # 再爬取小说模式
        novel_topics, novel_saved = crawl_single_mode('novel')
        total_topics += novel_topics
        total_saved += novel_saved
    else:
        # 爬取单个模式
        print(f"开始采集，模式：{crawl_mode}{'，仅采集当日数据' if daily_mode else ''}")
        print(f"当日数据保存路径：{save_paths}")
        topics, saved = crawl_single_mode(crawl_mode)
        total_topics += topics
        total_saved += saved
    
    print(f"\n=== 全部采集完成 ===")
    print(f"总共处理帖子：{total_topics} 个")
    print(f"总共保存内容：{total_saved} 项")
    
    # 推送结果到远程仓库（如果配置了）
    if config.get('remote_repo', {}).get('enable', False):
        remote_config = config['remote_repo']
        remote_url = remote_config['url']
        branch = remote_config['branch']
        username = remote_config['username']
        email = remote_config['email']
        
        if remote_url:
            print(f"\n=== 开始推送结果到远程仓库 ===")
            git_manager = GitManager(username=username, email=email)
            
            # 要推送的文件列表
            files_to_push = ['./picture', './novel']
            
            # 生成提交信息
            commit_message = f"Crawl results: {crawl_mode} mode, daily={daily_mode}, total={total_saved}"
            
            # 推送结果
            success = git_manager.push_results(
                remote_url=remote_url,
                branch_name=branch,
                files=files_to_push,
                commit_message=commit_message,
                username=username,
                email=email
            )
            
            if success:
                print("=== 结果推送完成 ===")
            else:
                print("=== 结果推送失败 ===")
        else:
            print("=== 远程仓库 URL 未配置，跳过推送 ===")

if __name__ == '__main__':
    main()