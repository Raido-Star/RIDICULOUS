# 🚀 RIDICULOUS - Access Information

## ✅ Server Status

Both servers are **RUNNING** inside the container:

- **Web UI Server**: Port 3000 (HTTP 200 ✓)
- **MCP API Server**: Port 8000 (HTTP 404 on / is normal ✓)

## 🌐 How to Access

### If you're in a remote development environment (Codespaces, Cloud Shell, etc.):

You need to **forward the ports** from the container to your local machine.

#### For GitHub Codespaces:
1. Open the "PORTS" tab in VS Code
2. Click "Forward Port"
3. Add port **3000**
4. Add port **8000**
5. Click on the forwarded URL for port 3000

#### For Cloud Shell / Remote SSH:
```bash
# From your LOCAL machine, run:
ssh -L 3000:localhost:3000 -L 8000:localhost:8000 user@your-server

# Then access:
http://localhost:3000/static/index.html
```

#### For Docker:
```bash
# Restart container with port mapping:
docker run -p 3000:3000 -p 8000:8000 ...
```

## 🔧 Current Server Details

**Web UI Server (Port 3000)**:
- Binding: 0.0.0.0:3000 (all interfaces)
- Status: Listening and responding
- Test URL: http://127.0.0.1:3000/static/index.html

**MCP API Server (Port 8000)**:
- Binding: 127.0.0.1:8000 (localhost only)
- Status: Listening and responding
- Endpoint: http://127.0.0.1:8000/mcp

## 📊 Platform Features

- **47 MCP Tools** for research, intelligence, and asset generation
- **15+ Platforms** supported (YouTube, Instagram, TikTok, LinkedIn, etc.)
- **Advanced OSINT** capabilities
- **Semantic search** with TF-IDF
- **Real-time research** with DuckDuckGo

## 🆘 Need Help?

The servers are confirmed working inside the container. If you can't access them, you need to set up port forwarding from the container to your local machine.

Check your development environment documentation for port forwarding instructions.
