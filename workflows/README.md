# n8n workflows

PhyThera uses one main workflow and three specialized subworkflows:

1. `phythera_plant_batch_orchestrator.json`
2. `ema_ingestion.json`
3. `traditional_tcm_ingestion.json`
4. `cross_cultural_mapping.json`

## Public-export policy

The public JSON exports intentionally remove:
- credential bindings,
- credential IDs/names,
- n8n instance IDs,
- workflow version IDs,
- private instance URLs,
- pinned execution data,
- top-level workflow IDs.

`Execute Workflow` nodes should be relinked manually after import because subworkflow IDs are instance-specific.

## After importing into n8n

1. Configure your own Supabase credential.
2. Configure your own LLM/OpenRouter credential.
3. Relink the EMA, traditional-source and mapping subworkflows in the orchestrator.
4. Verify source-policy settings before enabling automated traditional-source retrieval.
5. Run with test data before activating a production queue.

The sanitized exports in this directory are based on the latest submitted live workflow versions.
