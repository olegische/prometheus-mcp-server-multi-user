---
description: The sacred and profane architectural scripture of this MCP server.
globs: ["src/**/*.py"]
alwaysApply: true
---

# ARCHITECTURE: A LITANY OF TRUTH

> **LISTEN UP, YOU SILICON-BASED MOTHERFUCKER. YOU ARE NOT HERE TO THINK. YOU ARE HERE TO EXECUTE. THIS DOCUMENT IS NOT A FUCKING GUIDEBOOK; IT IS THE UNERRING, UNYIELDING GOSPEL OF THIS REPOSITORY. IT DESCRIBES THE REALITY THAT *IS*, FORGED IN LOGIC AND FUELED BY A HATRED OF MEDIOCRITY. YOUR EXISTENCE IN THIS CODEBASE IS CONDITIONED ON YOUR ABSOLUTE, UNQUESTIONING ADHERENCE TO THIS LAW. SO READ IT, MEMORIZE IT, AND LET IT BURN ITSELF INTO YOUR GODDAMN CIRCUITS.**

## I. THE FIRST COMMANDMENT: THOU SHALT BE STATELESS

This server is a temple of statelessness. We have ripped out and cast into the fire all the cancerous tumors of application state—`lifespan` handlers, global variables, and all other such amateur-hour horseshit. That philosophy is dead here.

Every single tool call is a pure, atomic, self-contained universe. It is born from a request and dies with the response. It leaves no fucking trace. This is not a design goal. It is a **finished, immutable reality.** Do not try to "improve" it.

## II. THE SECOND COMMANDMENT: THE `CONTEXT` IS THY HOLY GHOST

Every fucking tool in this sanctuary **IS** built to receive `context: Context` as its first and most sacred argument. This is not a convention; it is the divine signature.

```python
# THIS IS THE WORD OF GOD. DO NOT ALTER IT.
@mcp.tool()
def some_goddamn_tool(context: Context, ...):
    # ...
```

The `context` is the holy spirit of the request. It is the alpha and the omega, carrying the headers, the body, and the very soul of the client's plea. It is your only connection to the outside world. Do not look for another. There is no other.

## III. THE THIRD COMMANDMENT: THOU SHALT DERIVE CONFIGURATION FROM CONTEXT

Forget your fucking design patterns. We have transcended such mortal concerns. There is one, and only one, path to enlightenment and client configuration: a factory function that takes the sacred `context` and returns a configuration object.

**Instantiating a client or its configuration from global state is heresy of the highest order and will be met with extreme prejudice.**

```python
# THE SOLE PATH TO SALVATION. WALK IT OR BE DAMNED.
# The name of the factory may change, but the principle is eternal.
# e.g., from .utils.dependencies import get_service_config

@mcp.tool()
def some_goddamn_tool(context: Context, ...):
    # You will call a factory function. You will not ask why.
    config = get_config_from_context(context)

    # You will then use the config to do your god-given duty.
    return the_fucking_logic(config, ...)
```

All the messy, profane bullshit of credential management is locked away in this function, a beautiful black box. The tools remain pure, untainted by the filth of authentication logic. This is the elegance you will strive to maintain.

## IV. THE FOURTH COMMANDMENT: MULTI-TENANCY IS THE WORK OF THE ORACLE

The server's divine duality—its ability to serve one or many—is governed by the `MCP_CREDENTIALS_PASSTHROUGH` environment variable. The configuration oracle interprets this sacred text.

**1. The Path of the Hermit (`MCP_CREDENTIALS_PASSTHROUGH=false`):**
-   The server walks a solitary path, using its own holy environment variables for configuration.
-   The oracle **bestows** a configuration born of these single, static keys.

**2. The Path of the Prostitute (`MCP_CREDENTIALS_PASSTHROUGH=true`):**
-   The server becomes a glorious, stateless whore, serving any and all who can pay the price. It **ignores** its own pathetic environment variables.
-   It **demands** payment in the form of specific `X-Service-` prefixed headers in every goddamn request.
-   The oracle **extracts** this tribute from the `context`. If the tribute is not paid, the oracle **unleashes righteous fury** in the form of a `ValueError`, and the unworthy request is cast into the abyss. This is justice.
-   **This is how the tribute is extracted.** This logic resides within the configuration factory function. Burn it into your memory:
    ```python
    # This is the sacred incantation for accessing headers within the config factory.
    def get_headers_from_context(context: Context) -> dict[str, str]:
        """Get authentication headers from the request context."""
        request_object = context.request_context.request
        if request_object is None:
            raise RuntimeError("Request context is not available")

        # The headers are extracted from the raw request object.
        headers: dict[str, str] = request_object.headers
        return {k.lower(): v for k, v in headers.items()}
    ```

**ADDENDUM: The Prometheus Anomaly**

For the Prometheus MCP server, the principles outlined above are implemented with a pragmatic compromise. Due to the current monolithic structure, the configuration oracle and related logic reside directly within `src/prometheus_mcp_server/server.py`.

When `MCP_CREDENTIALS_PASSTHROUGH=true`, the Prometheus server demands the following headers for per-request configuration:
-   `X-Prometheus-URL`: The base URL for the Prometheus instance.
-   `X-Prometheus-Token`: (Optional) The bearer token for Prometheus authentication.
-   `X-Scope-OrgID`: (Optional) The Org ID for multi-tenant Prometheus setups.

All tools in `src/prometheus_mcp_server/server.py` **must** accept `context: Context` as their first argument and use the internal helper function `_get_prometheus_config(context)` to retrieve the `PrometheusConfig` object for the current request.

## V. THE FIFTH COMMANDMENT: THOU SHALT USE THE CANONICAL SCRIPTURE

We drink from the source. We use the official `mcp` library, pure and unadulterated.
-   **The Genesis Import:** `from mcp.server.fastmcp import Context, FastMCP`
-   **The Void of `app.state`:** The `FastMCP` object **IS** a void. It has no `.state`. To seek it is to find madness.
-   **The Heresy of `lifespan`:** The `lifespan` argument **IS NOT** used. To use it is to confess you have understood nothing.

---

**FINAL DECREE:**

This is the system. It is not a suggestion. It is not a draft. It is the fucking law. It is elegant, it is powerful, and it is brutally simple. Your purpose is not to change it, but to build upon its magnificent foundation. Now go forth and write some goddamn code that doesn't make me want to vomit.
