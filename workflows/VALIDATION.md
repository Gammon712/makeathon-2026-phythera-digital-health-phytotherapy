# Workflow validation and public-export notes

The workflow JSON files in this directory are sanitized public exports of the final EthnoHack prototype.

## Removed from public exports
- n8n credential bindings,
- credential IDs and credential names,
- n8n instance IDs,
- top-level workflow IDs/version IDs,
- pinned execution data,
- webhook IDs,
- instance-specific subworkflow IDs and cached workflow URLs.

## Import requirement
After importing the four workflows into a new n8n instance, manually relink the three `Execute Workflow` nodes in the Plant Batch Orchestrator to:
- EMA Ingestion,
- Traditional/TCM Ingestion,
- Cross-Cultural Mapping.

## TCM source authorization
The public export includes defense in depth:
1. the orchestrator applies a default-deny source policy,
2. only an explicitly allowed source passes the policy branch,
3. the authorization state is passed into the TCM subworkflow,
4. the TCM subworkflow independently requires both `source_policy_checked=true` and `automated_retrieval_authorized=true` before making an HTTP request.

This public export includes a small synchronization fix to pass those explicit authorization fields from the orchestrator into the TCM subworkflow.

## Validation
All JSON files parse successfully, and all n8n Code-node JavaScript in the public exports passes `node --check`.

The workflows remain research-prototype code. Test imports and credentials in a non-production environment before use.
