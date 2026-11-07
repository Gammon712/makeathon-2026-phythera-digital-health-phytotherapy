import json
import os

import streamlit as st
from supabase import create_client, Client


# ==================================================
# SUPABASE
# ==================================================

@st.cache_resource
def get_supabase() -> Client:
    """Create the read-only Supabase client used by the frontend.

    Configuration can be provided either via environment variables
    or Streamlit secrets. Never place a Supabase service-role/secret
    key in a public frontend or commit it to version control.
    """

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        try:
            supabase_secrets = st.secrets["supabase"]
            url = url or supabase_secrets.get("url")
            key = (
                key
                or supabase_secrets.get("key")
                or supabase_secrets.get("publishable_key")
                or supabase_secrets.get("anon_key")
            )
        except Exception:
            pass

    if not url or not key:
        raise RuntimeError(
            "Supabase configuration missing. Set SUPABASE_URL and "
            "SUPABASE_KEY, or provide [supabase] url/key in "
            ".streamlit/secrets.toml."
        )

    return create_client(url, key)


# ==================================================
# HELPERS
# ==================================================

def normalize(value):

    if value is None:
        return ""

    return str(value).strip().lower()


def parse_json_value(value):

    parsed = value

    for _ in range(3):

        if not isinstance(parsed, str):
            break

        try:
            parsed = json.loads(parsed)

        except json.JSONDecodeError:
            break

    return parsed


def match_score(query, value):

    query = normalize(query)
    value = normalize(value)

    if not query or not value:
        return None

    if query == value:
        return 0

    if value.startswith(query) or query.startswith(value):
        return 1

    if query in value or value in query:
        return 2

    return None


def as_float(value):

    if value is None:
        return None

    try:
        return float(value)

    except (TypeError, ValueError):
        return None


# ==================================================
# BASE DATA
# ==================================================

@st.cache_data(ttl=300)
def get_plants():

    return (
        get_supabase()
        .table("plants")
        .select(
            "id, scientific_name, family, common_names, "
            "description, metadata"
        )
        .order("scientific_name")
        .execute()
        .data
    )


@st.cache_data(ttl=300)
def get_plant_names():

    return (
        get_supabase()
        .table("plant_names")
        .select(
            "plant_id, name, language_code, "
            "name_type, traditional_system"
        )
        .execute()
        .data
    )


@st.cache_data(ttl=300)
def get_constituents():

    return (
        get_supabase()
        .table("constituents")
        .select(
            "id, name, compound_group, "
            "description, metadata"
        )
        .order("name")
        .execute()
        .data
    )


@st.cache_data(ttl=300)
def get_plant_constituents():

    return (
        get_supabase()
        .table("plant_constituents")
        .select(
            "plant_id, constituent_id, source_id, "
            "plant_part, proposed_role, evidence_note"
        )
        .execute()
        .data
    )


@st.cache_data(ttl=300)
def get_sources():

    return (
        get_supabase()
        .table("sources")
        .select("*")
        .execute()
        .data
    )


# ==================================================
# INDICATIONS
# ==================================================

@st.cache_data(ttl=300)
def get_indications():

    return (
        get_supabase()
        .table("indications")
        .select(
            "id, normalized_term, display_name, "
            "synonyms, icd11_code, description"
        )
        .order("display_name")
        .execute()
        .data
    )


@st.cache_data(ttl=300)
def get_valid_mapping_plant_ids():

    mappings = (
        get_supabase()
        .table("mapping_runs")
        .select(
            "plant_id, ema_run_id, "
            "tcm_run_id, created_at"
        )
        .order(
            "created_at",
            desc=True,
        )
        .execute()
        .data
    )

    runs = (
        get_supabase()
        .table("extraction_runs")
        .select(
            "id, plant_id"
        )
        .execute()
        .data
    )

    run_plant = {
        run["id"]:
            run["plant_id"]
        for run
        in runs
    }

    valid_plants = set()

    for mapping in mappings:

        plant_id = (
            mapping.get(
                "plant_id"
            )
        )

        ema_plant = (
            run_plant.get(
                mapping.get(
                    "ema_run_id"
                )
            )
        )

        tcm_plant = (
            run_plant.get(
                mapping.get(
                    "tcm_run_id"
                )
            )
        )

        if (
            plant_id
            and ema_plant == plant_id
            and tcm_plant == plant_id
        ):

            valid_plants.add(
                plant_id
            )

    return list(
        valid_plants
    )


@st.cache_data(ttl=300)
def get_plant_indication_profiles():

    rows = (
        get_supabase()
        .table("plant_indication_profiles")
        .select("*")
        .execute()
        .data
    )

    score_fields = [
        "evidence_relevance_score",
        "traditional_support_score",
        "modern_evidence_score",
        "source_convergence_score",
    ]

    valid_mapping_plants = set(
        get_valid_mapping_plant_ids()
    )

    for row in rows:

        for field in score_fields:

            row[field] = as_float(
                row.get(field)
            )

        if (
            row.get(
                "source_convergence_score"
            )
            is not None
            and row.get(
                "plant_id"
            )
            not in valid_mapping_plants
        ):

            row[
                "source_convergence_score"
            ] = None

    return rows


def search_indications(query):

    query = normalize(query)

    if len(query) < 2:
        return []

    results = []

    for indication in get_indications():

        terms = [
            indication.get(
                "display_name"
            ),
            indication.get(
                "normalized_term"
            ),
            *(
                indication.get(
                    "synonyms"
                )
                or []
            ),
        ]

        scores = []
        matched_terms = []

        for term in terms:

            score = match_score(
                query,
                term,
            )

            if score is not None:

                scores.append(score)
                matched_terms.append(term)

        if scores:

            results.append(
                {
                    **indication,

                    "match_score":
                        min(scores),

                    "matched_terms":
                        matched_terms,
                }
            )

    results.sort(
        key=lambda item: (
            item["match_score"],
            item["display_name"].lower(),
        )
    )

    return results


def get_ranked_plants_for_indication(
    query,
):

    indication_matches = (
        search_indications(
            query
        )
    )

    if not indication_matches:

        return {
            "indications": [],
            "results": [],
        }

    matched_ids = {
        item["id"]
        for item
        in indication_matches
    }

    plants_by_id = {
        plant["id"]: plant
        for plant
        in get_plants()
    }

    profiles = (
        get_plant_indication_profiles()
    )

    results = []

    for profile in profiles:

        if (
            profile.get(
                "indication_id"
            )
            not in matched_ids
        ):
            continue

        plant = plants_by_id.get(
            profile.get(
                "plant_id"
            )
        )

        if not plant:
            continue

        indication = next(
            item
            for item
            in indication_matches
            if item["id"]
            ==
            profile[
                "indication_id"
            ]
        )

        results.append(
            {
                "plant":
                    plant,

                "indication":
                    indication,

                "profile":
                    profile,
            }
        )

    results.sort(
        key=lambda item: (
            item["profile"].get(
                "evidence_relevance_score"
            )
            is None,

            -(
                item["profile"].get(
                    "evidence_relevance_score"
                )
                or 0
            ),

            item[
                "plant"
            ][
                "scientific_name"
            ].lower(),
        )
    )

    return {
        "indications":
            indication_matches,

        "results":
            results,
    }


# ==================================================
# PLANT / CONSTITUENT SEARCH
# ==================================================

def search_plants_and_constituents(
    query,
):

    query = normalize(query)

    if len(query) < 2:
        return []

    plants = get_plants()
    plant_names = get_plant_names()
    constituents = get_constituents()

    plant_constituents = (
        get_plant_constituents()
    )

    plants_by_id = {
        plant["id"]: plant
        for plant
        in plants
    }

    aliases_by_plant = {}

    for record in plant_names:

        aliases_by_plant.setdefault(
            record["plant_id"],
            [],
        ).append(
            record["name"]
        )

    results = []

    # --------------------------------------------------
    # Plants
    # --------------------------------------------------

    for plant in plants:

        aliases = (
            aliases_by_plant.get(
                plant["id"],
                [],
            )
        )

        common_names = (
            plant.get(
                "common_names"
            )
            or []
        )

        terms = [
            plant.get(
                "scientific_name"
            ),
            *common_names,
            *aliases,
        ]

        scores = []
        matched_terms = []

        for term in terms:

            score = match_score(
                query,
                term,
            )

            if score is not None:

                scores.append(score)
                matched_terms.append(
                    term
                )

        if scores:

            results.append(
                {
                    "result_type":
                        "plant",

                    "id":
                        plant["id"],

                    "plant_id":
                        plant["id"],

                    "title":
                        plant[
                            "scientific_name"
                        ],

                    "family":
                        plant.get(
                            "family"
                        ),

                    "common_names":
                        common_names,

                    "aliases":
                        aliases,

                    "matched_terms":
                        matched_terms,

                    "score":
                        min(scores),
                }
            )

    # --------------------------------------------------
    # Constituent relationships
    # --------------------------------------------------

    constituent_plants = {}
    constituent_roles = {}

    for relation in (
        plant_constituents
    ):

        constituent_id = (
            relation[
                "constituent_id"
            ]
        )

        constituent_plants.setdefault(
            constituent_id,
            [],
        ).append(
            relation[
                "plant_id"
            ]
        )

        role = relation.get(
            "proposed_role"
        )

        if role:

            constituent_roles.setdefault(
                constituent_id,
                [],
            ).append(
                role
            )

    # --------------------------------------------------
    # Constituents
    # --------------------------------------------------

    for constituent in constituents:

        scores = [
            score
            for score in [
                match_score(
                    query,
                    constituent.get(
                        "name"
                    ),
                ),
                match_score(
                    query,
                    constituent.get(
                        "compound_group"
                    ),
                ),
            ]
            if score is not None
        ]

        if not scores:
            continue

        linked_plants = []

        for plant_id in (
            constituent_plants.get(
                constituent["id"],
                [],
            )
        ):

            plant = (
                plants_by_id.get(
                    plant_id
                )
            )

            if plant:

                linked_plants.append(
                    {
                        "id":
                            plant_id,

                        "scientific_name":
                            plant[
                                "scientific_name"
                            ],
                    }
                )

        roles = list(
            dict.fromkeys(
                constituent_roles.get(
                    constituent["id"],
                    [],
                )
            )
        )

        results.append(
            {
                "result_type":
                    "constituent",

                "id":
                    constituent[
                        "id"
                    ],

                "title":
                    constituent[
                        "name"
                    ],

                "compound_group":
                    constituent.get(
                        "compound_group"
                    ),

                "linked_plants":
                    linked_plants,

                "roles":
                    roles,

                "score":
                    min(scores),
            }
        )

    type_priority = {
        "plant": 0,
        "constituent": 1,
    }

    results.sort(
        key=lambda item: (
            item["score"],
            type_priority[
                item[
                    "result_type"
                ]
            ],
            item[
                "title"
            ].lower(),
        )
    )

    return results


# ==================================================
# PLANT PROFILE
# ==================================================

@st.cache_data(ttl=300)
def get_plant_by_id(
    plant_id,
):

    response = (
        get_supabase()
        .table("plants")
        .select("*")
        .eq(
            "id",
            plant_id,
        )
        .limit(1)
        .execute()
    )

    if response.data:

        return response.data[0]

    return None


@st.cache_data(ttl=300)
def get_extraction_runs_for_plant(
    plant_id,
):

    runs = (
        get_supabase()
        .table("extraction_runs")
        .select("*")
        .eq(
            "plant_id",
            plant_id,
        )
        .order(
            "created_at",
            desc=True,
        )
        .execute()
        .data
    )

    sources = {
        source["id"]:
            source
        for source
        in get_sources()
    }

    for run in runs:

        run["profile_json"] = (
            parse_json_value(
                run.get(
                    "profile_json"
                )
            )
        )

        run["source"] = (
            sources.get(
                run.get(
                    "source_id"
                )
            )
        )

    return runs


@st.cache_data(ttl=300)
def get_latest_mapping_run(
    plant_id,
):

    response = (
        get_supabase()
        .table("mapping_runs")
        .select("*")
        .eq(
            "plant_id",
            plant_id,
        )
        .order(
            "created_at",
            desc=True,
        )
        .limit(1)
        .execute()
    )

    if not response.data:

        return None

    run = response.data[0]

    run["profile_json"] = (
        parse_json_value(
            run.get(
                "profile_json"
            )
        )
    )

    return run


@st.cache_data(ttl=300)
def get_evidence_for_plant(
    plant_id,
    extraction_runs=None,
):

    evidence = (
        get_supabase()
        .table("evidence_records")
        .select("*")
        .eq(
            "plant_id",
            plant_id,
        )
        .execute()
        .data
    )

    sources = {
        source["id"]:
            source
        for source
        in get_sources()
    }

    for record in evidence:

        record["source"] = (
            sources.get(
                record.get(
                    "source_id"
                )
            )
        )

        record["record_origin"] = (
            "evidence_record"
        )

    evidence.sort(
        key=lambda record: (
            (
                record.get(
                    "source"
                )
                or {}
            ).get(
                "publication_year"
            )
            or 0
        ),
        reverse=True,
    )

    if evidence:
        return evidence

    runs = (
        extraction_runs
        if extraction_runs is not None
        else get_extraction_runs_for_plant(
            plant_id
        )
    )

    ema_run = next(
        (
            run
            for run in runs
            if (
                run.get("pipeline")
                == "PhyThera EMA Extraction"
                and run.get("validation_status")
                in ("pass", "warning")
            )
        ),
        None,
    )

    if not ema_run:
        return []

    profile = (
        ema_run.get(
            "profile_json"
        )
        or {}
    )

    clinical = (
        profile.get(
            "clinical_efficacy"
        )
        or {}
    )

    summary = (
        clinical.get(
            "evidence_summary"
        )
        or clinical.get(
            "overall_efficacy_conclusion"
        )
    )

    if not (
        summary
        or clinical.get("investigated_areas")
        or clinical.get("supporting_quotes")
    ):
        return []

    source = (
        ema_run.get(
            "source"
        )
        or {}
    )

    if not source:
        metadata = profile.get("profile_metadata") or {}
        source = {
            "id": ema_run.get("source_id"),
            "source_type": "ema",
            "title": metadata.get("document_title") or "EMA/HMPC assessment report",
            "url": metadata.get("source_url"),
        }

    return [{
        "plant_id": plant_id,
        "source_id": ema_run.get("source_id"),
        "source": source,
        "evidence_domain": "regulatory clinical assessment",
        "evidence_type": "EMA/HMPC clinical assessment",
        "study_design": None,
        "outcome_direction": None,
        "summary": summary or "Clinical evidence is summarized in the EMA/HMPC assessment report.",
        "human_verified": False,
        "record_origin": "ema_extraction_fallback",
        "metadata": {
            "investigated_areas": clinical.get("investigated_areas") or [],
            "methodological_limitations": clinical.get("methodological_limitations") or [],
            "uncertainties": clinical.get("uncertainties") or [],
            "well_established_use_supported": clinical.get("well_established_use_supported"),
        },
    }]


def _safety_item_text(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    if not isinstance(value, dict):
        return str(value)
    if value.get("description"):
        return str(value["description"])
    if value.get("drug_or_target"):
        parts = [value.get("drug_or_target"), value.get("interaction_type"), value.get("clinical_relevance")]
        return " — ".join(str(part) for part in parts if part)
    if value.get("population"):
        parts = [value.get("population"), value.get("recommendation"), value.get("reason")]
        return " — ".join(str(part) for part in parts if part)
    for key in ["recommendation", "reason", "source_wording"]:
        if value.get(key):
            return str(value[key])
    return None


def _normalize_safety_list(values):
    if not isinstance(values, list):
        return []
    result = []
    for value in values:
        text = _safety_item_text(value)
        if text:
            result.append(text)
    return result


@st.cache_data(ttl=300)
def get_safety_for_plant(
    plant_id,
    extraction_runs=None,
):

    records = (
        get_supabase()
        .table("safety_records")
        .select("*")
        .eq("plant_id", plant_id)
        .execute()
        .data
    )

    sources = {source["id"]: source for source in get_sources()}

    for record in records:
        record["source"] = sources.get(record.get("source_id"))
        record["record_origin"] = "safety_record"

    if records:
        return records

    runs = extraction_runs if extraction_runs is not None else get_extraction_runs_for_plant(plant_id)
    fallback_records = []
    seen_pipelines = set()

    for run in runs:
        pipeline = run.get("pipeline")
        if pipeline in seen_pipelines:
            continue
        if run.get("validation_status") not in ("pass", "warning"):
            continue

        profile = run.get("profile_json") or {}
        safety = profile.get("safety") or {}
        if not isinstance(safety, dict):
            continue

        contraindications = _normalize_safety_list(safety.get("contraindications") or [])
        precautions = _normalize_safety_list((safety.get("precautions") or []) + (safety.get("cautions") or []) + (safety.get("other_safety_notes") or []))
        interactions = _normalize_safety_list((safety.get("interactions") or []) + (safety.get("interaction_warnings") or []))
        adverse_effects = _normalize_safety_list(safety.get("adverse_effects") or [])
        age_restrictions = _normalize_safety_list(safety.get("age_restrictions") or [])
        pregnancy = _safety_item_text(safety.get("pregnancy_lactation"))
        overall_summary = safety.get("overall_safety_summary")

        if not any([contraindications, precautions, interactions, adverse_effects, age_restrictions, pregnancy, overall_summary]):
            continue

        source = run.get("source") or {}
        if not source:
            metadata = profile.get("profile_metadata") or {}
            source = {
                "id": run.get("source_id"),
                "source_type": metadata.get("source_type"),
                "title": metadata.get("document_title") or metadata.get("source_name") or pipeline,
                "url": metadata.get("source_url"),
            }

        fallback_records.append({
            "plant_id": plant_id,
            "source_id": run.get("source_id"),
            "source": source,
            "contraindications": contraindications,
            "precautions": precautions,
            "interactions": interactions,
            "adverse_effects": adverse_effects,
            "age_restrictions": age_restrictions,
            "pregnancy_lactation": pregnancy,
            "overall_safety_summary": overall_summary,
            "human_verified": False,
            "record_origin": "extraction_run_fallback",
            "pipeline": pipeline,
        })
        seen_pipelines.add(pipeline)

    return fallback_records


@st.cache_data(ttl=300)
def get_constituents_for_plant(
    plant_id,
):

    relations = [
        relation
        for relation
        in get_plant_constituents()
        if relation[
            "plant_id"
        ] == plant_id
    ]

    constituents = {
        item["id"]:
            item
        for item
        in get_constituents()
    }

    sources = {
        source["id"]:
            source
        for source
        in get_sources()
    }

    results = []

    for relation in relations:

        constituent = (
            constituents.get(
                relation[
                    "constituent_id"
                ]
            )
        )

        if not constituent:
            continue

        results.append(
            {
                **constituent,

                "plant_part":
                    relation.get(
                        "plant_part"
                    ),

                "proposed_role":
                    relation.get(
                        "proposed_role"
                    ),

                "evidence_note":
                    relation.get(
                        "evidence_note"
                    ),

                "source":
                    sources.get(
                        relation.get(
                            "source_id"
                        )
                    ),
            }
        )

    results.sort(
        key=lambda item:
            item["name"]
    )

    return results


@st.cache_data(ttl=300)
def get_plant_profile(
    plant_id,
):

    plant = get_plant_by_id(
        plant_id
    )

    names = [
        record
        for record
        in get_plant_names()
        if record[
            "plant_id"
        ] == plant_id
    ]

    extraction_runs = (
        get_extraction_runs_for_plant(
            plant_id
        )
    )

    ema_run = next(
        (
            run
            for run
            in extraction_runs
            if run.get(
                "pipeline"
            )
            ==
            "PhyThera EMA Extraction"
        ),
        None,
    )

    tcm_run = next(
        (
            run
            for run
            in extraction_runs
            if run.get(
                "pipeline"
            )
            ==
            "PhyThera TCM Extraction"
        ),
        None,
    )

    indication_profiles = [
        row
        for row
        in get_plant_indication_profiles()
        if row.get(
            "plant_id"
        ) == plant_id
    ]

    mapping_run = (
        get_latest_mapping_run(
            plant_id
        )
    )

    if mapping_run:

        run_ids_for_plant = {
            run.get(
                "id"
            )
            for run
            in extraction_runs
        }

        if (
            mapping_run.get(
                "ema_run_id"
            )
            not in run_ids_for_plant
            or mapping_run.get(
                "tcm_run_id"
            )
            not in run_ids_for_plant
        ):

            mapping_run = None

    return {
        "plant":
            plant,

        "names":
            names,

        "ema_run":
            ema_run,

        "tcm_run":
            tcm_run,

        "mapping_run":
            mapping_run,

        "evidence":
            get_evidence_for_plant(
                plant_id,
                extraction_runs,
            ),

        "safety":
            get_safety_for_plant(
                plant_id,
                extraction_runs,
            ),

        "constituents":
            get_constituents_for_plant(
                plant_id
            ),

        "indication_profiles":
            indication_profiles,
    }