"""OpenAI Assistant MCP Server.

This module implements an MCP server for interacting with OpenAI Assistant API.
"""

import logging
from typing import Any, Dict, List, Literal, Optional, Union

from mcp.server.fastmcp import Context, FastMCP

# Run step models
from openai.types.beta.threads.runs import RunStepInclude

from .config.settings import Settings

# Tool models from common
# Common models
from .tools import (
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    Metadata,
    ResponseFormat,
    Tool,
    ToolResources,
)
from .tools.assistant import create_assistant as tools_create_assistant
from .tools.assistant import delete_assistant as tools_delete_assistant
from .tools.assistant import get_assistant as tools_get_assistant
from .tools.assistant import list_assistants as tools_list_assistants
from .tools.assistant import modify_assistant as tools_modify_assistant
from .tools.messages import MessageContent
from .tools.messages import create_message as tools_create_message
from .tools.messages import delete_message as tools_delete_message
from .tools.messages import get_message as tools_get_message
from .tools.messages import list_messages as tools_list_messages
from .tools.messages import modify_message as tools_modify_message
from .tools.run_steps import get_run_step as tools_get_run_step
from .tools.run_steps import list_run_steps as tools_list_run_steps
from .tools.runs import ToolChoice, TruncationStrategy
from .tools.runs import cancel_run as tools_cancel_run
from .tools.runs import create_run as tools_create_run
from .tools.runs import create_thread_and_run as tools_create_thread_and_run
from .tools.runs import get_run as tools_get_run
from .tools.runs import list_runs as tools_list_runs
from .tools.runs import modify_run as tools_modify_run
from .tools.runs import submit_tool_outputs as tools_submit_tool_outputs
from .tools.threads import create_thread as tools_create_thread
from .tools.threads import delete_thread as tools_delete_thread
from .tools.threads import get_thread as tools_get_thread
from .tools.threads import modify_thread as tools_modify_thread
from .utils.dependencies import get_openai_client


def _configure_logging(settings: Settings) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    # Load settings for initial configuration
    settings = Settings()
    _configure_logging(settings)

    logger = logging.getLogger(__name__)
    logger.info(f"Creating FastMCP server with {settings.TRANSPORT} transport")

    # Create FastMCP server with transport-specific configuration
    if settings.TRANSPORT.lower() == "stdio":
        mcp = FastMCP("openai-assistant-api")
    else:
        # For HTTP and SSE transports, pass host and port
        mcp = FastMCP("openai-assistant-api", host=settings.HOST, port=settings.PORT)

    return mcp


# Create server instance
settings = Settings()
_configure_logging(settings)
logger = logging.getLogger(__name__)

mcp = create_server()


# Assistant Tools
@mcp.tool()
def create_assistant(
    context: Context,
    model: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    instructions: Optional[str] = None,
    tools: Optional[List[Tool]] = None,
    tool_resources: Optional[ToolResources] = None,
    metadata: Optional[Metadata] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    response_format: Optional[ResponseFormat] = None,
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None,
) -> Dict[str, Any]:
    """
    Create an assistant.

    This is typically the first step in the workflow before creating threads
    and messages.

    Args:
        model: (REQUIRED) ID of the model to use
        name: Name of the assistant (max 256 chars)
        description: Description of the assistant (max 512 chars)
        instructions: System instructions (max 256k chars)
        tools: List of tools (max 128 tools)
        tool_resources: Resources for tools
        metadata: Key-value pairs (max 16 pairs)
        temperature: Sampling temperature (0-2)
        top_p: Nucleus sampling parameter (0-1)
        response_format: Output format specification
        reasoning_effort: Reasoning effort level (low/medium/high)

    Returns:
        AssistantObject: The created assistant containing:
        - id: The unique identifier for the assistant
        - object: Always "assistant"
        - created_at: Unix timestamp when the assistant was created
        - model: ID of the model being used
        - name: The assistant's name (max 256 chars)
        - description: The assistant's description (max 512 chars)
        - instructions: System instructions for the assistant (max 256k chars)
        - tools: List of enabled tools (max 128 tools)
        - tool_resources: Resources used by the assistant's tools
        - metadata: Key-value pairs attached to the object
        - temperature: Sampling temperature (0-2)
        - top_p: Nucleus sampling parameter (0-1)
        - response_format: Output format specification
    """
    client = get_openai_client(context)
    return tools_create_assistant(
        client=client,
        model=model,
        name=name,
        description=description,
        instructions=instructions,
        tools=tools,
        tool_resources=tool_resources,
        metadata=metadata,
        temperature=temperature,
        top_p=top_p,
        response_format=response_format,
        reasoning_effort=reasoning_effort,
    )


@mcp.tool()
def get_assistant(context: Context, assistant_id: str) -> Dict[str, Any]:
    """
    Get assistant by ID.

    Use this to retrieve an assistant's configuration after creation.

    Args:
        assistant_id: (REQUIRED) The ID of the assistant to retrieve

    Returns:
        AssistantObject: The assistant containing:
        - id: The unique identifier for the assistant
        - object: Always "assistant"
        - created_at: Unix timestamp when the assistant was created
        - model: ID of the model being used
        - name: The assistant's name (max 256 chars)
        - description: The assistant's description (max 512 chars)
        - instructions: System instructions for the assistant (max 256k chars)
        - tools: List of enabled tools (max 128 tools)
        - tool_resources: Resources used by the assistant's tools
        - metadata: Key-value pairs attached to the object
        - temperature: Sampling temperature (0-2)
        - top_p: Nucleus sampling parameter (0-1)
        - response_format: Output format specification
    """
    client = get_openai_client(context)
    return tools_get_assistant(client, assistant_id)


@mcp.tool()
def list_assistants(
    context: Context,
) -> Dict[str, Any]:
    """List assistants. Use this to view all available assistants."""
    client = get_openai_client(context)
    return tools_list_assistants(client)


@mcp.tool()
def modify_assistant(
    context: Context,
    assistant_id: str,
    model: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    instructions: Optional[str] = None,
    tools: Optional[List[Tool]] = None,
    tool_resources: Optional[ToolResources] = None,
    metadata: Optional[Metadata] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    response_format: Optional[ResponseFormat] = None,
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = None,
) -> Dict[str, Any]:
    """
    Modify an assistant.

    Use this to update an assistant's configuration after creation.

    Args:
        assistant_id: (REQUIRED) The ID of the assistant to modify
        model: ID of the model to use
        name: Name of the assistant (max 256 chars)
        description: Description of the assistant (max 512 chars)
        instructions: System instructions (max 256k chars)
        tools: List of tools (max 128 tools)
        tool_resources: Resources for tools
        metadata: Key-value pairs (max 16 pairs)
        temperature: Sampling temperature (0-2)
        top_p: Nucleus sampling parameter (0-1)
        response_format: Output format specification
        reasoning_effort: Reasoning effort level (low/medium/high)

    Returns:
        AssistantObject: The assistant containing:
        - id: The unique identifier for the assistant
        - object: Always "assistant"
        - created_at: Unix timestamp when the assistant was created
        - model: ID of the model being used
        - name: The assistant's name (max 256 chars)
        - description: The assistant's description (max 512 chars)
        - instructions: System instructions for the assistant (max 256k chars)
        - tools: List of enabled tools (max 128 tools)
        - tool_resources: Resources used by the assistant's tools
        - metadata: Key-value pairs attached to the object
        - temperature: Sampling temperature (0-2)
        - top_p: Nucleus sampling parameter (0-1)
        - response_format: Output format specification
    """
    client = get_openai_client(context)
    return tools_modify_assistant(
        client=client,
        assistant_id=assistant_id,
        model=model,
        name=name,
        description=description,
        instructions=instructions,
        tools=tools,
        tool_resources=tool_resources,
        metadata=metadata,
        temperature=temperature,
        top_p=top_p,
        response_format=response_format,
        reasoning_effort=reasoning_effort,
    )


@mcp.tool()
def delete_assistant(context: Context, assistant_id: str) -> Dict[str, Any]:
    """
    Delete an assistant.

    Permanently removes an assistant and its configuration.

    Args:
        assistant_id: (REQUIRED) The ID of the assistant to delete

    Returns:
        DeleteAssistantResponse: The deletion confirmation containing:
        - id: The ID of the deleted assistant
        - object: Always "assistant.deleted"
        - deleted: Boolean indicating whether the assistant was successfully deleted
    """
    client = get_openai_client(context)
    return tools_delete_assistant(client, assistant_id)


# Thread Tools
@mcp.tool()
def create_thread(
    context: Context,
    messages: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, str]] = None,
    tool_resources: Optional[Union[Dict[str, Any], ToolResources]] = None,
) -> Dict[str, Any]:
    """
    Create a thread.

    This is done after creating an assistant and before adding messages.
    A thread maintains the conversation state between the assistant and user.

    Args:
        messages: List of messages to start the thread with
        metadata: Key-value pairs (max 16 pairs)
        tool_resources: Resources for tools

    Returns:
        ThreadObject: The created thread containing:
        - id: The unique identifier for the thread
        - object: Always "thread"
        - created_at: Unix timestamp when the thread was created
        - metadata: Key-value pairs attached to the thread
        - tool_resources: Resources made available to assistant's tools in this thread
    """
    client = get_openai_client(context)
    return tools_create_thread(client, messages, metadata, tool_resources)


@mcp.tool()
def get_thread(context: Context, thread_id: str) -> Dict[str, Any]:
    """
    Get thread by ID.

    Use this to retrieve a thread's details after creation.

    Args:
        thread_id: (REQUIRED) The ID of the thread to retrieve

    Returns:
        ThreadObject: The thread containing:
        - id: The unique identifier for the thread
        - object: Always "thread"
        - created_at: Unix timestamp when the thread was created
        - metadata: Key-value pairs attached to the thread
        - tool_resources: Resources made available to assistant's tools in this thread
    """
    client = get_openai_client(context)
    return tools_get_thread(client, thread_id)


@mcp.tool()
def modify_thread(
    context: Context,
    thread_id: str,
    metadata: Optional[Dict[str, str]] = None,
    tool_resources: Optional[Union[Dict[str, Any], ToolResources]] = None,
) -> Dict[str, Any]:
    """
    Modify a thread.

    Use this to update a thread's metadata or tool resources.

    Args:
        thread_id: (REQUIRED) The ID of the thread to modify
        metadata: Key-value pairs (max 16 pairs)
        tool_resources: Resources for tools

    Returns:
        ThreadObject: The modified thread containing:
        - id: The unique identifier for the thread
        - object: Always "thread"
        - created_at: Unix timestamp when the thread was created
        - metadata: Key-value pairs attached to the thread
        - tool_resources: Resources made available to assistant's tools in this thread
    """
    client = get_openai_client(context)
    return tools_modify_thread(client, thread_id, metadata, tool_resources)


@mcp.tool()
def delete_thread(context: Context, thread_id: str) -> Dict[str, Any]:
    """
    Delete a thread.

    Permanently removes a thread and all its messages.

    Args:
        thread_id: (REQUIRED) The ID of the thread to delete

    Returns:
        ThreadDeleted: The deletion confirmation containing:
        - id: The ID of the deleted thread
        - object: Always "thread.deleted"
        - deleted: Boolean indicating whether the thread was successfully deleted
    """
    client = get_openai_client(context)
    return tools_delete_thread(client, thread_id)


# Message Tools
@mcp.tool()
def create_message(
    context: Context,
    thread_id: str,
    role: Literal["user", "assistant"],
    content: Union[str, List[MessageContent]],
    attachments: Optional[List[Dict[str, Any]]] = None,
    metadata: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Create a message in a thread.

    Messages are added to threads to build conversations.
    User messages are added when the user sends input, assistant messages
    when the assistant responds.

    Args:
        thread_id: (REQUIRED) The ID of the thread to create a message for
        role: (REQUIRED) The role of the entity creating the message
            ('user' or 'assistant')
        content: (REQUIRED) The content of the message (string or list of content parts)
        attachments: List of file attachments
        metadata: Key-value pairs (max 16 pairs)

    Returns:
        MessageObject: The created message containing:
        - id: The unique identifier for the message
        - object: Always "thread.message"
        - created_at: Unix timestamp when the message was created
        - thread_id: The ID of the thread this message belongs to
        - role: The role of the entity that created the message (user/assistant)
        - content: Array of message content (text, images, etc.)
        - assistant_id: ID of the assistant that authored this message (if applicable)
        - run_id: ID of the run associated with the message (if applicable)
        - completed_at: Unix timestamp when the message was completed
        - incomplete_at: Unix timestamp when the message was marked incomplete
        - incomplete_details: Details about why the message is incomplete
        - status: Message status (in_progress/incomplete/completed)
        - attachments: Files attached to the message
        - metadata: Key-value pairs attached to the message
    """
    client = get_openai_client(context)
    return tools_create_message(
        client=client,
        thread_id=thread_id,
        role=role,
        content=content,
        attachments=attachments,
        metadata=metadata,
    )


@mcp.tool()
def get_message(context: Context, thread_id: str, message_id: str) -> Dict[str, Any]:
    """
    Get message by ID.

    Use this to retrieve a specific message's details from a thread.

    Args:
        thread_id: (REQUIRED) The ID of the thread the message belongs to
        message_id: (REQUIRED) The ID of the message to retrieve

    Returns:
        MessageObject: The message containing:
        - id: The unique identifier for the message
        - object: Always "thread.message"
        - created_at: Unix timestamp when the message was created
        - thread_id: The ID of the thread this message belongs to
        - role: The role of the entity that created the message (user/assistant)
        - content: Array of message content (text, images, etc.)
        - assistant_id: ID of the assistant that authored this message (if applicable)
        - run_id: ID of the run associated with the message (if applicable)
        - completed_at: Unix timestamp when the message was completed
        - incomplete_at: Unix timestamp when the message was marked incomplete
        - incomplete_details: Details about why the message is incomplete
        - status: Message status (in_progress/incomplete/completed)
        - attachments: Files attached to the message
        - metadata: Key-value pairs attached to the message
    """
    client = get_openai_client(context)
    return tools_get_message(client, thread_id, message_id)


@mcp.tool()
def list_messages(
    context: Context,
    thread_id: str,
    limit: Optional[int] = None,
    order: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    run_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List messages for a thread.

    Use this to retrieve the conversation history in a thread.

    Args:
        thread_id: (REQUIRED) The ID of the thread to list messages for
        limit: Limit on number of messages (1-100, default 20)
        order: Sort order ('asc' or 'desc', default 'desc')
        after: Cursor for pagination (get messages after this ID)
        before: Cursor for pagination (get messages before this ID)
        run_id: Filter for messages from a specific run

    Returns:
        MessageListResponse: The list of messages containing:
        - object: Always "list"
        - data: Array of MessageObject items
        - first_id: The ID of the first message in the list
        - last_id: The ID of the last message in the list
        - has_more: Whether there are more messages to fetch
    """
    client = get_openai_client(context)
    return tools_list_messages(
        client=client,
        thread_id=thread_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        run_id=run_id,
    )


@mcp.tool()
def modify_message(
    context: Context,
    thread_id: str,
    message_id: str,
    metadata: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Modify a message.

    Use this to update message metadata after creation.

    Args:
        thread_id: (REQUIRED) The ID of the thread the message belongs to
        message_id: (REQUIRED) The ID of the message to modify
        metadata: Key-value pairs (max 16 pairs)

    Returns:
        MessageObject: The modified message containing:
        - id: The unique identifier for the message
        - object: Always "thread.message"
        - created_at: Unix timestamp when the message was created
        - thread_id: The ID of the thread this message belongs to
        - role: The role of the entity that created the message (user/assistant)
        - content: Array of message content (text, images, etc.)
        - assistant_id: ID of the assistant that authored this message (if applicable)
        - run_id: ID of the run associated with the message (if applicable)
        - completed_at: Unix timestamp when the message was completed
        - incomplete_at: Unix timestamp when the message was marked incomplete
        - incomplete_details: Details about why the message is incomplete
        - status: Message status (in_progress/incomplete/completed)
        - attachments: Files attached to the message
        - metadata: Key-value pairs attached to the message
    """
    client = get_openai_client(context)
    return tools_modify_message(
        client=client,
        thread_id=thread_id,
        message_id=message_id,
        metadata=metadata,
    )


@mcp.tool()
def delete_message(context: Context, thread_id: str, message_id: str) -> Dict[str, Any]:
    """
    Delete a message.

    Permanently removes a message from a thread.

    Args:
        thread_id: (REQUIRED) The ID of the thread the message belongs to
        message_id: (REQUIRED) The ID of the message to delete

    Returns:
        DeleteMessageResponse: The deletion confirmation containing:
        - id: The ID of the deleted message
        - object: Always "thread.message.deleted"
        - deleted: Boolean indicating whether the message was successfully deleted
    """
    client = get_openai_client(context)
    return tools_delete_message(client, thread_id, message_id)


# Run Tools
@mcp.tool()
def create_run(
    context: Context,
    thread_id: str,
    assistant_id: str,
    model: Optional[str] = None,
    instructions: Optional[str] = None,
    additional_instructions: Optional[str] = None,
    tools: Optional[
        List[Union[CodeInterpreterTool, FileSearchTool, FunctionTool]]
    ] = None,
    metadata: Optional[Dict[str, str]] = None,
    stream: Optional[bool] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_completion_tokens: Optional[int] = None,
    max_prompt_tokens: Optional[int] = None,
    response_format: Optional[Union[Literal["auto"], ResponseFormat]] = None,
    tool_choice: Optional[
        Union[Literal["none", "auto", "required"], ToolChoice]
    ] = None,
    truncation_strategy: Optional[TruncationStrategy] = None,
    parallel_tool_calls: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Create a run.

    This starts a new run with the specified assistant in a thread.
    A run represents the assistant processing messages and performing actions.

    Args:
        thread_id: (REQUIRED) The ID of the thread to run
        assistant_id: (REQUIRED) The ID of the assistant to use
        model: Model override for this run
        instructions: Instructions override for this run
        additional_instructions: Additional instructions for this run
        tools: List of tools for this run
        metadata: Key-value pairs (max 16 pairs)
        stream: Boolean for streaming mode
        temperature: Sampling temperature (0-2)
        top_p: Nucleus sampling value (0-1)
        max_completion_tokens: Maximum completion tokens
        max_prompt_tokens: Maximum prompt tokens
        response_format: Response format configuration
        tool_choice: Tool choice configuration
        truncation_strategy: Truncation strategy
        parallel_tool_calls: Boolean for parallel tool calls

    Returns:
        RunObject: The created run containing:
        - id: The unique identifier for the run
        - object: Always "thread.run"
        - created_at: Unix timestamp when the run was created
        - thread_id: The ID of the thread being executed on
        - assistant_id: The ID of the assistant used for execution
        - status: Current status
                (queued/in_progress/requires_action/cancelling/cancelled/
                failed/completed/incomplete/expired)
        - required_action: Details on action required to continue the run
        - last_error: The last error associated with this run
        - expires_at: Unix timestamp when the run will expire
        - started_at: Unix timestamp when the run was started
        - cancelled_at: Unix timestamp when the run was cancelled
        - failed_at: Unix timestamp when the run failed
        - completed_at: Unix timestamp when the run was completed
        - model: The model that the assistant used for this run
        - instructions: The instructions that the assistant used for this run
        - tools: List of tools that the assistant used for this run
        - file_ids: List of File IDs the assistant used for this run
        - metadata: Key-value pairs attached to the run
        - usage: Usage statistics (completion_tokens, prompt_tokens, total_tokens)
        - parallel_tool_calls: Whether parallel function calling is enabled
        - max_completion_tokens: Maximum completion tokens specified
        - max_prompt_tokens: Maximum prompt tokens specified
        - temperature: Sampling temperature used for this run
        - top_p: Nucleus sampling value used for this run
        - response_format: Format specification for model output
        - tool_choice: Controls which tool is called by the model
        - truncation_strategy: Controls for thread truncation prior to run
        - incomplete_details: Details on why the run is incomplete
    """
    client = get_openai_client(context)
    return tools_create_run(
        client=client,
        thread_id=thread_id,
        assistant_id=assistant_id,
        model=model,
        instructions=instructions,
        additional_instructions=additional_instructions,
        tools=tools,
        metadata=metadata,
        stream=stream,
        temperature=temperature,
        top_p=top_p,
        max_completion_tokens=max_completion_tokens,
        max_prompt_tokens=max_prompt_tokens,
        response_format=response_format,
        tool_choice=tool_choice,
        truncation_strategy=truncation_strategy,
        parallel_tool_calls=parallel_tool_calls,
    )


@mcp.tool()
def create_thread_and_run(
    context: Context,
    assistant_id: str,
    thread: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None,
    instructions: Optional[str] = None,
    tools: Optional[
        List[Union[CodeInterpreterTool, FileSearchTool, FunctionTool]]
    ] = None,
    metadata: Optional[Dict[str, str]] = None,
    stream: Optional[bool] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_completion_tokens: Optional[int] = None,
    max_prompt_tokens: Optional[int] = None,
    response_format: Optional[Union[Literal["auto"], ResponseFormat]] = None,
    tool_choice: Optional[
        Union[Literal["none", "auto", "required"], ToolChoice]
    ] = None,
    truncation_strategy: Optional[TruncationStrategy] = None,
    parallel_tool_calls: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Create a thread and run it in one request.

    This combines creating a new thread and starting a run into a single operation.
    Useful when you want to start a fresh conversation with an assistant.

    Args:
        assistant_id: (REQUIRED) The ID of the assistant to use
        thread: Thread configuration
        model: Model override for this run
        instructions: Instructions override for this run
        tools: List of tools for this run
        metadata: Key-value pairs (max 16 pairs)
        stream: Boolean for streaming mode
        temperature: Sampling temperature (0-2)
        top_p: Nucleus sampling value (0-1)
        max_completion_tokens: Maximum completion tokens
        max_prompt_tokens: Maximum prompt tokens
        response_format: Response format configuration
        tool_choice: Tool choice configuration
        truncation_strategy: Truncation strategy
        parallel_tool_calls: Boolean for parallel tool calls

    Returns:
        RunObject: The created run containing:
        - id: The unique identifier for the run
        - object: Always "thread.run"
        - created_at: Unix timestamp when the run was created
        - thread_id: The ID of the thread being executed on
        - assistant_id: The ID of the assistant used for execution
        - status: Current status
                (queued/in_progress/requires_action/cancelling/cancelled/
                failed/completed/incomplete/expired)
        - required_action: Details on action required to continue the run
        - last_error: The last error associated with this run
        - expires_at: Unix timestamp when the run will expire
        - started_at: Unix timestamp when the run was started
        - cancelled_at: Unix timestamp when the run was cancelled
        - failed_at: Unix timestamp when the run failed
        - completed_at: Unix timestamp when the run was completed
        - model: The model that the assistant used for this run
        - instructions: The instructions that the assistant used for this run
        - tools: List of tools that the assistant used for this run
        - file_ids: List of File IDs the assistant used for this run
        - metadata: Key-value pairs attached to the run
        - usage: Usage statistics (completion_tokens, prompt_tokens, total_tokens)
        - parallel_tool_calls: Whether parallel function calling is enabled
        - max_completion_tokens: Maximum completion tokens specified
        - max_prompt_tokens: Maximum prompt tokens specified
        - temperature: Sampling temperature used for this run
        - top_p: Nucleus sampling value used for this run
        - response_format: Format specification for model output
        - tool_choice: Controls which tool is called by the model
        - truncation_strategy: Controls for thread truncation prior to run
        - incomplete_details: Details on why the run is incomplete
    """
    client = get_openai_client(context)
    return tools_create_thread_and_run(
        client=client,
        assistant_id=assistant_id,
        thread=thread,
        model=model,
        instructions=instructions,
        tools=tools,
        metadata=metadata,
        stream=stream,
        temperature=temperature,
        top_p=top_p,
        max_completion_tokens=max_completion_tokens,
        max_prompt_tokens=max_prompt_tokens,
        response_format=response_format,
        tool_choice=tool_choice,
        truncation_strategy=truncation_strategy,
        parallel_tool_calls=parallel_tool_calls,
    )


@mcp.tool()
def list_runs(
    context: Context,
    thread_id: str,
    limit: Optional[int] = None,
    order: Optional[Literal["asc", "desc"]] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
) -> Dict[str, Any]:
    """
    List runs for a thread.

    Use this to view the history of runs in a thread.

    Args:
        thread_id: (REQUIRED) The ID of the thread to list runs for
        limit: Limit on number of runs (1-100, default 20)
        order: Sort order ('asc' or 'desc', default 'desc')
        after: Cursor for pagination (get runs after this ID)
        before: Cursor for pagination (get runs before this ID)

    Returns:
        RunListResponse: The list of runs containing:
        - object: Always "list"
        - data: Array of RunObject items
        - first_id: The ID of the first run in the list
        - last_id: The ID of the last run in the list
        - has_more: Whether there are more runs available
    """
    client = get_openai_client(context)
    return tools_list_runs(
        client=client,
        thread_id=thread_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
    )


@mcp.tool()
def get_run(context: Context, thread_id: str, run_id: str) -> Dict[str, Any]:
    """
    Get run by ID.

    Use this to retrieve details about a specific run.

    Args:
        thread_id: (REQUIRED) The ID of the thread the run belongs to
        run_id: (REQUIRED) The ID of the run to retrieve

    Returns:
        RunObject: The created run containing:
        - id: The unique identifier for the run
        - object: Always "thread.run"
        - created_at: Unix timestamp when the run was created
        - thread_id: The ID of the thread being executed on
        - assistant_id: The ID of the assistant used for execution
        - status: Current status
                (queued/in_progress/requires_action/cancelling/cancelled/
                failed/completed/incomplete/expired)
        - required_action: Details on action required to continue the run
        - last_error: The last error associated with this run
        - expires_at: Unix timestamp when the run will expire
        - started_at: Unix timestamp when the run was started
        - cancelled_at: Unix timestamp when the run was cancelled
        - failed_at: Unix timestamp when the run failed
        - completed_at: Unix timestamp when the run was completed
        - model: The model that the assistant used for this run
        - instructions: The instructions that the assistant used for this run
        - tools: List of tools that the assistant used for this run
        - file_ids: List of File IDs the assistant used for this run
        - metadata: Key-value pairs attached to the run
        - usage: Usage statistics (completion_tokens, prompt_tokens, total_tokens)
        - parallel_tool_calls: Whether parallel function calling is enabled
        - max_completion_tokens: Maximum completion tokens specified
        - max_prompt_tokens: Maximum prompt tokens specified
        - temperature: Sampling temperature used for this run
        - top_p: Nucleus sampling value used for this run
        - response_format: Format specification for model output
        - tool_choice: Controls which tool is called by the model
        - truncation_strategy: Controls for thread truncation prior to run
        - incomplete_details: Details on why the run is incomplete
    """
    client = get_openai_client(context)
    return tools_get_run(client, thread_id=thread_id, run_id=run_id)


@mcp.tool()
def modify_run(
    context: Context,
    thread_id: str,
    run_id: str,
    metadata: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Modify a run.

    Use this to update a run's metadata.

    Args:
        thread_id: (REQUIRED) The ID of the thread the run belongs to
        run_id: (REQUIRED) The ID of the run to modify
        metadata: Key-value pairs (max 16 pairs)

    Returns:
        RunObject: The created run containing:
        - id: The unique identifier for the run
        - object: Always "thread.run"
        - created_at: Unix timestamp when the run was created
        - thread_id: The ID of the thread being executed on
        - assistant_id: The ID of the assistant used for execution
        - status: Current status
                (queued/in_progress/requires_action/cancelling/cancelled/
                failed/completed/incomplete/expired)
        - required_action: Details on action required to continue the run
        - last_error: The last error associated with this run
        - expires_at: Unix timestamp when the run will expire
        - started_at: Unix timestamp when the run was started
        - cancelled_at: Unix timestamp when the run was cancelled
        - failed_at: Unix timestamp when the run failed
        - completed_at: Unix timestamp when the run was completed
        - model: The model that the assistant used for this run
        - instructions: The instructions that the assistant used for this run
        - tools: List of tools that the assistant used for this run
        - file_ids: List of File IDs the assistant used for this run
        - metadata: Key-value pairs attached to the run
        - usage: Usage statistics (completion_tokens, prompt_tokens, total_tokens)
        - parallel_tool_calls: Whether parallel function calling is enabled
        - max_completion_tokens: Maximum completion tokens specified
        - max_prompt_tokens: Maximum prompt tokens specified
        - temperature: Sampling temperature used for this run
        - top_p: Nucleus sampling value used for this run
        - response_format: Format specification for model output
        - tool_choice: Controls which tool is called by the model
        - truncation_strategy: Controls for thread truncation prior to run
        - incomplete_details: Details on why the run is incomplete
    """
    client = get_openai_client(context)
    return tools_modify_run(
        client, thread_id=thread_id, run_id=run_id, metadata=metadata
    )


@mcp.tool()
def submit_tool_outputs(
    context: Context,
    thread_id: str,
    run_id: str,
    tool_outputs: List[Dict[str, str]],
    stream: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Submit outputs for tool calls.

    Use this to provide the results of tool calls back to the assistant.

    Args:
        thread_id: (REQUIRED) The ID of the thread the run belongs to
        run_id: (REQUIRED) The ID of the run to submit outputs for
        tool_outputs: (REQUIRED) List of tool outputs with tool_call_id and output
        stream: Boolean for streaming mode

    Returns:
        RunObject: The created run containing:
        - id: The unique identifier for the run
        - object: Always "thread.run"
        - created_at: Unix timestamp when the run was created
        - thread_id: The ID of the thread being executed on
        - assistant_id: The ID of the assistant used for execution
        - status: Current status
                (queued/in_progress/requires_action/cancelling/cancelled/
                failed/completed/incomplete/expired)
        - required_action: Details on action required to continue the run
        - last_error: The last error associated with this run
        - expires_at: Unix timestamp when the run will expire
        - started_at: Unix timestamp when the run was started
        - cancelled_at: Unix timestamp when the run was cancelled
        - failed_at: Unix timestamp when the run failed
        - completed_at: Unix timestamp when the run was completed
        - model: The model that the assistant used for this run
        - instructions: The instructions that the assistant used for this run
        - tools: List of tools that the assistant used for this run
        - file_ids: List of File IDs the assistant used for this run
        - metadata: Key-value pairs attached to the run
        - usage: Usage statistics (completion_tokens, prompt_tokens, total_tokens)
        - parallel_tool_calls: Whether parallel function calling is enabled
        - max_completion_tokens: Maximum completion tokens specified
        - max_prompt_tokens: Maximum prompt tokens specified
        - temperature: Sampling temperature used for this run
        - top_p: Nucleus sampling value used for this run
        - response_format: Format specification for model output
        - tool_choice: Controls which tool is called by the model
        - truncation_strategy: Controls for thread truncation prior to run
        - incomplete_details: Details on why the run is incomplete
    """
    client = get_openai_client(context)
    return tools_submit_tool_outputs(
        client=client,
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs,
        stream=stream,
    )


@mcp.tool()
def cancel_run(context: Context, thread_id: str, run_id: str) -> Dict[str, Any]:
    """
    Cancel a run.

    Use this to stop a run that is in progress.

    Args:
        thread_id: (REQUIRED) The ID of the thread the run belongs to
        run_id: (REQUIRED) The ID of the run to cancel

    Returns:
        RunObject: The created run containing:
        - id: The unique identifier for the run
        - object: Always "thread.run"
        - created_at: Unix timestamp when the run was created
        - thread_id: The ID of the thread being executed on
        - assistant_id: The ID of the assistant used for execution
        - status: Current status
                (queued/in_progress/requires_action/cancelling/cancelled/
                failed/completed/incomplete/expired)
        - required_action: Details on action required to continue the run
        - last_error: The last error associated with this run
        - expires_at: Unix timestamp when the run will expire
        - started_at: Unix timestamp when the run was started
        - cancelled_at: Unix timestamp when the run was cancelled
        - failed_at: Unix timestamp when the run failed
        - completed_at: Unix timestamp when the run was completed
        - model: The model that the assistant used for this run
        - instructions: The instructions that the assistant used for this run
        - tools: List of tools that the assistant used for this run
        - file_ids: List of File IDs the assistant used for this run
        - metadata: Key-value pairs attached to the run
        - usage: Usage statistics (completion_tokens, prompt_tokens, total_tokens)
        - parallel_tool_calls: Whether parallel function calling is enabled
        - max_completion_tokens: Maximum completion tokens specified
        - max_prompt_tokens: Maximum prompt tokens specified
        - temperature: Sampling temperature used for this run
        - top_p: Nucleus sampling value used for this run
        - response_format: Format specification for model output
        - tool_choice: Controls which tool is called by the model
        - truncation_strategy: Controls for thread truncation prior to run
        - incomplete_details: Details on why the run is incomplete
    """
    client = get_openai_client(context)
    return tools_cancel_run(client, thread_id=thread_id, run_id=run_id)


# Run Step Tools
@mcp.tool()
def list_run_steps(
    context: Context,
    thread_id: str,
    run_id: str,
    limit: Optional[int] = None,
    order: Optional[Literal["asc", "desc"]] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
    include: Optional[List[RunStepInclude]] = None,
) -> Dict[str, Any]:
    """
    List run steps for a run.

    Use this to view the sequence of steps taken during a run.

    Args:
        thread_id: (REQUIRED) The ID of the thread the run belongs to
        run_id: (REQUIRED) The ID of the run to list steps for
        limit: Limit on number of steps (1-100, default 20)
        order: Sort order ('asc' or 'desc', default 'desc')
        after: Cursor for pagination (get steps after this ID)
        before: Cursor for pagination (get steps before this ID)
        include: List of additional fields to include in the response
                Currently only supports
                'step_details.tool_calls[*].file_search.results[*].content'

    Returns:
        RunStepListResponse: The list of run steps containing:
        - object: Always "list"
        - data: Array of RunStepObject items
        - first_id: The ID of the first run step in the list
        - last_id: The ID of the last run step in the list
        - has_more: Whether there are more run steps to fetch
    """
    client = get_openai_client(context)
    return tools_list_run_steps(
        client=client,
        thread_id=thread_id,
        run_id=run_id,
        limit=limit,
        order=order,
        after=after,
        before=before,
        include=include,
    )


@mcp.tool()
def get_run_step(
    context: Context,
    thread_id: str,
    run_id: str,
    step_id: str,
    include: Optional[List[RunStepInclude]] = None,
) -> Dict[str, Any]:
    """
    Get run step by ID.

    Use this to retrieve details about a specific step in a run.

    Args:
        thread_id: (REQUIRED) The ID of the thread the run belongs to
        run_id: (REQUIRED) The ID of the run the step belongs to
        step_id: (REQUIRED) The ID of the run step to retrieve
        include: List of additional fields to include in the response
                Currently only supports
                'step_details.tool_calls[*].file_search.results[*].content'

    Returns:
        RunStepObject: The run step containing:
        - id: The unique identifier for the run step
        - object: Always "thread.run.step"
        - created_at: Unix timestamp when the run step was created
        - run_id: The ID of the run this step is a part of
        - assistant_id: The ID of the assistant associated with this run step
        - thread_id: The ID of the thread this run step is a part of
        - type: The type of run step (message_creation/tool_calls)
        - status: The status of the run step
                (in_progress/cancelled/failed/completed/expired)
        - cancelled_at: Unix timestamp when the run step was cancelled
        - completed_at: Unix timestamp when the run step was completed
        - expired_at: Unix timestamp when the run step expired
        - failed_at: Unix timestamp when the run step failed
        - last_error: The last error associated with this run step
        - metadata: Key-value pairs attached to the run step
        - step_details: The details of the run step (message creation or tool calls)
        - usage: Usage statistics related to the run step
    """
    client = get_openai_client(context)
    return tools_get_run_step(
        client=client,
        thread_id=thread_id,
        run_id=run_id,
        step_id=step_id,
        include=include,
    )


def run_server() -> None:
    """Run the MCP server with the configured transport."""
    logger.info(f"Starting server with {settings.TRANSPORT} transport")
    mcp.run(transport=settings.TRANSPORT)


if __name__ == "__main__":
    run_server()
