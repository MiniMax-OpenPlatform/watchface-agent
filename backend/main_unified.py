"""
统一服务入口 - 同时提供前端静态文件和后端API
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from main import app  # 导入原有的FastAPI应用

# 静态文件目录
STATIC_DIR = Path(__file__).parent / "static"

# 挂载静态文件目录 - 用于 /watch-agent/ 路径下的JS/CSS等资源
if STATIC_DIR.exists():
    app.mount("/watch-agent/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="watch-agent-assets")
    print(f"✅ 静态资源目录已挂载: /watch-agent/assets")

# 根路径重定向
from fastapi.responses import RedirectResponse

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    """根路径重定向到 /watch-agent/"""
    return RedirectResponse(url="/watch-agent/", status_code=301)

# 处理 /watch-agent/ 路径
@app.get("/watch-agent/")
async def serve_watchagent_index():
    """返回前端应用的 index.html"""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"error": "Frontend not found"}

# SPA 路由支持 - 所有 /watch-agent/* 路径都返回 index.html
@app.get("/watch-agent/{full_path:path}")
async def serve_watchagent_spa(full_path: str):
    """SPA 路由支持 - 优先返回文件，否则返回 index.html"""
    # 尝试返回实际文件
    file_path = STATIC_DIR / full_path
    if file_path.is_file():
        return FileResponse(file_path)
    
    # 如果不是文件，返回 index.html（SPA路由）
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    
    return {"error": "File not found"}

# 健康检查（覆盖原有的，提供更详细的信息）
@app.get("/health")
async def health_check_unified():
    """统一服务健康检查"""
    return {
        "status": "healthy",
        "service": "watchface-agent-unified",
        "frontend": STATIC_DIR.exists(),
        "backend": True
    }

print("🚀 统一服务启动:")
print(f"   前端访问: http://localhost:10031/watch-agent/")
print(f"   后端API: http://localhost:10031/api/")
print(f"   健康检查: http://localhost:10031/health")

