"""Execute the portfolio notebooks in fresh kernels using this Python environment."""

from __future__ import annotations

import argparse
import json
import os
import queue
import sys
import time
from pathlib import Path

from jupyter_client import KernelManager


ROOT = Path(__file__).resolve().parents[1]


def execute_cell(client, source: str, timeout: float):
    message_id = client.execute(source, stop_on_error=True)
    outputs = []
    execution_count = None
    deadline = time.monotonic() + timeout
    while True:
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Cell exceeded {timeout:g} seconds.")
        try:
            message = client.get_iopub_msg(timeout=5)
        except queue.Empty:
            continue
        if message.get("parent_header", {}).get("msg_id") != message_id:
            continue
        kind, content = message["header"]["msg_type"], message["content"]
        if kind == "execute_input":
            execution_count = content["execution_count"]
        elif kind == "stream":
            outputs.append({"output_type": "stream", "name": content["name"],
                            "text": content["text"].splitlines(keepends=True)})
        elif kind in {"execute_result", "display_data"}:
            output = {"output_type": kind, "data": content["data"], "metadata": content["metadata"]}
            if kind == "execute_result":
                output["execution_count"] = content["execution_count"]
            outputs.append(output)
        elif kind == "error":
            raise RuntimeError("\n".join(content["traceback"]))
        elif kind == "status" and content["execution_state"] == "idle":
            break
        elif kind == "clear_output":
            outputs.clear()
    while True:
        reply = client.get_shell_msg(timeout=30)
        if reply.get("parent_header", {}).get("msg_id") != message_id:
            continue
        if reply["content"]["status"] != "ok":
            raise RuntimeError(str(reply["content"]))
        return outputs, execution_count


def run_notebook(path: Path, timeout: float = 600) -> dict:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    sources = [(cell["cell_type"], cell["source"]) for cell in notebook["cells"]]
    manager = KernelManager(kernel_name="python3")
    manager.kernel_spec.argv[0] = sys.executable
    manager.start_kernel(cwd=str(ROOT), env=dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONNOUSERSITE="1"))
    client = manager.client()
    client.start_channels()
    started = time.monotonic()
    executed = 0
    try:
        client.wait_for_ready(timeout=60)
        execute_cell(client, "%matplotlib inline", timeout)
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            print(f"{path.name}: running code cell {index + 1}/{len(notebook['cells'])}", flush=True)
            cell["outputs"], cell["execution_count"] = execute_cell(client, "".join(cell["source"]), timeout)
            cell["metadata"].pop("execution", None)
            executed += 1
        current = json.loads(path.read_text(encoding="utf-8"))
        if sources != [(cell["cell_type"], cell["source"]) for cell in current["cells"]]:
            raise RuntimeError(f"{path.name} changed during execution; refusing to overwrite it.")
        notebook["metadata"]["kernelspec"] = {"display_name": "Python 3.14", "language": "python", "name": "python3"}
        notebook["metadata"].setdefault("language_info", {})["version"] = sys.version.split()[0]
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        stderr_outputs = sum(output.get("name") == "stderr" for cell in notebook["cells"]
                             for output in cell.get("outputs", []))
        result = {"notebook": path.name, "code_cells": executed,
                  "seconds": round(time.monotonic() - started, 1), "stderr_outputs": stderr_outputs}
        print(f"Completed: {result}", flush=True)
        return result
    finally:
        client.stop_channels()
        manager.shutdown_kernel(now=True)


def main():
    if sys.version_info[:2] != (3, 14):
        raise SystemExit("Use Python 3.14 with the packages in requirements.txt.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", default=["main.ipynb", "trend_analysis.ipynb"])
    parser.add_argument("--timeout", type=float, default=600, help="Maximum seconds per code cell.")
    args = parser.parse_args()
    for name in args.notebooks:
        path = (ROOT / name).resolve()
        if path.parent != ROOT or path.suffix != ".ipynb" or not path.is_file():
            parser.error(f"Expected a notebook in the repository root: {name}")
        run_notebook(path, args.timeout)


if __name__ == "__main__":
    main()
