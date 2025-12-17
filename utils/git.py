#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 操作工具类
用于管理爬虫结果的远程仓库推送
"""

import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GitManager:
    """Git 操作管理类"""
    
    def __init__(self, repo_path: str = '.', username: str = '', email: str = ''):
        """初始化 Git 管理器
        
        Args:
            repo_path: 仓库路径
            username: Git 用户名
            email: Git 邮箱
        """
        self.repo_path = repo_path
        self.username = username
        self.email = email
    
    def run_command(self, cmd: list, cwd: str = None) -> tuple:
        """运行 Git 命令
        
        Args:
            cmd: 命令列表
            cwd: 工作目录
            
        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        if not cwd:
            cwd = self.repo_path
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            logger.error(f"命令超时: {' '.join(cmd)}")
            return 1, '', 'Command timed out'
        except Exception as e:
            logger.error(f"命令执行失败: {' '.join(cmd)}，错误: {e}")
            return 1, '', str(e)
    
    def set_config(self) -> bool:
        """设置 Git 配置
        
        Returns:
            bool: 是否成功
        """
        if not self.username or not self.email:
            logger.warning("Git 用户名或邮箱未设置，跳过配置")
            return True
        
        # 设置全局配置
        code1, _, stderr1 = self.run_command(['git', 'config', '--global', 'user.name', self.username])
        code2, _, stderr2 = self.run_command(['git', 'config', '--global', 'user.email', self.email])
        
        if code1 == 0 and code2 == 0:
            logger.info(f"Git 配置已设置: {self.username} <{self.email}>")
            return True
        else:
            logger.error(f"Git 配置失败: {stderr1} {stderr2}")
            return False
    
    def add_remote(self, remote_name: str, remote_url: str) -> bool:
        """添加或更新远程仓库
        
        Args:
            remote_name: 远程仓库名称
            remote_url: 远程仓库 URL
            
        Returns:
            bool: 是否成功
        """
        # 检查远程仓库是否已存在
        code, stdout, _ = self.run_command(['git', 'remote'])
        
        if code != 0:
            logger.error("获取远程仓库列表失败")
            return False
        
        remotes = stdout.split() if stdout else []
        
        if remote_name in remotes:
            # 更新远程仓库 URL
            code, _, stderr = self.run_command(['git', 'remote', 'set-url', remote_name, remote_url])
            if code == 0:
                logger.info(f"已更新远程仓库 {remote_name} 的 URL 为 {remote_url}")
                return True
            else:
                logger.error(f"更新远程仓库 URL 失败: {stderr}")
                return False
        else:
            # 添加远程仓库
            code, _, stderr = self.run_command(['git', 'remote', 'add', remote_name, remote_url])
            if code == 0:
                logger.info(f"已添加远程仓库 {remote_name}: {remote_url}")
                return True
            else:
                logger.error(f"添加远程仓库失败: {stderr}")
                return False
    
    def checkout_branch(self, branch_name: str) -> bool:
        """切换或创建分支
        
        Args:
            branch_name: 分支名称
            
        Returns:
            bool: 是否成功
        """
        # 检查分支是否存在
        code, stdout, _ = self.run_command(['git', 'branch', '--list', branch_name])
        
        if branch_name in stdout:
            # 切换到已有分支
            code, _, stderr = self.run_command(['git', 'checkout', branch_name])
            if code == 0:
                logger.info(f"已切换到分支 {branch_name}")
                return True
            else:
                logger.error(f"切换到分支 {branch_name} 失败: {stderr}")
                return False
        else:
            # 创建并切换到新分支
            code, _, stderr = self.run_command(['git', 'checkout', '-b', branch_name])
            if code == 0:
                logger.info(f"已创建并切换到分支 {branch_name}")
                return True
            else:
                logger.error(f"创建分支 {branch_name} 失败: {stderr}")
                return False
    
    def add_files(self, files: list) -> bool:
        """添加文件到暂存区
        
        Args:
            files: 文件列表
            
        Returns:
            bool: 是否成功
        """
        if not files:
            logger.warning("没有文件需要添加")
            return True
        
        code, _, stderr = self.run_command(['git', 'add'] + files)
        
        if code == 0:
            logger.info(f"已添加文件: {', '.join(files)}")
            return True
        else:
            logger.error(f"添加文件失败: {stderr}")
            return False
    
    def commit(self, message: str) -> bool:
        """提交更改
        
        Args:
            message: 提交信息
            
        Returns:
            bool: 是否成功
        """
        code, stdout, stderr = self.run_command(['git', 'commit', '-m', message])
        
        if code == 0:
            logger.info(f"提交成功: {message}")
            return True
        elif "nothing to commit" in stderr or "nothing to commit" in stdout:
            logger.info("没有更改需要提交")
            return True
        else:
            logger.error(f"提交失败: {stderr}")
            return False
    
    def push(self, remote_name: str, branch_name: str, force: bool = False) -> bool:
        """推送更改到远程仓库
        
        Args:
            remote_name: 远程仓库名称
            branch_name: 分支名称
            force: 是否强制推送
            
        Returns:
            bool: 是否成功
        """
        cmd = ['git', 'push', '-u', remote_name, branch_name]
        if force:
            cmd.append('--force')
        
        code, _, stderr = self.run_command(cmd)
        
        if code == 0:
            logger.info(f"已推送更改到 {remote_name}/{branch_name}")
            return True
        else:
            logger.error(f"推送失败: {stderr}")
            return False
    
    def push_results(self, remote_url: str, branch_name: str, files: list, commit_message: str, 
                     username: str = '', email: str = '') -> bool:
        """推送爬虫结果到远程仓库
        
        Args:
            remote_url: 远程仓库 URL
            branch_name: 分支名称
            files: 要推送的文件列表
            commit_message: 提交信息
            username: Git 用户名
            email: Git 邮箱
            
        Returns:
            bool: 是否成功
        """
        logger.info(f"开始推送结果到远程仓库: {remote_url}")
        
        # 设置 Git 用户名和邮箱
        if username and email:
            self.username = username
            self.email = email
            if not self.set_config():
                return False
        
        # 添加或更新远程仓库
        if not self.add_remote('origin', remote_url):
            return False
        
        # 切换或创建分支
        if not self.checkout_branch(branch_name):
            return False
        
        # 添加文件到暂存区
        if not self.add_files(files):
            return False
        
        # 提交更改
        if not self.commit(commit_message):
            return False
        
        # 推送更改
        if not self.push('origin', branch_name, force=True):
            return False
        
        logger.info("结果推送完成")
        return True
