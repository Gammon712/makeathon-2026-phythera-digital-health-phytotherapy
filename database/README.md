# Database setup

PhyThera uses Supabase/PostgreSQL as its persistent data layer.

## Recreate the reference schema

1. Create a new Supabase project.
2. Open the Supabase SQL editor.
3. Run `schema.sql`.
4. Configure Row Level Security for your deployment.
5. Use a **publishable/anon key** in the public frontend. Never expose a service-role/secret key.

`rls_demo_readonly.sql` is an **optional demonstration-only** example for a database that contains only public research data. Review it before use.

## Why no database dump?

The repository intentionally contains schema but no complete production database dump. Source-derived records can carry third-party licensing, reuse, provenance, or access restrictions. Reproducibility is therefore provided through:
- schema,
- workflow definitions,
- scoring rules,
- source provenance,
- setup instructions.

Populate a new database only with data you are entitled to store and reuse.
