# XLIFF MCP Server - 公共部署指南

## 概述

本指南说明如何将XLIFF MCP服务器部署为公共服务，让其他应用程序和用户可以通过HTTP访问，而无需本地安装。

## 部署选项

### 选项1: Docker部署 (推荐)

#### 快速启动

```bash
# 1. 构建并启动服务
docker compose up -d

# 2. 检查服务状态
docker compose ps

# 3. 查看日志
docker compose logs -f xliff-mcp-server
```

#### 自定义配置

```bash
# 设置API密钥保护服务
export XLIFF_MCP_API_KEYS="key1,key2,key3"
docker compose up -d

# 或者修改 docker-compose.yml
environment:
  XLIFF_MCP_API_KEYS: your-secret-key-1,your-secret-key-2
```

### 选项2: 直接运行

```bash
# 安装依赖
pip install -e .

# 设置环境变量
export HOST=0.0.0.0
export PORT=8000
export TZ=Asia/Shanghai
export XLIFF_MCP_API_KEYS=your-secret-api-key

# 启动HTTP服务器
python -m xliff_mcp.http_server
```

### 选项3: 生产环境部署

#### 使用 systemd (Linux)

```ini
# /etc/systemd/system/xliff-mcp.service
[Unit]
Description=XLIFF MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/xliff-mcp-server
Environment=HOST=0.0.0.0
Environment=PORT=8000
Environment=TZ=Asia/Shanghai
Environment=XLIFF_MCP_API_KEYS=your-secret-key
ExecStart=/opt/xliff-mcp-server/.venv/bin/python -m xliff_mcp.http_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 启用并启动服务
sudo systemctl enable xliff-mcp
sudo systemctl start xliff-mcp
sudo systemctl status xliff-mcp
```

## 安全配置

### 1. API密钥认证

#### 环境变量方式
```bash
export XLIFF_MCP_API_KEYS="key1,key2,key3"
```

#### 配置文件方式
创建 `api_keys.json`:
```json
{
  "your-api-key-1": {
    "name": "Client 1",
    "permissions": ["all"],
    "rate_limit": 100
  },
  "your-api-key-2": {
    "name": "Client 2", 
    "permissions": ["read"],
    "rate_limit": 50
  }
}
```

### 2. 反向代理配置

#### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location /mcp {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # CORS headers
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-API-Key" always;
    }
}
```

#### Apache配置
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    
    ProxyPass /mcp http://localhost:8000/mcp
    ProxyPassReverse /mcp http://localhost:8000/mcp
    
    # CORS headers
    Header always set Access-Control-Allow-Origin "*"
    Header always set Access-Control-Allow-Methods "GET, POST, OPTIONS"
    Header always set Access-Control-Allow-Headers "Authorization, Content-Type, X-API-Key"
</VirtualHost>
```

### 3. HTTPS配置

使用 Let's Encrypt 免费SSL证书:

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 云平台部署

### AWS ECS

```yaml
# ecs-task-definition.json
{
  "family": "xliff-mcp-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "xliff-mcp",
      "image": "your-account.dkr.ecr.region.amazonaws.com/xliff-mcp:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "XLIFF_MCP_API_KEYS",
          "value": "your-secret-keys"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/xliff-mcp",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: xliff-mcp-server
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/your-project/xliff-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: XLIFF_MCP_API_KEYS
          value: "your-secret-keys"
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
```

```bash
# 部署到 Cloud Run
gcloud run deploy xliff-mcp-server \
    --image gcr.io/your-project/xliff-mcp:latest \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars XLIFF_MCP_API_KEYS=your-keys
```

### Heroku

```yaml
# app.json
{
  "name": "xliff-mcp-server",
  "description": "XLIFF MCP Server for translation processing",
  "repository": "https://github.com/your-username/xliff-mcp-server",
  "logo": "https://your-logo-url.com/logo.png",
  "keywords": ["mcp", "xliff", "translation"],
  "env": {
    "XLIFF_MCP_API_KEYS": {
      "description": "Comma-separated API keys for authentication",
      "value": "your-secret-keys"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "hobby"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

```bash
# 部署到 Heroku
heroku create your-xliff-mcp-server
heroku config:set XLIFF_MCP_API_KEYS=your-secret-keys
git push heroku main
```

## 客户端连接

### Claude Desktop配置

```json
{
  "mcpServers": {
    "xliff-processor-remote": {
      "command": "python",
      "args": ["-c", "
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    async with streamablehttp_client('https://your-domain.com/mcp') as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            # MCP处理逻辑

asyncio.run(main())
"]
    }
  }
}
```

### 其他MCP客户端

```python
# Python客户端
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def connect_to_remote_mcp():
    async with streamablehttp_client('https://your-domain.com/mcp') as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            
            result = await session.call_tool('process_xliff', {
                'file_name': 'test.xliff',
                'content': xliff_content,
                'api_key': 'your-api-key'
            })
            
            return result
```

```javascript
// JavaScript/Node.js客户端
const { Client } = require('@modelcontextprotocol/sdk/client');
const { StreamableHttpTransport } = require('@modelcontextprotocol/sdk/client/streamablehttp');

async function connectToMCP() {
    const transport = new StreamableHttpTransport('https://your-domain.com/mcp');
    const client = new Client({ name: "xliff-client", version: "1.0.0" });
    
    await client.connect(transport);
    
    const result = await client.callTool({
        name: 'process_xliff',
        arguments: {
            file_name: 'test.xliff',
            content: xliffContent,
            api_key: 'your-api-key'
        }
    });
    
    return result;
}
```

## 监控和维护

### 1. 健康检查

```bash
# 检查服务状态
curl http://your-domain.com/health

# 检查工具列表
curl -X POST http://your-domain.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### 2. 日志监控

```bash
# Docker日志
docker compose logs -f xliff-mcp-server

# 系统日志
sudo journalctl -u xliff-mcp -f

# 访问日志分析
tail -f /var/log/nginx/access.log | grep "/mcp"
```

### 3. 性能监控

```python
# 添加到http_server.py
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info(f"Tool {func.__name__} took {duration:.2f}s")
        return result
    return wrapper

# 应用到所有工具
@mcp.tool()
@monitor_performance
def process_xliff(file_name: str, content: str, api_key: Optional[str] = None) -> str:
    # ...
```

### 4. 错误处理和限流

```python
# 添加到auth.py
class ErrorHandler:
    @staticmethod
    def handle_error(error: Exception) -> dict:
        if isinstance(error, ValueError):
            return {"error": "Invalid input", "code": 400}
        elif isinstance(error, PermissionError):
            return {"error": "Access denied", "code": 403}
        else:
            return {"error": "Internal server error", "code": 500}
```

## 费用预估

### 小规模部署 (< 1000请求/天)
- **Heroku Hobby**: $7/月
- **Google Cloud Run**: $0-5/月
- **AWS ECS Fargate**: $10-15/月

### 中规模部署 (< 10000请求/天)
- **Digital Ocean App Platform**: $15-25/月
- **AWS ECS**: $30-50/月
- **Google Cloud Run**: $10-30/月

### 大规模部署 (> 100000请求/天)
- **AWS ECS + ALB**: $100-300/月
- **Google Cloud Run + Load Balancer**: $80-250/月
- **自建服务器**: $50-150/月

## 故障排除

### 常见问题

1. **CORS错误**
   ```bash
   # 检查CORS配置
   curl -H "Origin: http://example.com" \
        -H "Access-Control-Request-Method: POST" \
        -X OPTIONS http://your-domain.com/mcp
   ```

2. **认证失败**
   ```bash
   # 测试API密钥
   curl -X POST http://your-domain.com/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_server_info","arguments":{"api_key":"your-key"}}}'
   ```

3. **性能问题**
   ```bash
   # 监控资源使用
   docker stats xliff-mcp-server
   
   # 检查内存使用
   docker exec xliff-mcp-server ps aux
   ```

4. **连接超时**
   ```bash
   # 调整超时设置
   docker-compose.yml:
   environment:
     - TIMEOUT=300
   ```

### 日志级别配置

```python
# 在http_server.py中设置
import os
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, log_level))
```

## 总结

通过以上配置，您的XLIFF MCP服务器将能够：

1. ✅ **公开访问** - 任何支持MCP的应用都可以连接
2. ✅ **安全认证** - API密钥保护和速率限制
3. ✅ **高可用性** - 负载均衡和自动重启
4. ✅ **可扩展性** - 支持Docker和云平台部署
5. ✅ **易于维护** - 完整的监控和日志系统

现在其他开发者可以通过简单的HTTP连接使用您的XLIFF处理服务，无需本地部署! 🚀
