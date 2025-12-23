# MCP Server Setup, Client Configuration, and Testing Guide

This document describes how to:

- Set up and run the MCP server
- Configure it for use with:
  - goose (Block’s Goose)
  - Cursor
  - Langflow (as an MCP client)
- Test that the server is running and responding as expected

All examples assume:

- Your MCP server is implemented in Python with FastMCP (or a similar MCP framework).
- You are running it over HTTPS on `https://localhost:8443`.
- You have already created TLS certificates as described in your SECURITY documentation.

You will need to adjust paths, names, and environment variables to match your project.

---

## 1. MCP Server Setup

### 1.1. Directory Layout (example)

A typical layout might look like:

    <PROJECT_ROOT>/
      pyproject.toml
      fastmcp.json          # optional, if you use FastMCP config
      mcp_server/
        __init__.py
        server.py           # contains your MCP server object
      certs/
        server.crt
        server.key

Your actual server entrypoint can be any importable object, for example:
- `mcp_server.server:mcp`
- `mcp_server.server:app`
- `mcp_server.server:server`

### 1.2. Python Environment and Dependencies

Create and activate a virtual environment (pick your tool: uv, venv, etc.):

    cd <PROJECT_ROOT>

    # Example with uv
    uv venv
    source .venv/bin/activate

    # Install your package + FastMCP
    uv pip install -e .
    uv pip install fastmcp

Or, with plain venv/pip:

    python -m venv .venv
    source .venv/bin/activate
    pip install -e .
    pip install fastmcp

### 1.3. Environment Variables

Define any environment variables your MCP server needs. Common patterns:

- Back-end API configuration (for example, Jira):
  - `JIRA_BASE_URL` — base URL, e.g. `https://your-domain.atlassian.net`
  - `JIRA_EMAIL` — Jira user email
  - `JIRA_API_TOKEN` — API token (keep this secret)
- TLS configuration:
  - `TLS_CERT_FILE` — path to `server.crt`
  - `TLS_KEY_FILE` — path to `server.key`
- Port and host:
  - `MCP_HOST` — e.g. `0.0.0.0` or `127.0.0.1`
  - `MCP_PORT` — e.g. `8443`

You can set these in a `.env` file or your shell:

    export JIRA_BASE_URL="https://your-domain.atlassian.net"
    export JIRA_EMAIL="you@example.com"
    export JIRA_API_TOKEN="your-token"
    export TLS_CERT_FILE="./certs/server.crt"
    export TLS_KEY_FILE="./certs/server.key"
    export MCP_HOST="0.0.0.0"
    export MCP_PORT="8443"

### 1.4. Running the MCP Server (HTTPS)

If you are using FastMCP with a `fastmcp.json` configuration, a common pattern is:

    # Example: run via FastMCP using a config file
    uv run fastmcp run fastmcp.json \
      --host "$MCP_HOST" \
      --port "$MCP_PORT" \
      --cert-file "$TLS_CERT_FILE" \
      --key-file "$TLS_KEY_FILE"

Or, if your server is defined directly in Python, for example `mcp_server/server.py`:

    # fastmcp.json (example)
    {
      "$schema": "https://gofastmcp.com/public/schemas/fastmcp.json/v1.json",
      "source": {
        "path": "mcp_server/server.py",
        "entrypoint": "mcp"
      },
      "environment": {
        "dependencies": []
      }
    }

Run it:

    uv run fastmcp run fastmcp.json \
      --host "$MCP_HOST" \
      --port "$MCP_PORT" \
      --cert-file "$TLS_CERT_FILE" \
      --key-file "$TLS_KEY_FILE"

If you’re not using FastMCP’s CLI, your `server.py` might contain something like:

    from fastmcp import FastMCPServer

    mcp = FastMCPServer(name="Jira MCP Server")

    # ... tool registrations ...

    if __name__ == "__main__":
        mcp.run_http(
            host="0.0.0.0",
            port=8443,
            certfile="./certs/server.crt",
            keyfile="./certs/server.key",
        )

Then run:

    python -m mcp_server.server

Adjust the command to your module name and entrypoint.

---

## 2. Verifying the MCP Server is Running

Before integrating with clients, verify that:

1. The server process is running with no errors.
2. The TLS handshake works.
3. The MCP protocol responds to a client.

### 2.1. Basic Connectivity and TLS Check

Use curl to check the HTTPS port is reachable. This does **not** speak MCP, but confirms TLS and networking.

For a self-signed certificate:

    curl -v --cacert ./certs/server.crt https://localhost:8443/

You should see a successful TLS handshake and an HTTP response (the exact body may vary or be empty).

If you use a CA-issued certificate trusted by your OS:

    curl -v https://localhost:8443/

### 2.2. MCP-Level Testing (Inspector / CLI)

If you have an MCP inspector or a simple MCP client (for example, a small test script using the MCP library), run a basic call like:

- List tools
- Call a very simple tool (e.g., “ping”, “health_check”, or a trivial echo tool)

Conceptually, you want to confirm:

- The MCP handshake succeeds.
- `list_tools` returns the tools you expect (e.g., `search_jira`, `get_issue`, etc.).
- Invoking a tool returns a valid MCP result instead of an error.

Once this works, you are ready to integrate with clients.

#### Tool Reference

- `search_jira` – `jql` (required), optional `maxResults` (default 50) and `startAt` (default 0). JQL is sanitized to reject control characters and pipes.
- `list_jira_issues` – `project` (required), optional `maxResults` (default 50), `startAt` (default 0), and `fields` (defaults to standard fields). Project keys are normalized to uppercase and must be alphanumeric/underscores.
- `get_jira_issue` – `issueKey` (required) and optional `fields` (defaults to standard fields). Issue keys are normalized to uppercase and must match the `PROJ-123` pattern.
- `get_jira_comments` – `issueKey` (required) plus optional pagination (`maxResults` default 50, `startAt` default 0).
- `get_jira_transitions` – `issueKey` (required) for listing available transitions on an issue.
- `get_jira_projects` – optional `maxResults` (default 50) and `startAt` (default 0) for paginated project discovery.
- `create_jira_issue` – `project` and `summary` (required), optional `description` (default empty string) and `issueType` (default `Task`). Summary and type must be non-empty strings.
- `update_jira_issue` – `issueKey` and `fields` object (both required) for updating existing issues.
- `add_jira_comment` – `issueKey` and `body` (both required). Comment bodies are trimmed, must be non-empty, and reject null bytes, pipes, ampersands, and backticks.
- `transition_jira_issue` – `issueKey` and numeric `transitionId` (both required) for status changes.

---

## 3. Configuring the MCP Server in goose

goose can use any MCP server as an extension.

### 3.1. High-Level Approach

You will:

1. Ensure your MCP server can be launched or reached by goose.
2. Add it as a **Custom Extension** (MCP server) in goose.
3. Provide:
   - A **name/ID** for the extension.
   - A **command** and **args** (for local process) or a configuration that points to your HTTPS endpoint, depending on how you prefer to run the server.
   - Any **environment variables** needed (e.g., Jira credentials, TLS env vars if not handled by your shell).
4. Test from a goose chat by invoking one of the tools.

### 3.2. Adding the MCP Server as a goose Extension (Command-based)

This pattern assumes goose will launch the MCP server process for you (stdio MCP):

1. Open goose (Desktop or CLI).
2. Open the **Extensions** or **MCP Servers / Extensions** section.
3. Choose **Add custom extension** (or similar wording).
4. Fill in fields (common pattern):

   - **ID**: `jira-mcp`
   - **Name**: `Jira MCP Server`
   - **Description**: `MCP server providing Jira search and issue tools.`
   - **Command**: `uv`  (or `python`, depending on your setup)
   - **Args** (example using FastMCP):

         run fastmcp run fastmcp.json --host 127.0.0.1 --port 8443 --cert-file ./certs/server.crt --key-file ./certs/server.key

     or, if using a direct Python script:

         -m mcp_server.server

   - **Environment variables**:
     - Add any API credentials or TLS-related env vars you wish goose to set for the server process.

5. Save / add the extension.

### 3.3. Adding the MCP Server as a goose Extension (Already-running HTTPS server)

If you prefer to run the MCP server yourself as a long-lived process (for example, under systemd or docker) and goose supports connecting to remote MCP servers:

1. Start your MCP server independently (as in Section 1.4).
2. In goose, when adding a custom extension:
   - Choose the option for a **remote or hosted MCP server** if available in your version.
   - Provide:
     - **Base URL**: `https://your-hostname:8443`
     - Any required auth headers (if you implement auth).
3. Save / add the extension.

The exact UI labels may vary, but the concept remains:
- Either goose launches the server via a command.
- Or goose connects to a pre-running HTTPS MCP endpoint.

### 3.4. Testing in goose

1. Open a new goose session.
2. Ensure the extension is listed as **enabled / active**.
3. Ask the model something that requires your MCP server, for example:

   - “Use the `jira-mcp` tools to list Jira projects.”
   - Or ask it to call a known tool explicitly (depending on goose’s UI).

4. If the extension is working:
   - goose should show prompts about using the extension’s tools.
   - You should see tool calls and responses in goose’s tool log / output.

If it fails:
- Check extension logs inside goose.
- Verify the server command is correct and the TLS configuration matches.
- Check that environment variables are correctly passed.

---

## 4. Configuring the MCP Server in Cursor

Cursor uses a JSON configuration file called `mcp.json`. This can be:
- Global: `~/.cursor/mcp.json`
- Project-specific: `<PROJECT_ROOT>/.cursor/mcp.json`

### 4.1. Basic File Structure

The standard structure is:

    {
      "mcpServers": {
        "jira-mcp": {
          "command": "uv",
          "args": [
            "run",
            "fastmcp",
            "run",
            "fastmcp.json",
            "--host", "127.0.0.1",
            "--port", "8443",
            "--cert-file", "./certs/server.crt",
            "--key-file", "./certs/server.key"
          ],
          "env": {
            "JIRA_BASE_URL": "https://your-domain.atlassian.net",
            "JIRA_EMAIL": "you@example.com",
            "JIRA_API_TOKEN": "your-token"
          }
        }
      }
    }

Key points:

- `command`: The executable to run (for example, `uv` or `python`).
- `args`: Command-line arguments to start your MCP server.
- `env`: Optional environment variables passed to the server process.

### 4.2. Creating / Editing the Configuration

1. Open Cursor’s settings and locate the MCP config editor (or open the file directly).
2. For a **global** configuration:
   - Edit `~/.cursor/mcp.json`.
3. For a **project-specific** configuration:
   - Create `.cursor/mcp.json` at the root of your project.

Paste or merge in your `mcpServers` configuration.

### 4.3. Using a Remote HTTPS MCP Server in Cursor

If you have a **hosted** MCP server and your version of Cursor supports configuring a server by URL instead of by spawning a process:

1. Open Cursor’s MCP settings (for example, via “MCP Tools” or “Add Custom MCP”).
2. Add a new MCP server entry named `jira-mcp` (or similar).
3. Provide:
   - The **hosted MCP URL** (e.g. `https://your-hostname:8443`).
   - Any required headers or auth configuration.
4. Save the configuration.

The details differ by version, but the idea is:
- Either Cursor launches the server via `command` + `args`.
- Or it connects to a remote HTTPS MCP endpoint you manage.

### 4.4. Testing in Cursor

1. Restart Cursor so it reloads the MCP configuration.
2. In Cursor’s chat, ensure that:
   - The MCP server appears in the list of tools / MCP servers.
3. Ask Cursor something that should trigger your MCP tools, for example:

   - “Use the `jira-mcp` tools to search for the 5 most recent issues in project MAX.”

4. Watch the “MCP Tools” / “Tools” pane:
   - You should see tool calls to `jira-mcp`.
   - If there is an error, Cursor usually shows logs or an error message explaining the failure.

Common problems:
- Incorrect path or command in `mcp.json`.
- Missing dependencies in the environment.
- TLS issues (e.g., self-signed cert not trusted by Cursor/OS).
- Incorrect env vars (e.g., wrong API token).

---

## 5. Configuring the MCP Server in Langflow (as Client)

Langflow can act as an MCP client and connect to external MCP servers (including yours).

### 5.1. Starting Langflow

1. Install Langflow (Desktop or via pip) according to its docs.
2. Run Langflow and access the web UI (often `http://localhost:<port>`).

### 5.2. Registering Your MCP Server in Langflow

The exact UI may change, but the workflow is typically:

1. In Langflow’s UI, open the **MCP** or **MCP Client** section.
2. Add a new MCP connection:
   - **Name**: `jira-mcp`
   - **Base URL / Endpoint**: `https://your-hostname:8443`
   - **Auth**:
     - If your MCP server implements auth, configure the required headers (e.g., API key).
     - If there is no auth (dev only), choose “None” as the auth mode.
3. Save the MCP connection.

If Langflow supports importing an MCP JSON configuration, you can also generate a standard `mcpServers` entry and import or manually translate it into Langflow’s MCP client settings.

### 5.3. Using MCP Tools in a Langflow Flow

Once the MCP server is registered:

1. Create a new flow.
2. Add an **LLM** node (for your model: local, OpenAI, etc.).
3. Add an **MCP Tools** node (or similar) and configure it to use:
   - The `jira-mcp` MCP connection you created.
   - Specific tools (for example, `search_jira`, `get_issue`) exposed by your server.
4. Wire the MCP Tools node into your flow, for example:
   - Prompt → LLM → MCP Tools → LLM → Output, depending on your pattern.

### 5.4. Testing in Langflow

1. Set test input for your flow (for example, a query like “Find the last 5 issues in project MAX”).
2. Run the flow.
3. In the execution logs and node outputs, verify that:
   - Langflow successfully connects to the MCP server.
   - The MCP tools receive requests and return responses.
   - Any error messages include useful details (connection failed, TLS error, tool not found, etc.).

If you see TLS or connection errors:
- Confirm the MCP server base URL and port.
- Verify certificates (especially if using self-signed).
- Ensure any required auth headers or API keys are correctly set.

---

## 6. End-to-End Testing Checklist

Use this checklist to validate that your MCP server is correctly configured and usable from goose, Cursor, and Langflow.

### 6.1. Server-Level

- [ ] The MCP server process starts without errors.
- [ ] HTTPS endpoint is reachable:
  - `curl -v --cacert server.crt https://localhost:8443/` succeeds (for self-signed).
- [ ] A basic MCP client or inspector can:
  - [ ] List tools.
  - [ ] Successfully call a trivial tool.

### 6.2. goose Integration

- [ ] MCP server added as a custom extension (command-based or remote HTTPS).
- [ ] Required env vars (e.g., API tokens) configured in the extension.
- [ ] From a goose chat:
  - [ ] The extension is listed as active.
  - [ ] A tool call from the extension returns a valid result (for example, a Jira search).

### 6.3. Cursor Integration

- [ ] `~/.cursor/mcp.json` or `.cursor/mcp.json` contains a `mcpServers` entry for `jira-mcp`.
- [ ] `command` and `args` correctly start the server, or:
  - [ ] Cursor is configured to use a hosted MCP URL.
- [ ] Cursor reloads configuration with no errors.
- [ ] In a Cursor chat:
  - [ ] Tools from `jira-mcp` are visible and can be invoked.
  - [ ] A sample tool call (e.g., Jira search) succeeds.

### 6.4. Langflow Integration

- [ ] MCP client configuration added in Langflow for `jira-mcp`.
- [ ] Base URL and any auth headers set correctly.
- [ ] A flow using the MCP Tools node:
  - [ ] Connects to `jira-mcp`.
  - [ ] Invokes one or more tools.
  - [ ] Receives expected results without TLS or auth errors.

---

## 7. Tips and Common Pitfalls

- If using **self-signed certificates**:
  - Remember to trust the certificate in each environment (OS, tool, or client).
  - For development, you can often specify a custom CA file (`--cacert` in curl, or equivalent in clients).
- If using a **public / CA-issued certificate**:
  - Ensure your certificate chain is complete (leaf + intermediates).
- If any of the clients fail to connect:
  - Check for port, hostname, or firewall issues.
  - Review logs in the MCP server process.
  - Check each client’s MCP logs or tool logs for error messages.

Once all three clients (goose, Cursor, Langflow) can successfully list and invoke your MCP tools, your MCP server is fully integrated and ready to be used in your workflows.
