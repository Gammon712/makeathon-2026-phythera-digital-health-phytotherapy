# Live n8n synchronization note

One small issue was discovered during final public-export validation:

- the orchestrator's TCM source policy correctly produced an authorization result,
- the TCM subworkflow correctly contained a defense-in-depth authorization guard,
- but the intermediate `Prepare TCM Job` node did not yet pass the authorization fields into the subworkflow.

The public submission export corrects this by passing:

```javascript
source_policy_checked: true,
automated_retrieval_authorized:
  policy.tcm_automated_retrieval_allowed === true,
tcm_source_policy_status:
  policy.tcm_source_policy_status ?? null,
tcm_source_policy_version:
  policy.tcm_source_policy_version ?? null
```

The live n8n workflow should receive the same small patch so that the live system and public repository remain identical.
