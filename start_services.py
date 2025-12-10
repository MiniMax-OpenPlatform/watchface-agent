#!/usr/bin/env python3
"""
启动WatchFace Code Agent服务
"""
import subprocess
import sys
import time
import os
import signal

def start_backend():
    """启动后端服务"""
    print("🚀 Starting Backend on port 10020...")
    
    os.chdir("/home/moshu/my_proj/watch_agent_cd/backend")
    
    # 设置环境变量
    env = os.environ.copy()
    env["MINIMAX_BASE_URL"] = "https://api.minimaxi.com/v1"
    env["MINIMAX_API_KEY"] = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiLpmYjlh6_lroEiLCJVc2VyTmFtZSI6IumZiOWHr-WugSIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxODM2NzAyODA4NzMzMTI3MDU3IiwiUGhvbmUiOiIxNTg4OTcyOTA0MSIsIkdyb3VwSUQiOiIxODM2NzAyODA4NzI0NzM4NDQ5IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjUtMDgtMTQgMDE6NTU6MDAiLCJUb2tlblR5cGUiOjEsImlzcyI6Im1pbmltYXgifQ.PyP-etho9FgXJD3JwFpY3RezRug_bFmEA-FeicIEpLGocUVQZyPnbtuXrYbAlZD8x25TC2x3MhHkhvYFeP9Ap7JOdBRPPJ-na2hDMEXMTje9yPmQPvdKp7U7VQwSweVNMKreUzU6K0k6l92TN6IwL3Sq9KmNgfJF5P6mvA5j1ooVK0MKKz7AqX9RqjvhN4iNUpR76z3qpOVSLfZb00_kWoNIy9_v3tI-w8K5M_MMd4nzETzIem9I8jMUNx4ChX4Bs_5AVAs5X9Dxy_9Z9X21i4fIKY8OzbWXM_vas1rYQBgtTt2vJ4UW6LKhEyG-6TKG7RlSKqChEB46T-FElP2-xw"
    env["BACKEND_PORT"] = "10020"
    
    # 启动uvicorn
    cmd = ["venv/bin/python3", "main.py"]
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return process

def start_frontend():
    """启动前端服务"""
    print("\n🚀 Starting Frontend on port 10021...")
    
    os.chdir("/home/moshu/my_proj/watch_agent_cd/frontend")
    
    cmd = ["npm", "run", "dev"]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    return process

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 WatchFace Code Agent - Starting Services")
    print("=" * 60)
    
    backend_process = None
    frontend_process = None
    
    try:
        # 启动后端
        backend_process = start_backend()
        print(f"✅ Backend process started (PID: {backend_process.pid})")
        
        # 等待后端启动
        print("⏳ Waiting for backend to start...")
        time.sleep(5)
        
        # 检查后端是否运行
        if backend_process.poll() is not None:
            print("❌ Backend failed to start!")
            print("\n=== Backend Output ===")
            print(backend_process.stdout.read())
            return 1
        
        print("✅ Backend is running")
        print(f"   API: http://localhost:10020")
        print(f"   Docs: http://localhost:10020/docs")
        
        # 启动前端
        frontend_process = start_frontend()
        print(f"✅ Frontend process started (PID: {frontend_process.pid})")
        
        print("\n" + "=" * 60)
        print("🎉 All services are running!")
        print("=" * 60)
        print(f"📱 Frontend: http://10.11.17.19:10021")
        print(f"🔧 Backend API: http://10.11.17.19:10020")
        print(f"📚 API Docs: http://10.11.17.19:10020/docs")
        print("\nPress Ctrl+C to stop all services...")
        print("=" * 60)
        
        # 实时显示日志
        while True:
            # 显示后端日志
            if backend_process.stdout:
                line = backend_process.stdout.readline()
                if line:
                    print(f"[Backend] {line.rstrip()}")
            
            # 显示前端日志
            if frontend_process.stdout:
                line = frontend_process.stdout.readline()
                if line:
                    print(f"[Frontend] {line.rstrip()}")
            
            # 检查进程是否还在运行
            if backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly!")
                break
            
            if frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly!")
                break
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down services...")
        
    finally:
        # 清理进程
        if backend_process:
            print("Stopping backend...")
            backend_process.terminate()
            backend_process.wait(timeout=5)
            print("✅ Backend stopped")
        
        if frontend_process:
            print("Stopping frontend...")
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
            print("✅ Frontend stopped")
        
        print("\n👋 All services stopped. Goodbye!")

if __name__ == "__main__":
    sys.exit(main())

