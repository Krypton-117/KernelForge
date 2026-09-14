import asyncio, json, tomllib
from pathlib import Path
from datetime import timedelta
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[2]
async def main():
 c=tomllib.loads((ROOT/'.codex/config.toml').read_text(encoding='utf-8-sig'))['mcp_servers']['paperqa']
 p=StdioServerParameters(command=c['command'],args=c['args'],cwd=c['cwd'],env=c.get('env'))
 async with stdio_client(p) as (r,w):
  async with ClientSession(r,w,read_timeout_seconds=timedelta(seconds=120)) as s:
   await s.initialize()
   result=await s.call_tool('retrieve_chunks',{'query':'layer normalization different training cases mini-batch size online regime','k':5})
   assert not result.isError, result
   data=result.structuredContent or json.loads(result.content[0].text)
   (ROOT/'docs/acceptance/end-to-end-retrieval.log').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
   for chunk in data['chunks']:
    print(json.dumps(chunk,ensure_ascii=False))
if __name__=='__main__': asyncio.run(main())
