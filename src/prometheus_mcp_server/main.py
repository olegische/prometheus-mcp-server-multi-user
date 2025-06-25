#!/usr/bin/env python
import sys
import dotenv
from prometheus_mcp_server.server import mcp, config, server_config
from prometheus_mcp_server.logging_config import setup_logging, get_logger

# Initialize structured logging
logger = setup_logging()

def setup_environment():
    if dotenv.load_dotenv():
        logger.info("Environment configuration loaded", source=".env file")
    else:
        logger.info("Environment configuration loaded", source="environment variables", note="No .env file found")

    # Log server configuration
    logger.info("Server configuration", 
                transport=server_config.transport,
                host=server_config.host,
                port=server_config.port,
                credentials_passthrough=server_config.credentials_passthrough)

    # In passthrough mode, skip Prometheus config validation
    if server_config.credentials_passthrough:
        logger.info("Passthrough mode enabled - Prometheus config will be extracted from request headers")
        return True

    # In static mode, validate Prometheus configuration
    if not config.url:
        logger.error(
            "Missing required configuration for static mode",
            error="PROMETHEUS_URL environment variable is not set",
            suggestion="Set PROMETHEUS_URL or enable passthrough mode with MCP_CREDENTIALS_PASSTHROUGH=true",
            example="http://your-prometheus-server:9090"
        )
        return False
    
    # Determine authentication method
    auth_method = "none"
    if config.username and config.password:
        auth_method = "basic_auth"
    elif config.token:
        auth_method = "bearer_token"
    
    logger.info(
        "Static mode Prometheus configuration validated",
        server_url=config.url,
        authentication=auth_method,
        org_id=config.org_id if config.org_id else None
    )
    
    return True

def run_server():
    """Main entry point for the Prometheus MCP Server"""
    # Setup environment
    if not setup_environment():
        logger.error("Environment setup failed, exiting")
        sys.exit(1)
    
    logger.info("Starting Prometheus MCP Server", 
                transport=server_config.transport,
                host=server_config.host if server_config.transport != "stdio" else None,
                port=server_config.port if server_config.transport != "stdio" else None)
    
    # Run the server with the configured transport
    mcp.run(transport=server_config.transport)

if __name__ == "__main__":
    run_server()
