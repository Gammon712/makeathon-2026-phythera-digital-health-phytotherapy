# Submission package status

## Prepared
- [x] Public-safe Streamlit frontend (current v6 logic)
- [x] PhyThera logo
- [x] Requirements pinned
- [x] Python/Streamlit quick-start instructions
- [x] Docker setup
- [x] Supabase reference schema
- [x] Optional demo read-only RLS example
- [x] Final four n8n workflows imported from latest live exports
- [x] n8n credentials/instance metadata removed
- [x] n8n Code-node JavaScript syntax validated
- [x] TCM default-deny + defense-in-depth authorization synchronized in public workflow export
- [x] Frontend screenshots
- [x] n8n workflow screenshots
- [x] PNG metadata stripped from submission images
- [x] Architecture documentation
- [x] Scoring documentation
- [x] Responsible-AI documentation
- [x] Data/source policy
- [x] Limitations and known prototype gaps
- [x] Team/contribution description
- [x] Medical/scientific/legal disclaimer with severability clause
- [x] MIT licence for project-authored code/docs
- [x] Public-repository privacy checker
- [x] n8n sanitization script

## Final actions before pushing to GitHub
- [ ] Apply the documented TCM authorization-field pass-through patch to the live n8n orchestrator so live and public workflow versions match.
- [ ] Create the public GitHub repository `Gammon712/PhyThera`.
- [ ] Run one final fresh-clone test on the repository.
- [ ] Run `python scripts/check_public_repo.py .` immediately before push.
- [ ] Confirm the exact submission URL required by EthnoHack.

Slides/video are handled separately by the team partner.
