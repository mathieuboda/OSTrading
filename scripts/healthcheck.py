from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from skills.execution_agent.orders import get_account_info, get_positions  # noqa: E402


def healthcheck() -> dict:
    results: dict = {
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "checks": {},
    }

    try:
        account = get_account_info()
        results["checks"]["alpaca_connection"] = {
            "status": "ok",
            "equity": account.get("equity"),
            "trading_blocked": account.get("trading_blocked"),
        }
    except Exception as e:
        results["checks"]["alpaca_connection"] = {
            "status": "error",
            "error": str(e),
        }

    try:
        positions = get_positions()
        results["checks"]["positions"] = {
            "status": "ok",
            "count": len(positions),
        }
    except Exception as e:
        results["checks"]["positions"] = {
            "status": "error",
            "error": str(e),
        }

    config_path = Path("config/agents.json")
    results["checks"]["config"] = {
        "status": "ok" if config_path.exists() else "missing",
        "path": str(config_path),
    }

    env_required = ["ALPACA_API_KEY", "ALPACA_API_SECRET"]
    env_ok = all(
        os.environ.get(v) not in (None, "", f"your_{v.lower()}_here")
        for v in env_required
    )
    results["checks"]["env_vars"] = {
        "status": "ok" if env_ok else "missing",
        "required": env_required,
    }

    all_ok = all(
        c.get("status") == "ok" for c in results["checks"].values()
    )
    results["status"] = "healthy" if all_ok else "unhealthy"

    return results


def main():
    result = healthcheck()
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["status"] == "healthy" else 1)


if __name__ == "__main__":
    main()
