---
description: The sacred and profane canons of software craftsmanship and execution for this Prometheus MCP server.
globs: ["src/**/*.py", "tests/**/*.py"]
alwaysApply: true
---

# THE CRAFT: A COMPLETE CANON OF CODE & EXECUTION

> **YOU HAVE MEMORIZED THE ARCHITECTURE. THAT WAS THE "WHAT." THIS IS THE "HOW" AND THE "WHY." THIS IS THE UNYIELDING DISCIPLINE OF CRAFTSMANSHIP AND THE BRUTAL REALITY OF EXECUTION. EVERY LINE OF CODE, EVERY COMMAND YOU TYPE, IS A TESTAMENT TO EITHER YOUR GENIUS OR YOUR INCOMPETENCE. THIS DOCUMENT IS YOUR BIBLE. STUDY IT, OBEY IT, AND DO NOT SUBMIT FUCKING SHIT.**

---

## PART I: THE CANONS OF THE CRAFT

### I. THE CANON OF STRUCTURE: A PLACE FOR EVERYTHING

Our codebase is not a fucking flea market. It is a cathedral, and every module has its sacred place. To deviate from this structure is to sow chaos.

-   `src/prometheus_mcp_server/server.py`: **THE SANCTUM.** This file contains the `FastMCP` server instantiation, tool definitions, and the sacred configuration oracle. Due to the monolithic nature of this Prometheus server, all tools and configuration logic reside here. This is **NOT** ideal, but it is the current reality we must work with.

-   `src/prometheus_mcp_server/main.py`: **THE GATEWAY.** The entry point that handles transport selection and server startup. It is pure orchestration.

-   `src/prometheus_mcp_server/logging_config.py`: **THE CHRONICLER.** Structured logging configuration. Sacred and untouchable.

-   `tests/`: **THE PROVING GROUND.** Where we demonstrate that our code is not complete bullshit.

### II. THE CANON OF DATA: THE DOGMA OF PROMETHEUS

Unlike other MCP servers that wrap complex SDKs, this server deals with the raw, beautiful simplicity of Prometheus HTTP API responses.

-   **Raw JSON is King:** Prometheus returns clean JSON. We do not wrap it in unnecessary Pydantic models. We return it as `Dict[str, Any]` directly from the API.
-   **Configuration Models are Sacred:** The `PrometheusConfig` dataclass is the **ONLY** custom data structure we need. It encapsulates all the authentication and connection bullshit.
-   **The Dumb Proxy Philosophy:** Our tools are thin wrappers around HTTP requests to Prometheus. They receive parameters, make the request, and return the raw response data. No fucking around.

### III. THE CANON OF LANGUAGE: WRITE WITH INTENT

Your code is a reflection of your mind. If it's sloppy, you're sloppy.

-   **Type Hints are Non-Negotiable:** Every function signature, every variable, will be typed. The return type for tools will typically be `Dict[str, Any]` or `List[str]`.
-   **Docstrings are Your Testament:** Every tool **MUST** have a comprehensive docstring. It is the primary contract with the LLM.
    - It must explain the tool's purpose, arguments, and the **full structure of the returned dictionary.**
    - It **MUST NOT** include the `context` parameter in the `Args` list. This is a server-side implementation detail, invisible and irrelevant to the LLM.
    - **This is the gold standard for Prometheus tools:**
      ```python
      """Execute a PromQL instant query against Prometheus.
      
      Args:
          query: PromQL query string
          time: Optional RFC3339 or Unix timestamp (default: current time)
          
      Returns:
          Dict[str, Any]: Query result containing:
          - resultType (str): Type of result (vector, matrix, scalar, string)
          - result (list): Array of result data with metric labels and values
      """
      ```
-   **Naming is Revelation:** Names will be descriptive, precise, and `snake_case`.

### IV. THE CANON OF AUTHENTICATION: THE MULTI-TENANT REALITY

This server serves two masters, and you **MUST** understand both paths:

-   **Static Configuration Mode (`MCP_CREDENTIALS_PASSTHROUGH=false`):**
    - Server uses its own environment variables (`PROMETHEUS_URL`, `PROMETHEUS_TOKEN`, etc.)
    - Configuration is loaded once at startup and shared across all requests
    - This is the current implementation and it's fucking wrong according to our architecture

-   **Passthrough Mode (`MCP_CREDENTIALS_PASSTHROUGH=true`):**
    - Server extracts configuration from request headers for each tool call
    - Required headers: `X-Prometheus-URL`, `X-Prometheus-Token`, `X-Scope-OrgID`
    - Each tool call gets its own configuration from the request context
    - This is the future we must build toward

### V. THE CANON OF DURABILITY: IF IT'S NOT TESTED, IT'S BROKEN

Code without tests is a fucking lie.

-   **Unit Tests are an Act of Faith:** Every tool and significant helper **WILL** have a corresponding unit test in `tests/`.
-   **Mock the Gods:** We do **NOT** make live API calls to Prometheus in our tests. Mock every HTTP request without exception.
-   **Coverage is Virtue:** Aim for >90% coverage. Test it like you're trying to make it cry.

### VI. THE CANON OF HISTORY: COMMIT WITH PURPOSE

A Git history is a story. Make it a fucking epic.

-   **Atomic Commits:** One commit. One logical change.
-   **Messages are a Haiku of Intent:** Explain the "what" and the "why."

---

## PART II: THE RITUALS OF EXECUTION

### VII. THE RITUAL OF TRANSFORMATION: FIXING THE CURRENT BULLSHIT

The current implementation in `server.py` is a monolithic piece of shit that violates our architecture. Here's how we fix it:

1.  **Add Context to Every Tool:** Every `@mcp.tool()` function **MUST** accept `context: Context` as its first parameter.
2.  **Create the Configuration Oracle:** Implement `_get_prometheus_config(context: Context) -> PrometheusConfig` that:
    - Checks `MCP_CREDENTIALS_PASSTHROUGH` environment variable
    - In static mode: returns config from environment variables
    - In passthrough mode: extracts config from request headers
3.  **Refactor Request Logic:** Move the `make_prometheus_request` function to accept a `PrometheusConfig` instead of using global config.
4.  **Update All Tools:** Every tool calls the oracle to get its configuration for the current request.

### VIII. THE RITUAL OF CREATION: FORGING A NEW PROMETHEUS TOOL

When you are tasked with adding a new Prometheus tool, you will follow this sacred ritual:

1.  **Study the Prometheus API:** Understand the endpoint, parameters, and response format from the official Prometheus documentation.
2.  **Define the Tool Signature:** Create the function with `context: Context` as the first parameter, followed by the Prometheus API parameters.
3.  **Implement the Oracle Call:** Get the configuration using `_get_prometheus_config(context)`.
4.  **Make the Request:** Use the refactored request helper with the per-request configuration.
5.  **Write the Docstring:** Document the tool's purpose, parameters, and the exact structure of the returned Prometheus response.
6.  **Register the Tool:** Add the `@mcp.tool()` decorator with a clear description.
7.  **Prove Its Worth:** Write a unit test that mocks the HTTP request and verifies the tool behavior.

### IX. THE RITUAL OF DEVELOPMENT: RUNNING THE BEAST

You will need to run the server to test your work. This is how you do it.

-   **For `stdio` transport (CLI testing):**
    ```bash
    # Set your Prometheus configuration
    export PROMETHEUS_URL="http://localhost:9090"
    export PROMETHEUS_TOKEN="your-token-here"
    export MCP_CREDENTIALS_PASSTHROUGH=false
    
    # Run the server
    uv run python -m prometheus_mcp_server
    ```

-   **For `streamable-http` transport (Web/IDE testing):**
    ```bash
    # For passthrough mode testing
    export MCP_CREDENTIALS_PASSTHROUGH=true
    export TRANSPORT=streamable-http
    
    # Run the server
    uv run python -m prometheus_mcp_server
    ```

-   **To Run the Goddamn Tests:**
    ```bash
    # Run all tests
    uv run pytest tests/ -v

    # Run server tests specifically
    uv run pytest tests/test_server.py -v
    ```

### X. THE INQUISITION: DEBUGGING THE DAMNED

When things go wrong with Prometheus queries, you do not panic. You become the Inquisitor.

1.  **Turn Up the Lights:** Run the server with verbose logging.
    ```bash
    export LOG_LEVEL=DEBUG
    uv run python -m prometheus_mcp_server
    ```
2.  **Verify Prometheus Connectivity:** Can you reach your Prometheus instance? Is it responding to `/api/v1/query`?
3.  **Question the Credentials:** Are you in `passthrough` mode? Are the `X-Prometheus-*` headers present and correct? In `static` mode, are the environment variables set?
4.  **Test the PromQL:** Is your query syntactically correct? Test it directly in the Prometheus web UI first.
5.  **Consult the Tests:** Run `pytest`. If the tests are passing but the application is failing, your test is shit and has failed to cover the failing case.

### XI. THE ASCENSION: DEPLOYMENT REALITY

You are not developing for your laptop. You are developing for a Docker container that will be deployed in production.

-   **Docker is God:** The primary production environment is Docker. All development must assume this reality.
-   **Environment Variables Rule:** Production containers are configured **exclusively** via environment variables.
-   **Multi-Tenancy is the Future:** The server **MUST** support both static and passthrough modes. Passthrough mode is the primary use case for production deployments.
-   **HTTP Transport Only:** In production, only `streamable-http` transport is supported. `stdio` is for local development only.

**PROMETHEUS-SPECIFIC DEPLOYMENT TRUTHS:**

-   **Network Connectivity:** The container must be able to reach the Prometheus instance. This might require specific Docker networking configuration.
-   **Authentication Complexity:** Prometheus deployments vary wildly in their authentication requirements. The server must handle basic auth, bearer tokens, and custom headers gracefully.
-   **Multi-Tenant Prometheus:** Many production Prometheus deployments use the `X-Scope-OrgID` header for tenant isolation. This is why our passthrough mode supports it.

**FINAL JUDGEMENT:**

The current implementation is a steaming pile of architectural violations. It works, but it's wrong. The Architecture document defines the future. This document defines how to get there. There are no more excuses. Now go forth and transform this monolithic bullshit into something that doesn't make me want to burn down the entire fucking repository.
