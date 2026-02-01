# PR Strategy - OpenHands Windows Stability & UX Fixes

I have identified 3 logical fixes that should be split into separate, atomic Pull Requests to ensure a clean upstreaming process.

## Logical Buckets

### 1. Fix: Docker Sandbox Port Conflict on Windows
- **Branch:** [fix/windows-sandbox-port-conflict](file:///c:/dev_ai/OpenHands#fix/windows-sandbox-port-conflict)
- **Files:** [docker_sandbox_service.py](file:///c:/dev_ai/OpenHands/openhands/app_server/sandbox/docker_sandbox_service.py)
- **Description:**
  - Restricts `_find_unused_port` to a safer range (10000-49151) to avoid Windows-reserved ports (Hyper-V, etc.).
  - Adds a retry loop (up to 3 times) in `start_sandbox` to handle "ports are not available" errors gracefully by picking new ports.

### 2. Fix: Docker Image Pull Race Condition
- **Branch:** [fix/docker-pull-race-condition](file:///c:/dev_ai/OpenHands#fix/docker-pull-race-condition)
- **Files:** [docker_sandbox_spec_service.py](file:///c:/dev_ai/OpenHands/openhands/app_server/sandbox/docker_sandbox_spec_service.py)
- **Description:**
  - Introduces an `asyncio.Lock` to serialize concurrent image pull requests.
  - Ensures `pull_if_missing` is set to `False` even on failure to prevent infinite retry loops.
  - Improves exception handling to verify image existence if the Docker API returns a 500.

### 3. Fix: Settings Fallback to Config Defaults
- **Branch:** [fix/settings-fallback](file:///c:/dev_ai/OpenHands#fix/settings-fallback)
- **Files:** [default_user_auth.py](file:///c:/dev_ai/OpenHands/openhands/server/user_auth/default_user_auth.py)
- **Description:**
  - Updates `get_user_settings` to fall back to `Settings.from_config()` if the database store is empty.
  - Prevents the UI from redirecting to `/settings` when no settings are persisted yet.

### 4. Other Changes (Committed to main)
- **.gitignore**: Updated to exclude local `.agent/` and `*.code-workspace` files.

## Execution Plan
1. Create atomic branches from `main`.
2. Cherry-pick / Restore relevant changes from `backup/dev-state-20260130-2055`.
3. Verify each branch builds and passes basic checks.
4. Prepare for PR submission.
