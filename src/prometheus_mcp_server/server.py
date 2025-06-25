#!/usr/bin/env python

import os
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import time
from datetime import datetime, timedelta

import dotenv
import requests
from mcp.server.fastmcp import Context, FastMCP
from prometheus_mcp_server.logging_config import get_logger

dotenv.load_dotenv()

# Get logger instance
logger = get_logger()

@dataclass
class PrometheusConfig:
    url: str
    # Optional credentials
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None
    # Optional Org ID for multi-tenant setups
    org_id: Optional[str] = None

@dataclass
class ServerConfig:
    transport: str
    host: str
    port: int
    credentials_passthrough: bool

config = PrometheusConfig(
    url=os.environ.get("PROMETHEUS_URL", ""),
    username=os.environ.get("PROMETHEUS_USERNAME", ""),
    password=os.environ.get("PROMETHEUS_PASSWORD", ""),
    token=os.environ.get("PROMETHEUS_TOKEN", ""),
    org_id=os.environ.get("ORG_ID", ""),
)

server_config = ServerConfig(
    transport=os.environ.get("TRANSPORT", "stdio"),
    host=os.environ.get("HOST", "0.0.0.0"),
    port=int(os.environ.get("PORT", "8660")),
    credentials_passthrough=os.environ.get("MCP_CREDENTIALS_PASSTHROUGH", "false").lower() == "true"
)

def create_server() -> FastMCP:
    """Create MCP server based on transport configuration."""
    if server_config.transport == "stdio":
        mcp = FastMCP("Prometheus MCP")
    else:
        mcp = FastMCP("Prometheus MCP", host=server_config.host, port=server_config.port)
    return mcp

# Create the server instance
mcp = create_server()

def get_headers_from_context(context: Context) -> dict[str, str]:
    """Get authentication headers from the request context."""
    request_object = context.request_context.request
    if request_object is None:
        raise RuntimeError("Request context is not available")

    # The headers are extracted from the raw request object.
    headers: dict[str, str] = request_object.headers
    return {k.lower(): v for k, v in headers.items()}

def _get_prometheus_config(context: Context) -> PrometheusConfig:
    """The sacred configuration oracle. Extract Prometheus config from context.
    
    This is the divine function that determines whether we serve one master or many.
    It checks MCP_CREDENTIALS_PASSTHROUGH and acts accordingly.
    """
    if not server_config.credentials_passthrough:
        # The Path of the Hermit: use static environment variables
        logger.debug("Using static configuration from environment variables")
        return config
    
    # The Path of the Prostitute: extract from request headers
    logger.debug("Using passthrough mode - extracting config from request headers")
    
    try:
        headers = get_headers_from_context(context)
        
        # Extract required Prometheus URL
        prometheus_url = headers.get("x-prometheus-url")
        if not prometheus_url:
            raise ValueError("X-Prometheus-URL header is required in passthrough mode")
        
        # Extract ALL optional credentials - we serve any fucking master who pays
        prometheus_username = headers.get("x-prometheus-username")
        prometheus_password = headers.get("x-prometheus-password") 
        prometheus_token = headers.get("x-prometheus-token")
        org_id = headers.get("x-scope-orgid")
        
        logger.debug("Extracted configuration from headers", 
                    url=prometheus_url, 
                    has_username=bool(prometheus_username),
                    has_password=bool(prometheus_password),
                    has_token=bool(prometheus_token),
                    has_org_id=bool(org_id))
        
        return PrometheusConfig(
            url=prometheus_url,
            username=prometheus_username,
            password=prometheus_password,
            token=prometheus_token,
            org_id=org_id
        )
        
    except Exception as e:
        logger.error("Failed to extract Prometheus configuration from context", error=str(e))
        raise ValueError(f"Failed to extract Prometheus configuration: {str(e)}")

def get_prometheus_auth(prometheus_config: PrometheusConfig):
    """Get authentication for Prometheus based on provided credentials."""
    if prometheus_config.token:
        return {"Authorization": f"Bearer {prometheus_config.token}"}
    elif prometheus_config.username and prometheus_config.password:
        return requests.auth.HTTPBasicAuth(prometheus_config.username, prometheus_config.password)
    return None

def make_prometheus_request(prometheus_config: PrometheusConfig, endpoint: str, params=None):
    """Make a request to the Prometheus API with proper authentication and headers."""
    if not prometheus_config.url:
        logger.error("Prometheus configuration missing", error="PROMETHEUS_URL not set")
        raise ValueError("Prometheus configuration is missing. Please set PROMETHEUS_URL.")

    url = f"{prometheus_config.url.rstrip('/')}/api/v1/{endpoint}"
    auth = get_prometheus_auth(prometheus_config)
    headers = {}

    if isinstance(auth, dict):  # Token auth is passed via headers
        headers.update(auth)
        auth = None  # Clear auth for requests.get if it's already in headers
    
    # Add OrgID header if specified
    if prometheus_config.org_id:
        headers["X-Scope-OrgID"] = prometheus_config.org_id

    try:
        logger.debug("Making Prometheus API request", endpoint=endpoint, url=url, params=params)
        
        # Make the request with appropriate headers and auth
        response = requests.get(url, params=params, auth=auth, headers=headers)
        
        response.raise_for_status()
        result = response.json()
        
        if result["status"] != "success":
            error_msg = result.get('error', 'Unknown error')
            logger.error("Prometheus API returned error", endpoint=endpoint, error=error_msg, status=result["status"])
            raise ValueError(f"Prometheus API error: {error_msg}")
        
        logger.debug("Prometheus API request successful", endpoint=endpoint, result_type=result.get("data", {}).get("resultType"))
        return result["data"]
    
    except requests.exceptions.RequestException as e:
        logger.error("HTTP request to Prometheus failed", endpoint=endpoint, url=url, error=str(e), error_type=type(e).__name__)
        raise
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Prometheus response as JSON", endpoint=endpoint, url=url, error=str(e))
        raise ValueError(f"Invalid JSON response from Prometheus: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error during Prometheus request", endpoint=endpoint, url=url, error=str(e), error_type=type(e).__name__)
        raise

@mcp.tool(description="Execute a PromQL instant query against Prometheus")
async def execute_query(context: Context, query: str, time: Optional[str] = None) -> Dict[str, Any]:
    """Execute an instant query against Prometheus.
    
    Args:
        query: PromQL query string
        time: Optional RFC3339 or Unix timestamp (default: current time)
        
    Returns:
        Dict[str, Any]: Query result containing:
        - resultType (str): Type of result (vector, matrix, scalar, string)
        - result (list): Array of result data with metric labels and values
    """
    # Get configuration from the sacred oracle
    prometheus_config = _get_prometheus_config(context)
    
    params = {"query": query}
    if time:
        params["time"] = time
    
    logger.info("Executing instant query", query=query, time=time)
    data = make_prometheus_request(prometheus_config, "query", params=params)
    
    result = {
        "resultType": data["resultType"],
        "result": data["result"]
    }
    
    logger.info("Instant query completed", 
                query=query, 
                result_type=data["resultType"], 
                result_count=len(data["result"]) if isinstance(data["result"], list) else 1)
    
    return result

@mcp.tool(description="Execute a PromQL range query with start time, end time, and step interval")
async def execute_range_query(context: Context, query: str, start: str, end: str, step: str) -> Dict[str, Any]:
    """Execute a range query against Prometheus.
    
    Args:
        query: PromQL query string
        start: Start time as RFC3339 or Unix timestamp
        end: End time as RFC3339 or Unix timestamp
        step: Query resolution step width (e.g., '15s', '1m', '1h')
        
    Returns:
        Dict[str, Any]: Range query result containing:
        - resultType (str): Type of result (usually matrix)
        - result (list): Array of result data with metric labels and values over time
    """
    # Get configuration from the sacred oracle
    prometheus_config = _get_prometheus_config(context)
    
    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": step
    }
    
    logger.info("Executing range query", query=query, start=start, end=end, step=step)
    data = make_prometheus_request(prometheus_config, "query_range", params=params)
    
    result = {
        "resultType": data["resultType"],
        "result": data["result"]
    }
    
    logger.info("Range query completed", 
                query=query, 
                result_type=data["resultType"], 
                result_count=len(data["result"]) if isinstance(data["result"], list) else 1)
    
    return result

@mcp.tool(description="List all available metrics in Prometheus")
async def list_metrics(context: Context) -> List[str]:
    """Retrieve a list of all metric names available in Prometheus.
    
    Returns:
        List[str]: List of metric names as strings
    """
    # Get configuration from the sacred oracle
    prometheus_config = _get_prometheus_config(context)
    
    logger.info("Listing available metrics")
    data = make_prometheus_request(prometheus_config, "label/__name__/values")
    logger.info("Metrics list retrieved", metric_count=len(data))
    return data

@mcp.tool(description="Get metadata for a specific metric")
async def get_metric_metadata(context: Context, metric: str) -> List[Dict[str, Any]]:
    """Get metadata about a specific metric.
    
    Args:
        metric: The name of the metric to retrieve metadata for
        
    Returns:
        List[Dict[str, Any]]: List of metadata entries for the metric
    """
    # Get configuration from the sacred oracle
    prometheus_config = _get_prometheus_config(context)
    
    logger.info("Retrieving metric metadata", metric=metric)
    params = {"metric": metric}
    data = make_prometheus_request(prometheus_config, "metadata", params=params)
    logger.info("Metric metadata retrieved", metric=metric, metadata_count=len(data["metadata"]))
    return data["metadata"]

@mcp.tool(description="Get information about all scrape targets")
async def get_targets(context: Context) -> Dict[str, List[Dict[str, Any]]]:
    """Get information about all Prometheus scrape targets.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary containing:
        - activeTargets (list): List of active scrape targets
        - droppedTargets (list): List of dropped scrape targets
    """
    # Get configuration from the sacred oracle
    prometheus_config = _get_prometheus_config(context)
    
    logger.info("Retrieving scrape targets information")
    data = make_prometheus_request(prometheus_config, "targets")
    
    result = {
        "activeTargets": data["activeTargets"],
        "droppedTargets": data["droppedTargets"]
    }
    
    logger.info("Scrape targets retrieved", 
                active_targets=len(data["activeTargets"]), 
                dropped_targets=len(data["droppedTargets"]))
    
    return result

if __name__ == "__main__":
    logger.info("Starting Prometheus MCP Server", mode="direct")
    mcp.run()
