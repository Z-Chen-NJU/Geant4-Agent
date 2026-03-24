from __future__ import annotations

import sys
import unittest

from core.runtime.types import Geant4RuntimePhase, RuntimeActionStatus, ToolCallRequest
from mcp.geant4.adapter import LocalProcessGeant4Adapter
from mcp.geant4.server import Geant4McpServer


class Geant4McpAdapterTest(unittest.TestCase):
    def test_server_lists_minimal_tools(self) -> None:
        server = Geant4McpServer()
        names = [item["name"] for item in server.list_tools()]
        self.assertEqual(
            names,
            [
                "get_runtime_state",
                "apply_config_patch",
                "initialize_run",
                "run_beam",
                "get_last_log",
            ],
        )

    def test_run_requires_initialization(self) -> None:
        server = Geant4McpServer()
        obs = server.call_tool(ToolCallRequest(tool_name="run_beam", arguments={"events": 10}))
        self.assertEqual(obs.status, RuntimeActionStatus.REJECTED)
        self.assertEqual(obs.runtime_phase, Geant4RuntimePhase.IDLE)

    def test_configure_initialize_and_run(self) -> None:
        server = Geant4McpServer()
        server.call_tool(
            ToolCallRequest(
                tool_name="apply_config_patch",
                arguments={
                    "patch": {
                        "geometry": {"structure": "single_box"},
                        "source": {"particle": "gamma"},
                        "physics_list": {"name": "FTFP_BERT"},
                    }
                },
            )
        )
        init_obs = server.call_tool(ToolCallRequest(tool_name="initialize_run", arguments={}))
        run_obs = server.call_tool(ToolCallRequest(tool_name="run_beam", arguments={"events": 4}))
        self.assertEqual(init_obs.status, RuntimeActionStatus.COMPLETED)
        self.assertEqual(run_obs.status, RuntimeActionStatus.COMPLETED)
        self.assertEqual(run_obs.payload["events"], 4)

    def test_local_process_adapter_executes_command(self) -> None:
        adapter = LocalProcessGeant4Adapter(
            [
                sys.executable,
                "-c",
                "import sys; print('geant4 wrapper ok'); print('argv=' + ' '.join(sys.argv[1:]))",
            ]
        )
        server = Geant4McpServer(adapter=adapter)
        server.call_tool(
            ToolCallRequest(
                tool_name="apply_config_patch",
                arguments={
                    "patch": {
                        "geometry": {"structure": "single_box"},
                        "source": {"particle": "gamma"},
                        "physics_list": {"name": "FTFP_BERT"},
                    }
                },
            )
        )
        init_obs = server.call_tool(ToolCallRequest(tool_name="initialize_run", arguments={}))
        run_obs = server.call_tool(ToolCallRequest(tool_name="run_beam", arguments={"events": 2}))
        log_obs = server.call_tool(ToolCallRequest(tool_name="get_last_log", arguments={}))
        self.assertEqual(init_obs.status, RuntimeActionStatus.COMPLETED)
        self.assertEqual(run_obs.status, RuntimeActionStatus.COMPLETED)
        self.assertEqual(run_obs.payload["returncode"], 0)
        self.assertIn("geant4 wrapper ok", "\n".join(log_obs.payload["lines"]))


if __name__ == "__main__":
    unittest.main()
