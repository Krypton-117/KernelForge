"""Preload PaperQA before upstream FastMCP starts worker threads on Windows."""
import os
os.environ.setdefault('LITELLM_LOCAL_MODEL_COST_MAP', 'True')
import paperqa  # noqa: F401 -- deliberately load native dependencies before the event loop
from paperpipe.paperqa_mcp_server import main

if __name__ == '__main__':
    main()
