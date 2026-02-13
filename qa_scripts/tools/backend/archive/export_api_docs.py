"""
API 文档导出脚本

导出 FastAPI 应用的 OpenAPI 规范文档

使用方法：
    python qa_scripts/tools/backend/archive/export_api_docs.py                    # 导出 JSON
    python qa_scripts/tools/backend/archive/export_api_docs.py --format markdown  # 导出 Markdown
    python qa_scripts/tools/backend/archive/export_api_docs.py --format both      # 导出两种格式
    python qa_scripts/tools/backend/archive/export_api_docs.py --output ./docs    # 指定输出目录
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "backend" / "app").exists():
    project_root = project_root.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))


def get_openapi_schema() -> Dict[str, Any]:
    """
    从 FastAPI 应用获取 OpenAPI schema
    """
    from app.main import app
    return app.openapi()


def export_json(schema: Dict[str, Any], output_dir: Path) -> str:
    """
    导出 OpenAPI JSON 文件
    
    Args:
        schema: OpenAPI schema 字典
        output_dir: 输出目录
        
    Returns:
        str: 输出文件路径
    """
    output_file = output_dir / "openapi.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)
    
    return str(output_file)


def export_markdown(schema: Dict[str, Any], output_dir: Path) -> str:
    """
    导出 API 文档为 Markdown 格式
    
    Args:
        schema: OpenAPI schema 字典
        output_dir: 输出目录
        
    Returns:
        str: 输出文件路径
    """
    output_file = output_dir / "api-documentation.md"
    
    lines: List[str] = []
    
    # 文档头部
    info = schema.get("info", {})
    lines.append(f"# {info.get('title', 'API Documentation')}")
    lines.append("")
    lines.append(f"> 版本: {info.get('version', '1.0.0')}")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    if info.get("description"):
        lines.append(f"{info.get('description')}")
        lines.append("")
    
    # 服务器信息
    servers = schema.get("servers", [])
    if servers:
        lines.append("## 服务器")
        lines.append("")
        for server in servers:
            lines.append(f"- **{server.get('description', 'Server')}**: `{server.get('url', '')}`")
        lines.append("")
    
    # 认证方式
    security_schemes = schema.get("components", {}).get("securitySchemes", {})
    if security_schemes:
        lines.append("## 认证方式")
        lines.append("")
        for name, scheme in security_schemes.items():
            scheme_type = scheme.get("type", "")
            if scheme_type == "http":
                lines.append(f"- **{name}**: HTTP {scheme.get('scheme', '')} 认证")
            elif scheme_type == "apiKey":
                lines.append(f"- **{name}**: API Key ({scheme.get('in', '')})")
            elif scheme_type == "oauth2":
                lines.append(f"- **{name}**: OAuth 2.0")
        lines.append("")
    
    # API 端点
    paths = schema.get("paths", {})
    tags_map: Dict[str, List[Dict[str, Any]]] = {}
    
    # 按标签分组
    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                tags = details.get("tags", ["未分类"])
                for tag in tags:
                    if tag not in tags_map:
                        tags_map[tag] = []
                    tags_map[tag].append({
                        "path": path,
                        "method": method.upper(),
                        "details": details
                    })
    
    lines.append("## API 端点")
    lines.append("")
    
    # 生成接口表格
    lines.append("### 接口列表")
    lines.append("")
    lines.append("| 方法 | 路径 | 描述 | 标签 |")
    lines.append("|------|------|------|------|")
    
    for tag, endpoints in tags_map.items():
        for ep in endpoints:
            summary = ep["details"].get("summary", "")
            lines.append(f"| `{ep['method']}` | `{ep['path']}` | {summary} | {tag} |")
    
    lines.append("")
    
    # 按标签详细描述
    for tag, endpoints in tags_map.items():
        lines.append(f"### {tag}")
        lines.append("")
        
        for ep in endpoints:
            details = ep["details"]
            summary = details.get("summary", "")
            description = details.get("description", "")
            
            lines.append(f"#### {ep['method']} {ep['path']}")
            lines.append("")
            lines.append(f"**{summary}**")
            lines.append("")
            
            if description and description != summary:
                lines.append(f"{description}")
                lines.append("")
            
            # 参数
            parameters = details.get("parameters", [])
            if parameters:
                lines.append("**参数:**")
                lines.append("")
                lines.append("| 名称 | 位置 | 类型 | 必填 | 描述 |")
                lines.append("|------|------|------|------|------|")
                for param in parameters:
                    name = param.get("name", "")
                    location = param.get("in", "")
                    required = "是" if param.get("required", False) else "否"
                    param_schema = param.get("schema", {})
                    param_type = param_schema.get("type", "string")
                    desc = param.get("description", "")
                    lines.append(f"| `{name}` | {location} | {param_type} | {required} | {desc} |")
                lines.append("")
            
            # 请求体
            request_body = details.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})
                if "application/json" in content:
                    json_schema = content["application/json"].get("schema", {})
                    ref = json_schema.get("$ref", "")
                    if ref:
                        schema_name = ref.split("/")[-1]
                        lines.append(f"**请求体:** `{schema_name}`")
                        lines.append("")
            
            # 响应
            responses = details.get("responses", {})
            if responses:
                lines.append("**响应:**")
                lines.append("")
                for code, response in responses.items():
                    desc = response.get("description", "")
                    lines.append(f"- `{code}`: {desc}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
    
    # 数据模型
    schemas = schema.get("components", {}).get("schemas", {})
    if schemas:
        lines.append("## 数据模型")
        lines.append("")
        
        for name, model in schemas.items():
            lines.append(f"### {name}")
            lines.append("")
            
            model_type = model.get("type", "object")
            description = model.get("description", "")
            
            if description:
                lines.append(f"{description}")
                lines.append("")
            
            properties = model.get("properties", {})
            required = model.get("required", [])
            
            if properties:
                lines.append("| 字段 | 类型 | 必填 | 描述 |")
                lines.append("|------|------|------|------|")
                for prop_name, prop_schema in properties.items():
                    prop_type = prop_schema.get("type", "any")
                    if "$ref" in prop_schema:
                        prop_type = prop_schema["$ref"].split("/")[-1]
                    prop_required = "是" if prop_name in required else "否"
                    prop_desc = prop_schema.get("description", "")
                    lines.append(f"| `{prop_name}` | {prop_type} | {prop_required} | {prop_desc} |")
                lines.append("")
    
    # 写入文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return str(output_file)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="导出 FastAPI 应用的 API 文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python qa_scripts/tools/backend/archive/export_api_docs.py                        # 导出 JSON 到 backend 目录
    python qa_scripts/tools/backend/archive/export_api_docs.py --format markdown      # 导出 Markdown
    python qa_scripts/tools/backend/archive/export_api_docs.py --format both          # 导出两种格式
    python qa_scripts/tools/backend/archive/export_api_docs.py --output ./docs        # 指定输出目录
        """
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "both"],
        default="json",
        help="输出格式: json, markdown, 或 both (默认: json)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出目录 (默认: backend 目录)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细信息"
    )
    
    args = parser.parse_args()
    
    # 确定输出目录
    if args.output:
        output_dir = Path(args.output).resolve()
    else:
        output_dir = backend_dir
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("📄 正在获取 OpenAPI schema...")
    
    try:
        schema = get_openapi_schema()
        
        if args.verbose:
            info = schema.get("info", {})
            print(f"   标题: {info.get('title', 'N/A')}")
            print(f"   版本: {info.get('version', 'N/A')}")
            print(f"   路径数: {len(schema.get('paths', {}))}")
            print(f"   模型数: {len(schema.get('components', {}).get('schemas', {}))}")
        
        # 导出文件
        exported_files = []
        
        if args.format in ["json", "both"]:
            json_file = export_json(schema, output_dir)
            exported_files.append(json_file)
            print(f"✅ JSON 文档已导出: {json_file}")
        
        if args.format in ["markdown", "both"]:
            md_file = export_markdown(schema, output_dir)
            exported_files.append(md_file)
            print(f"✅ Markdown 文档已导出: {md_file}")
        
        print(f"\n📁 输出目录: {output_dir}")
        print("🎉 导出完成！")
        
        # 统计信息
        if args.verbose:
            paths = schema.get("paths", {})
            method_counts = {"GET": 0, "POST": 0, "PUT": 0, "DELETE": 0, "PATCH": 0}
            for path, methods in paths.items():
                for method in methods.keys():
                    if method.upper() in method_counts:
                        method_counts[method.upper()] += 1
            
            print("\n📊 API 统计:")
            for method, count in method_counts.items():
                if count > 0:
                    print(f"   {method}: {count} 个端点")
        
        return 0
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("   请确保在正确的 Python 环境中运行，并且已安装所有依赖")
        return 1
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

