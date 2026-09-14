"""Section 23 Method Bank acceptance; run retrieval first. Safe to re-run unchanged payload."""
import asyncio, hashlib, json, tomllib
from datetime import datetime, timezone
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/acceptance'
MID='METHOD-MATCH-NORMALIZATION-STATISTICS-TO-EXECUTION'
SID='SOURCE-LAYER-NORMALIZATION-1607-06450'
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
async def call(s,name,args):
 r=await s.call_tool(name,args)
 assert not r.isError, r.content
 return r.structuredContent or json.loads(r.content[0].text)
async def main():
 paper=ROOT/'data/papers/papers/layer-normalization'
 source=paper/'source.tex'
 lines=source.read_text(encoding='utf-8').splitlines()
 assert r'\label{eq:ln}' in lines[126]
 assert 'pure online regime with batch size 1' in lines[129]
 retrieval=json.loads((OUT/'end-to-end-retrieval.log').read_text(encoding='utf-8'))
 assert retrieval['ok'] and retrieval['index_files']['failed']==0
 selected=[c for c in retrieval['chunks'] if 'Layer Normalization' in c['citation'] and 'batch size 1' in c['text']]
 assert selected, 'No cited batch-size-one passage; inspect retrieval before continuing'
 chunk=selected[0]
 provenance=dict(source_id=SID,source_type='paper',title='Layer Normalization',external_id='arxiv:1607.06450',uri='https://arxiv.org/abs/1607.06450',metadata={'paperpipe_name':'layer-normalization','source_path':'data/papers/papers/layer-normalization/source.tex','source_sha256':digest(source),'pdf_sha256':digest(paper/'paper.pdf')},locator='Section 3, equation (3), source.tex lines 117-130; '+chunk['chunk_name'],relation='supports',note='Mean and standard deviation reduce across H hidden units for each case. Generalization and proposed engineering test are agent-derived, not paper conclusions.')
 method=dict(id=MID,title='Match normalization statistics to the execution unit',aphorism='Normalize with statistics available when the model runs.',source_claim='Layer Normalization section 3 computes mean and standard deviation over hidden units within each individual training case; different cases have different statistics, allowing online use with batch size one.',interpretation='For an experiment constrained to individual examples or tiny batches, include per-example layer normalization as a candidate and check that unrelated examples cannot alter its normalization result.',generalized_principle='Choose the population over which state or statistics are computed to match the independence and information available at execution time.',trigger='A proposed model must operate on single examples or unreliable small batches.',scope_level='domain',scope_tags=['machine-learning','normalization','execution-contract'],action_bias='Compare no normalization, batch normalization and per-example layer normalization under fixed training budgets; perturb co-batched examples and inspect per-example outputs.',verification='Confirm the intended hidden-unit reduction axis; test singleton and changed-co-batch inference at fixed weights, specify zero-variance epsilon separately, and compare held-out quality and runtime before adoption.')
 payload={'method':method,'sources':[provenance]}
 (OUT/'end-to-end-candidate.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
 config=tomllib.loads((ROOT/'.codex/config.toml').read_text(encoding='utf-8-sig'))['mcp_servers']['method-bank']
 params=StdioServerParameters(command=config['command'],args=config['args'],cwd=config['cwd'],env=config.get('env'))
 async with stdio_client(params) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   existing=await s.call_tool('method_get',{'method_id':MID})
   if not existing.isError:
    old=existing.structuredContent or json.loads(existing.content[0].text)
    assert all(old[k]==v for k,v in method.items()) and old['sources']==[provenance]
    added=False
   else:
    assert (await call(s,'method_add_candidate',payload))['method_id']==MID
    added=True
   original=await call(s,'method_get',{'method_id':MID})
 async with stdio_client(params) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   search=await call(s,'method_search',{'query':'normalization','scope_levels':['domain'],'scope_tags':['execution-contract'],'status':'candidate'})
   assert any(m['id']==MID for m in search)
   assert all('source_claim' not in m and 'sources' not in m for m in search)
   restored=await call(s,'method_get',{'method_id':MID})
   assert restored==original and restored['status']=='candidate'
   src=await call(s,'source_get',{'source_id':SID})
   assert any(link['method_id']==MID for link in src['locators'])
   assert digest(ROOT/src['metadata']['source_path'])==src['metadata']['source_sha256']
 evidence={'status':'passed','checked_at':datetime.now(timezone.utc).isoformat(),'added_new_candidate_this_run':added,'method_id':MID,'source_id':SID,'fresh_process_retrieval':True,'compact_search':search,'method_get':restored,'source_get':src,'cited_chunk':{'chunk_name':chunk['chunk_name'],'citation':chunk['citation'],'text_sha256':hashlib.sha256(chunk['text'].encode()).hexdigest()},'latex_locator':'source.tex lines 117-130, equation (3)','retrieval_file':'docs/acceptance/end-to-end-retrieval.log'}
 (OUT/'end-to-end-evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
 print(json.dumps(evidence,indent=2))
if __name__=='__main__': asyncio.run(main())
