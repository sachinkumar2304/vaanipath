import asyncio
from typing import Any, Dict

from .utils import setup_logger
from .app import (
    run_job,
    get_manifest,
    list_chunks,
    get_chunk_detail,
    reprocess_chunk,
    get_job_stats,
)

logger = setup_logger("mcp_server")


# Basic MCP server using the 'mcp' library
# Note: This is a minimal implementation; depending on MCP client expectations,
# you may need to adapt tool schemas.
try:
    from mcp.server import Server
    from mcp.types import Tool, ToolOutput
except Exception:
    Server = None
    Tool = None
    ToolOutput = None


async def start_server() -> None:
    if Server is None:
        raise RuntimeError("mcp library not installed; please install 'mcp' to run the server")

    server = Server(name="localizer")

    @server.tool("localizer.start_job")
    async def t_start_job(input_path: str, source: str, target: str, job_id: str, course_id: str, mode: str = "fast") -> Dict[str, Any]:
        logger.info(f"start_job: job_id={job_id} mode={mode}")
        manifest_path = run_job(
            input_path=input_path,
            source=source,
            target=target,
            job_id=job_id,
            course_id=course_id,
            mode=mode,
        )
        return {"manifest_path": manifest_path}

    @server.tool("localizer.get_manifest")
    async def t_get_manifest(job_id: str) -> Dict[str, Any]:
        return get_manifest(job_id)

    @server.tool("localizer.list_chunks")
    async def t_list_chunks(job_id: str) -> Dict[str, Any]:
        return {"chunks": list_chunks(job_id)}

    @server.tool("localizer.get_chunk_detail")
    async def t_get_chunk_detail(job_id: str, chunk_index: int) -> Dict[str, Any]:
        return get_chunk_detail(job_id, chunk_index)

    @server.tool("localizer.reprocess_chunk")
    async def t_reprocess_chunk(job_id: str, chunk_index: int, target_lang: str, mode: str = "fast") -> Dict[str, Any]:
        return reprocess_chunk(job_id, chunk_index, target_lang, mode)

    @server.tool("localizer.get_job_stats")
    async def t_get_job_stats(job_id: str) -> Dict[str, Any]:
        return get_job_stats(job_id)

    await server.run()


if __name__ == "__main__":
    asyncio.run(start_server())