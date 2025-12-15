import requests
import time
import os
import warnings
from typing import Dict, Any, Optional

# 忽略SSL验证警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request is being made to host')
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

class RequestHandler:
    def __init__(self, headers: Dict[str, str], timeout: int = 10, delay: float = 1, retry_times: int = 3, proxies: Optional[Dict[str, str]] = None):
        self.headers = headers
        self.timeout = timeout
        self.delay = delay
        self.retry_times = retry_times
        
        # 构建代理字典，支持分别配置http和https代理
        self.proxies = {}
        if proxies:
            # 只使用非null的代理配置
            if proxies.get('http'):
                self.proxies['http'] = proxies['http']
            if proxies.get('https'):
                self.proxies['https'] = proxies['https']
        
        # 如果没有有效的代理配置，设置为None
        if not self.proxies:
            self.proxies = None
        
        # 清除可能影响请求的环境变量
        self._clear_proxy_env_vars()
    
    def _clear_proxy_env_vars(self):
        """清除可能影响请求的代理环境变量"""
        proxy_vars = [
            'http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 
            'ALL_PROXY', 'all_proxy', 'ftp_proxy', 'FTP_PROXY',
            'SOCKS_PROXY', 'socks_proxy', 'SOCKS5_PROXY', 'socks5_proxy'
        ]
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]
                print(f"已清除代理环境变量: {var}")
    
    def _force_disable_proxy(self):
        """强制禁用代理，确保不受系统设置影响"""
        # 清除代理环境变量
        self._clear_proxy_env_vars()
        
        # 确保请求库不使用任何代理
        import requests
        from urllib.request import getproxies
        
        # 打印当前代理设置，用于调试
        print(f"系统代理设置: {getproxies()}")
        
        # 确保requests库不使用代理
        session = requests.Session()
        session.trust_env = False
        session.proxies = {}
    
    def get(self, url: str) -> str:
        """发送GET请求，支持重试机制"""
        for i in range(self.retry_times):
            try:
                # 强制禁用代理，确保不受系统设置影响
                self._force_disable_proxy()
                
                # 使用Session对象
                session = requests.Session()
                # 强制不使用任何代理
                session.proxies = {}
                # 禁用SSL验证
                session.verify = False
                # 强制不信任环境变量
                session.trust_env = False
                
                response = session.get(
                    url, 
                    headers=self.headers, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                time.sleep(self.delay)  # 请求延迟
                return response.text
            except requests.exceptions.ProxyError as e:
                print(f"代理错误 {url}: {e}")
                print("将尝试不使用代理重试...")
                # 重试时不使用代理
                try:
                    session = requests.Session()
                    session.proxies = {}
                    session.verify = False
                    session.trust_env = False
                    
                    response = session.get(
                        url, 
                        headers=self.headers, 
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    time.sleep(self.delay)
                    return response.text
                except requests.RequestException as e2:
                    print(f"不使用代理重试失败: {e2}")
            except requests.RequestException as e:
                print(f"请求失败 {url}: {e}")
            except Exception as e:
                print(f"未知错误 {url}: {e}")
            
            if i < self.retry_times - 1:
                print(f"{i+1}/{self.retry_times} 重试中...")
                time.sleep(self.delay * 2)  # 重试延迟加倍
            else:
                print(f"{self.retry_times}次重试后仍失败，跳过此URL")
                return ""
    
    def download_file(self, url: str, save_path: str) -> bool:
        """下载文件"""
        for i in range(self.retry_times):
            try:
                # 强制禁用代理，确保不受系统设置影响
                self._force_disable_proxy()
                
                # 使用Session对象
                session = requests.Session()
                # 强制不使用任何代理
                session.proxies = {}
                # 禁用SSL验证
                session.verify = False
                # 强制不信任环境变量
                session.trust_env = False
                
                response = session.get(
                    url, 
                    headers=self.headers, 
                    timeout=self.timeout, 
                    stream=True
                )
                response.raise_for_status()
                
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                time.sleep(self.delay)
                return True
            except requests.exceptions.ProxyError as e:
                print(f"代理错误 {url}: {e}")
                print("将尝试不使用代理重试...")
                # 重试时不使用代理
                try:
                    session = requests.Session()
                    session.proxies = {}
                    session.verify = False
                    session.trust_env = False
                    
                    response = session.get(
                        url, 
                        headers=self.headers, 
                        timeout=self.timeout, 
                        stream=True
                    )
                    response.raise_for_status()
                    
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    time.sleep(self.delay)
                    return True
                except requests.RequestException as e2:
                    print(f"不使用代理重试失败: {e2}")
            except requests.RequestException as e:
                print(f"下载失败 {url}: {e}")
            except Exception as e:
                print(f"未知错误 {url}: {e}")
            
            if i < self.retry_times - 1:
                print(f"{i+1}/{self.retry_times} 重试中...")
                time.sleep(self.delay * 2)
            else:
                print(f"{self.retry_times}次重试后仍失败，跳过此文件")
                return False