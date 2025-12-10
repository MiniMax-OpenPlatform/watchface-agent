#!/usr/bin/env python3
"""
快速重启服务脚本
"""
import subprocess
import time
import sys
import os

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 or "no process found" in result.stderr.lower():
            print(f"✅ {description} - 完成")
            return True
        else:
            print(f"⚠️  {description} - {result.stderr[:100]}")
            return True  # 继续执行
    except Exception as e:
        print(f"❌ {description} - 错误: {e}")
        return False

def main():
    print("=" * 60)
    print("🔄 重启 WatchFace Code Agent 服务")
    print("=" * 60)
    print()
    
    # 1. 停止现有服务
    print("📛 步骤1: 停止现有服务")
    print("-" * 60)
    
    run_command("pkill -f 'python3 main.py'", "停止后端服务")
    run_command("pkill -f 'python3 start_services.py'", "停止启动脚本")
    run_command("pkill -f 'vite'", "停止前端服务")
    run_command("pkill -f 'npm run dev'", "停止npm进程")
    
    print()
    print("⏳ 等待进程完全停止...")
    time.sleep(3)
    print()
    
    # 2. 检查端口
    print("🔍 步骤2: 检查端口状态")
    print("-" * 60)
    
    result = subprocess.run("lsof -i :10020 2>/dev/null || echo 'Port 10020 is free'", 
                          shell=True, capture_output=True, text=True)
    print(f"后端端口 10020: {result.stdout.strip()}")
    
    result = subprocess.run("lsof -i :10021 2>/dev/null || echo 'Port 10021 is free'", 
                          shell=True, capture_output=True, text=True)
    print(f"前端端口 10021: {result.stdout.strip()}")
    print()
    
    # 3. 启动服务
    print("🚀 步骤3: 启动服务")
    print("-" * 60)
    print()
    
    # 改变到项目目录
    os.chdir('/home/moshu/my_proj/watch_agent_cd')
    
    print("正在启动服务...")
    print("提示: 服务将在后台运行")
    print()
    print("📝 启动命令:")
    print("   cd /home/moshu/my_proj/watch_agent_cd")
    print("   python3 start_services.py")
    print()
    
    # 使用nohup启动
    try:
        subprocess.Popen(
            ['python3', 'start_services.py'],
            stdout=open('service_output.log', 'w'),
            stderr=subprocess.STDOUT,
            cwd='/home/moshu/my_proj/watch_agent_cd'
        )
        print("✅ 服务启动命令已执行")
        print()
        time.sleep(5)
        
        # 检查是否启动成功
        result = subprocess.run("ps aux | grep 'python3 start_services.py' | grep -v grep", 
                              shell=True, capture_output=True, text=True)
        if result.stdout:
            print("✅ 服务已启动!")
            print()
            print("📋 进程信息:")
            print(result.stdout[:200])
        else:
            print("⚠️  服务可能没有启动成功")
            print("请手动运行: python3 start_services.py")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print()
        print("请手动启动服务:")
        print("  cd /home/moshu/my_proj/watch_agent_cd")
        print("  python3 start_services.py")
        return 1
    
    print()
    print("=" * 60)
    print("🎉 重启流程完成!")
    print("=" * 60)
    print()
    print("📱 访问地址:")
    print("   前端: http://10.11.17.19:10021")
    print("   后端: http://10.11.17.19:10020")
    print("   API文档: http://10.11.17.19:10020/docs")
    print()
    print("📋 查看日志:")
    print("   tail -f /home/moshu/my_proj/watch_agent_cd/logs/backend.log")
    print("   tail -f /home/moshu/my_proj/watch_agent_cd/service_output.log")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

