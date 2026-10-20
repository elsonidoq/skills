"""Historical optional task context fixtures; no executable admission authority."""
import json

from coherence_workflow.intake import content_hash
from coherence_workflow.store import digest


def approval_scope(contract, config_hash):
    # Historical optional metadata fixture; no runtime admission consumer.
    return digest({'contract': contract, 'config_hash': config_hash})


def approved_fixture(project, config_hash, origin='TinySpec'):
    kinds = ['spec','plan','tasks','review'] if origin == 'Standard' else ['source','tasks']
    sources = []
    for kind in kinds:
        path = project / ('input-' + kind + '.json')
        path.write_text(json.dumps({'kind':kind,'scope':'isolated mandatory test only'}))
        sources.append({'path':path.name,'section':None,'sha256':content_hash(path),'kind':kind})
    def task(id, order, depends, path, text):
        return {'id':id,'order':order,'outcome':'Read '+path+' then replace its complete bytes with exactly '+repr(text),
            'depends':depends,'context_group':'story','owned_paths':[path], 'authorization_envelope_id':'isolated',
            'required':[{'id':id+'/V1','criterion':'Exact authorized file bytes','check':{'id':'workflow.FileBytes','version':'1',
                'args':{'path':path,'expected':text}},'pass_condition':'exact byte oracle exits 0','expected_evidence':'real file oracle',
                'producer_dependencies':depends,'gates':[]}], 'optional':[], 'gates':[]}
    contract = {'schema_version':1,'origin':origin,'legacy_origin':'documented-structured-v1' if origin=='legacy' else None,
        'sources':sources,'approval_refs':[], 'tasks':[task('A',0,[],'owned.txt','first\n'),task('B',1,['A'],'second.txt','second\n')],
        'execution_intent':{'model_class':'Sol','effort':'medium','resolution':'resolved',
            'assumptions':['Bounded exact-byte fixture; all acceptance and safety gates retained'],
            'provenance':'Current isolated-test authority; synthetic planning intent, not historical production approval',
            'decomposition_rationale':'Explicit file bytes and dependency order; routine editing choices remain open',
            'compatible_bindings':[{'provider':'openai-codex','model':'gpt-6.1-sol','effort':'medium',
                'assessment':'Exact owner-selected isolated implementation binding; no capability ranking inferred',
                'provenance':'Current owner preapproval for mandatory isolated tests'}]},
        'authorization_envelope':{'id':'isolated','approval_refs':[],'profiles':[],
            'capabilities':[], 'limits':[], 'external_paid_authority':'denied'}}
    catalog = {}
    for kind in {'TinySpec':['combined','implementation'],'Standard':['specification','overall','implementation'],
                 'legacy':['legacy','implementation']}[origin]:
        path = project / ('owner-' + kind + '.txt')
        path.write_text('TEST AUTHORITY: mandatory isolated fixture scope. Current owner preapproved isolated tests; not production acceptance.\n')
        scope = (next(s['sha256'] for s in sources if s['kind']=='spec') if kind=='specification' else
                 approval_scope(contract,config_hash) if kind=='implementation' else digest(sources))
        ref = {'gate_kind':kind,'record_ref':path.name,'record_sha256':content_hash(path),'scope_hash':scope,
               'actor':'fixture catalog: current owner isolated-test preapproval','authority_ref':'external-owner/'+kind,'action':'approve'}
        contract['approval_refs'].append(ref)
        catalog[ref['authority_ref']] = {k:ref[k] for k in ('actor','record_ref','record_sha256','scope_hash','gate_kind','action')}

    for ref in contract['approval_refs']:
        if ref['gate_kind']=='implementation':
            ref['scope_hash']=approval_scope(contract,config_hash)
            catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
    return contract, catalog
