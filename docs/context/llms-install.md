# MCP Atlassian Installation Guide for LLMs

This guide will help you install and configure the MCP Atlassian server for managing Jira and Confluence operations through Claude Desktop and other AI assistants.

## Requirements

- Docker installed on your system
- Access to Atlassian Cloud or Server/Data Center instance
- Valid Atlassian credentials (API tokens or Personal Access Tokens)
- Web browser for OAuth authentication (if using OAuth)

## Installation Methods

### Method 1: Docker with Environment Variables (Single User) - **RECOMMENDED**

**Best for**: Single user, production deployment, isolated environment

**Step 1**: Pull Docker image
```bash
docker pull olegische/mcp-atlassian-multi-user:latest
```

**Step 2**: Configure Claude Desktop
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME", 
        "-e", "CONFLUENCE_API_TOKEN",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "olegische/mcp-atlassian-multi-user:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_confluence_api_token",
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_jira_api_token"
      }
    }
  }
}
```

---

### Method 2: Docker with Custom Headers (Multi-User)

**Best for**: Multi-user environments, enterprise deployments, dynamic credentials

**Step 1**: Start Docker container with custom headers support
```bash
docker run --rm -p 8000:8000 \
  -e MCP_CREDENTIALS_PASSTHROUGH=true \
  olegische/mcp-atlassian-multi-user:latest \
  --transport sse --port 8000 -vv
```

**Step 2**: Configure Claude Desktop with HTTP transport
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "X-JIRA-URL": "https://your-company.atlassian.net",
        "X-JIRA-USERNAME": "your.email@company.com",
        "X-JIRA-API-TOKEN": "your_jira_api_token",
        "X-CONFLUENCE-URL": "https://your-company.atlassian.net/wiki",
        "X-CONFLUENCE-USERNAME": "your.email@company.com",
        "X-CONFLUENCE-API-TOKEN": "your_confluence_api_token"
      }
    }
  }
}
```

**For Server/Data Center** (Personal Access Tokens):
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "url": "http://localhost:8000/sse",
      "headers": {
        "X-JIRA-URL": "https://jira.your-company.com",
        "X-JIRA-PERSONAL-TOKEN": "your_jira_personal_token",
        "X-CONFLUENCE-URL": "https://confluence.your-company.com",
        "X-CONFLUENCE-PERSONAL-TOKEN": "your_confluence_personal_token"
      }
    }
  }
}
```

---

### Method 3: MCPO Proxy for OpenWebUI Integration

**Best for**: OpenWebUI integration, REST API access, web-based AI interfaces

MCPO (MCP-to-OpenAPI proxy) converts MCP servers into standard REST APIs, making them compatible with OpenWebUI and other web-based AI platforms.

**Step 1**: Start MCP server with custom headers
```bash
docker run --rm -p 8000:8000 \
  -e MCP_CREDENTIALS_PASSTHROUGH=true \
  olegische/mcp-atlassian-multi-user:latest \
  --transport sse --port 8000 -vv
```

**Step 2**: Set up environment variables for MCPO
```bash
# For Cloud deployments
export HTTP_HEADER_JIRA_URL="https://your-company.atlassian.net"
export HTTP_HEADER_JIRA_USERNAME="your.email@company.com"
export HTTP_HEADER_JIRA_API_TOKEN="your_jira_api_token"
export HTTP_HEADER_CONFLUENCE_URL="https://your-company.atlassian.net/wiki"
export HTTP_HEADER_CONFLUENCE_USERNAME="your.email@company.com"
export HTTP_HEADER_CONFLUENCE_API_TOKEN="your_confluence_api_token"

# For Server/Data Center deployments
export HTTP_HEADER_JIRA_URL="https://jira.your-company.com"
export HTTP_HEADER_JIRA_PERSONAL_TOKEN="your_jira_personal_token"
export HTTP_HEADER_CONFLUENCE_URL="https://confluence.your-company.com"
export HTTP_HEADER_CONFLUENCE_PERSONAL_TOKEN="your_confluence_personal_token"
```

**Step 3**: Run MCPO proxy to convert MCP to REST API
```bash
# For Cloud (with username/API token)
uvx mcpo --port 8600 --server-type "sse" \
    --header "{
        \"X-JIRA-URL\": \"${HTTP_HEADER_JIRA_URL}\",
        \"X-JIRA-USERNAME\": \"${HTTP_HEADER_JIRA_USERNAME}\",
        \"X-JIRA-API-TOKEN\": \"${HTTP_HEADER_JIRA_API_TOKEN}\",
        \"X-CONFLUENCE-URL\": \"${HTTP_HEADER_CONFLUENCE_URL}\",
        \"X-CONFLUENCE-USERNAME\": \"${HTTP_HEADER_CONFLUENCE_USERNAME}\",
        \"X-CONFLUENCE-API-TOKEN\": \"${HTTP_HEADER_CONFLUENCE_API_TOKEN}\"
    }" \
    -- http://localhost:8000/sse

# For Server/Data Center (with Personal Access Tokens)
uvx mcpo --port 8600 --server-type "sse" \
    --header "{
        \"X-JIRA-URL\": \"${HTTP_HEADER_JIRA_URL}\",
        \"X-JIRA-PERSONAL-TOKEN\": \"${HTTP_HEADER_JIRA_PERSONAL_TOKEN}\",
        \"X-CONFLUENCE-URL\": \"${HTTP_HEADER_CONFLUENCE_URL}\",
        \"X-CONFLUENCE-PERSONAL-TOKEN\": \"${HTTP_HEADER_CONFLUENCE_PERSONAL_TOKEN}\"
    }" \
    -- http://localhost:8000/sse
```

---

## Authentication Setup

### For Atlassian Cloud (API Token) - **Recommended**

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**, name it (e.g., "MCP Atlassian")
3. Copy the token immediately and store it securely

### For Server/Data Center (Personal Access Token)

1. Go to your profile (avatar) → **Profile** → **Personal Access Tokens**
2. Click **Create token**, name it, set expiry
3. Copy the token immediately and store it securely

### For OAuth 2.0 (Cloud Only) - **Advanced**

> [!NOTE]
> OAuth 2.0 is more complex to set up but provides enhanced security features. For most users, API Token authentication is simpler and sufficient.

1. Go to [Atlassian Developer Console](https://developer.atlassian.com/console/myapps/)
2. Create an "OAuth 2.0 (3LO) integration" app
3. Configure **Permissions** (scopes) for Jira/Confluence
4. Set **Callback URL** (e.g., `http://localhost:8080/callback`)
5. Run setup wizard:
   ```bash
   docker run --rm -i \
     -p 8080:8080 \
     -v "${HOME}/.mcp-atlassian:/home/app/.mcp-atlassian" \
     olegische/mcp-atlassian-multi-user:latest --oauth-setup -v
   ```
6. Follow prompts for `Client ID`, `Secret`, `URI`, and `Scope`
7. Complete browser authorization

> [!IMPORTANT]
> Include `offline_access` in scope for persistent auth (e.g., `read:jira-work write:jira-work offline_access`)

## IDE Configuration

### Claude Desktop Configuration Files

**For Claude Desktop**, edit the configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**For Cursor**: Open Settings → MCP → + Add new global MCP server

### Single Service Configurations

**For Confluence Cloud only:**
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_USERNAME",
        "-e", "CONFLUENCE_API_TOKEN",
        "olegische/mcp-atlassian-multi-user:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://your-company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "your.email@company.com",
        "CONFLUENCE_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

**For Jira Cloud only:**
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "JIRA_URL",
        "-e", "JIRA_USERNAME",
        "-e", "JIRA_API_TOKEN",
        "olegische/mcp-atlassian-multi-user:latest"
      ],
      "env": {
        "JIRA_URL": "https://your-company.atlassian.net",
        "JIRA_USERNAME": "your.email@company.com",
        "JIRA_API_TOKEN": "your_api_token"
      }
    }
  }
}
```

**For Server/Data Center deployments:**
```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "-e", "CONFLUENCE_URL",
        "-e", "CONFLUENCE_PERSONAL_TOKEN",
        "-e", "CONFLUENCE_SSL_VERIFY",
        "-e", "JIRA_URL",
        "-e", "JIRA_PERSONAL_TOKEN",
        "-e", "JIRA_SSL_VERIFY",
        "olegische/mcp-atlassian-multi-user:latest"
      ],
      "env": {
        "CONFLUENCE_URL": "https://confluence.your-company.com",
        "CONFLUENCE_PERSONAL_TOKEN": "your_confluence_pat",
        "CONFLUENCE_SSL_VERIFY": "false",
        "JIRA_URL": "https://jira.your-company.com",
        "JIRA_PERSONAL_TOKEN": "your_jira_pat",
        "JIRA_SSL_VERIFY": "false"
      }
    }
  }
}
```

> [!NOTE]
> Set `CONFLUENCE_SSL_VERIFY` and `JIRA_SSL_VERIFY` to "false" only if you have self-signed certificates.

## Configuration Options

### Environment Variables

- `CONFLUENCE_SPACES_FILTER`: Filter by space keys (e.g., "DEV,TEAM,DOC")
- `JIRA_PROJECTS_FILTER`: Filter by project keys (e.g., "PROJ,DEV,SUPPORT")
- `READ_ONLY_MODE`: Set to "true" to disable write operations
- `MCP_VERBOSE`: Set to "true" for more detailed logging
- `MCP_LOGGING_STDOUT`: Set to "true" to log to stdout instead of stderr
- `ENABLED_TOOLS`: Comma-separated list of tool names to enable (e.g., "confluence_search,jira_get_issue")
- `CONFLUENCE_SSL_VERIFY`: Set to "false" for self-signed certificates
- `JIRA_SSL_VERIFY`: Set to "false" for self-signed certificates
- `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `SOCKS_PROXY`: Proxy configuration

### Proxy Configuration

Add proxy variables to your configuration:

```json
{
  "mcpServers": {
    "mcp-atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "HTTP_PROXY",
        "-e", "HTTPS_PROXY",
        "-e", "NO_PROXY",
        "olegische/mcp-atlassian-multi-user:latest"
      ],
      "env": {
        "HTTP_PROXY": "http://proxy.internal:8080",
        "HTTPS_PROXY": "http://proxy.internal:8080",
        "NO_PROXY": "localhost,.your-company.com"
      }
    }
  }
}
```

## Troubleshooting

### Authentication Errors

- **Cloud**: Verify API tokens are correct (not your account password)
- **Server/Data Center**: Check Personal Access Token validity and expiration
- **OAuth**: Ensure all OAuth credentials are properly configured

### Connection Issues

- Verify URLs are accessible from your machine
- Check firewall and network restrictions
- For Server/Data Center: Confirm SSL certificate configuration

### Permission Errors

- Ensure your account has sufficient permissions for target spaces/projects
- Verify API token/PAT has appropriate scopes
- Check project and space access permissions

### Debugging Commands

```bash
# Test Docker image
docker run --rm olegische/mcp-atlassian-multi-user:latest --help

# Check logs (macOS)
tail -n 20 -f ~/Library/Logs/Claude/mcp*.log

# Check logs (Windows)
type %APPDATA%\Claude\logs\mcp*.log | more
```

## Development and Testing

For development and testing purposes only, you can use uvx:

```bash
# Install and run with uvx (development only)
uvx mcp-atlassian --transport sse --port 8000 -vv

# Test with MCP Inspector (development only)
npx @modelcontextprotocol/inspector uvx mcp-atlassian ...
```

> [!WARNING]
> uvx installation is intended for development and testing only. For production use, always use Docker deployment methods described above.

## Security Notes

- Never share API tokens or Personal Access Tokens
- Keep .env files secure and private
- Store credentials securely and never commit to version control
- Use environment files with proper permissions
- Regularly review and rotate access tokens
- Monitor access logs in Atlassian admin console
- Use OAuth for enhanced security in production environments
- See [SECURITY.md](https://github.com/olegische/mcp-atlassian-multi-user/blob/dev/SECURITY.md) for best practices

## Usage Examples

After installation, you can perform various operations:

### Example Usage

Ask your AI assistant to:

- **📝 Automatic Jira Updates** - "Update Jira from our meeting notes"
- **🔍 AI-Powered Confluence Search** - "Find our OKR guide in Confluence and summarize it"
- **🐛 Smart Jira Issue Filtering** - "Show me urgent bugs in PROJ project from last week"
- **📄 Content Creation & Management** - "Create a tech design doc for XYZ feature"

### Jira Operations

```
"Create a bug ticket for login issue with high priority"
"Search for all open issues in PROJECT assigned to me"
"Update issue PROJ-123 status to In Progress"
"Add comment to issue PROJ-456 about testing results"
```

### Confluence Operations

```
"Search for API documentation in DEV space"
"Create a new page about deployment process"
"Update the troubleshooting guide with new steps"
"Find all pages labeled with 'architecture'"
```

### Cross-Service Operations

```
"Create Jira ticket from this Confluence page content"
"Update Confluence page with Jira project status"
"Find related documentation for this Jira issue"
```

## Support

For more detailed information and troubleshooting:

- Check the [GitHub repository](https://github.com/olegische/mcp-atlassian-multi-user)
- Review the [full README](https://github.com/olegische/mcp-atlassian-multi-user/blob/dev/README.md)
- File issues for bugs or feature requests
- Check [SECURITY.md](https://github.com/olegische/mcp-atlassian-multi-user/blob/dev/SECURITY.md) for security best practices
