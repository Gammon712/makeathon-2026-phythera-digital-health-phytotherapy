-- OPTIONAL DEMO-ONLY RLS EXAMPLE
-- Use only on a database that contains data intended to be publicly readable.
-- Do not apply blindly to an internal or sensitive project.

alter table plants enable row level security;
alter table plant_names enable row level security;
alter table indications enable row level security;
alter table sources enable row level security;
alter table preparations enable row level security;
alter table constituents enable row level security;
alter table plant_constituents enable row level security;
alter table evidence_records enable row level security;
alter table safety_records enable row level security;
alter table constituent_indication_evidence enable row level security;
alter table extraction_runs enable row level security;
alter table mapping_runs enable row level security;
alter table plant_indication_profiles enable row level security;

create policy "public read plants"
on plants for select to anon, authenticated using (true);

create policy "public read plant_names"
on plant_names for select to anon, authenticated using (true);

create policy "public read indications"
on indications for select to anon, authenticated using (true);

create policy "public read sources"
on sources for select to anon, authenticated using (true);

create policy "public read preparations"
on preparations for select to anon, authenticated using (true);

create policy "public read constituents"
on constituents for select to anon, authenticated using (true);

create policy "public read plant_constituents"
on plant_constituents for select to anon, authenticated using (true);

create policy "public read evidence_records"
on evidence_records for select to anon, authenticated using (true);

create policy "public read safety_records"
on safety_records for select to anon, authenticated using (true);

create policy "public read constituent_indication_evidence"
on constituent_indication_evidence for select to anon, authenticated using (true);

create policy "public read extraction_runs"
on extraction_runs for select to anon, authenticated using (true);

create policy "public read mapping_runs"
on mapping_runs for select to anon, authenticated using (true);

create policy "public read plant_indication_profiles"
on plant_indication_profiles for select to anon, authenticated using (true);

-- The ingestion queue is intentionally NOT exposed by this demo policy.
