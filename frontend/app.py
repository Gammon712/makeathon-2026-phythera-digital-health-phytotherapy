import html

import streamlit as st
import streamlit.components.v1 as st_components

from components import (
    inject_phytera_css,
    render_header,
    render_hero,
)

from data import (
    get_plants,
    get_plant_profile,
    get_ranked_plants_for_indication,
    search_plants_and_constituents,
)


# ==================================================
# PAGE
# ==================================================

st.set_page_config(
    page_title="PhyThera",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


inject_phytera_css()
render_header()
render_hero()


# ==================================================
# HELPERS
# ==================================================

def score_percent(value):

    if value is None:
        return None

    return int(
        round(float(value) * 100)
    )


def score_display(value):

    percent = score_percent(value)

    if percent is None:
        return "Not available"

    return f"{percent}/100"


def score_css_class(value):

    percent = score_percent(value)

    if percent is None:
        return "score-na"

    if percent >= 80:
        return "score-excellent"

    if percent >= 60:
        return "score-good"

    if percent >= 40:
        return "score-moderate"

    return "score-low"


def evidence_strength_label(value):

    percent = score_percent(value)

    if percent is None:
        return "Not available"

    if percent >= 80:
        return "Strong evidence support"

    if percent >= 60:
        return "Good evidence support"

    if percent >= 40:
        return "Moderate evidence support"

    return "Limited evidence support"


def convergence_display(value):

    percent = score_percent(value)

    if percent is None:
        return "Not assessed"

    return f"{percent}/100"


def convergence_label(value):

    percent = score_percent(value)

    if percent is None:
        return None

    if percent >= 75:
        return "Strong convergence"

    if percent >= 40:
        return "Partial convergence"

    if percent > 0:
        return "Limited convergence"

    return "No meaningful convergence"


def convergence_css_class(value):

    percent = score_percent(value)

    if percent is None:
        return "convergence-na"

    if percent >= 75:
        return "convergence-strong"

    if percent >= 40:
        return "convergence-partial"

    if percent > 0:
        return "convergence-limited"

    return "convergence-none"


def convergence_description(
    convergence,
    traditional_support,
):

    if convergence is not None:

        label = convergence_label(
            convergence
        )

        return (
            f"{label}. European and TCM use concepts "
            "were compared. This signal is not part "
            "of the Evidence Score."
        )

    if traditional_support is None:

        return (
            "No EMA/HMPC comparison profile is "
            "available, so cross-cultural mapping "
            "cannot be assessed."
        )

    return (
        "No comparable TCM profile is currently "
        "available, so cross-cultural mapping "
        "cannot be assessed."
    )


def display_item(value):

    if value is None:
        return None

    if isinstance(value, str):
        return value.strip() or None

    if not isinstance(value, dict):
        return str(value)

    if value.get("description"):
        return str(value["description"])

    if value.get("drug_or_target"):
        parts = [
            value.get("drug_or_target"),
            value.get("interaction_type"),
            value.get("clinical_relevance"),
        ]
        return " — ".join(
            str(part)
            for part in parts
            if part
        )

    if value.get("population"):
        parts = [
            value.get("population"),
            value.get("recommendation"),
            value.get("reason"),
        ]
        return " — ".join(
            str(part)
            for part in parts
            if part
        )

    if value.get("recommendation"):
        parts = [
            value.get("recommendation"),
            value.get("reason"),
        ]
        return " — ".join(
            str(part)
            for part in parts
            if part
        )

    for key in [
        "source_wording",
        "reason",
        "clinical_relevance",
    ]:
        if value.get(key):
            return str(value[key])

    return None


def render_profile_list(
    title,
    values,
):

    if not isinstance(values, list):
        return False

    cleaned = []

    for value in values:
        text = display_item(value)
        if text:
            cleaned.append(text)

    if not cleaned:
        return False

    st.markdown("**" + title + "**")

    for text in cleaned:
        st.write("• " + text)

    return True


def render_source_link(
    profile_data,
    fallback_label,
):

    metadata = (
        profile_data.get(
            "profile_metadata"
        )
        or {}
    )

    url = metadata.get(
        "source_url"
    )

    if url:
        st.link_button(
            "Open source",
            url,
        )

    return (
        metadata.get(
            "document_title"
        )
        or metadata.get(
            "source_name"
        )
        or fallback_label
    )


def score_summary(profile):

    modern = profile.get(
        "modern_evidence_score"
    )

    traditional = profile.get(
        "traditional_support_score"
    )

    if (
        modern is not None
        and traditional is not None
    ):
        return (
            "The ranking combines modern clinical "
            "evidence with documented EMA/HMPC "
            "traditional or regulatory support."
        )

    if modern is not None:
        return (
            "The ranking is based on available modern "
            "clinical evidence. EMA/HMPC support is "
            "not available for this profile."
        )

    if traditional is not None:
        return (
            "The ranking is based on documented "
            "EMA/HMPC support. Comparable modern "
            "clinical evidence is not available."
        )

    return (
        "Not enough comparable evidence is available "
        "to calculate a meaningful ranking."
    )


# ==================================================
# DATABASE
# ==================================================

try:

    plants = get_plants()

    database_ready = True

except Exception as error:

    database_ready = False

    plants = []

    st.error(
        "Database connection failed."
    )

    with st.expander(
        "Technical details"
    ):

        st.code(
            str(error)
        )


# ==================================================
# SEARCH
# ==================================================

(
    search_indication,
    search_product,
) = st.tabs(
    [
        "Search by indication",
        "Search by plant / constituent",
    ]
)


# ==================================================
# INDICATION SEARCH
# ==================================================

with search_indication:

    indication_query = (
        st.text_input(
            "Indication",
            placeholder=(
                "e.g. fatigue, weakness, "
                "insomnia, mild anxiety"
            ),
            label_visibility="collapsed",
            key="indication_search",
        )
    )

    st.caption(
        "Find medicinal plants ranked by a "
        "transparent evidence relevance score. "
        "Cross-cultural convergence is displayed "
        "separately and does not increase the score."
    )

    if (
        database_ready
        and len(
            indication_query.strip()
        ) >= 2
    ):

        search_data = (
            get_ranked_plants_for_indication(
                indication_query
            )
        )

        indication_matches = (
            search_data[
                "indications"
            ]
        )

        ranked_results = (
            search_data[
                "results"
            ]
        )

        # ------------------------------------------
        # Indication recognized
        # ------------------------------------------

        if indication_matches:

            primary_indication = (
                indication_matches[0]
            )

            st.markdown(
                "### Indication match"
            )

            st.write(
                "**"
                + primary_indication[
                    "display_name"
                ]
                + "**"
            )

            matched_terms = (
                primary_indication.get(
                    "matched_terms"
                )
                or []
            )

            if matched_terms:

                st.caption(
                    "Matched terminology: "
                    + " · ".join(
                        matched_terms
                    )
                )

            if primary_indication.get(
                "description"
            ):

                st.caption(
                    primary_indication[
                        "description"
                    ]
                )

            # --------------------------------------
            # Ranked plants
            # --------------------------------------

            if ranked_results:

                st.markdown(
                    "### Ranked evidence results"
                )

                st.caption(
                    f"{len(ranked_results)} plant"
                    f"{'' if len(ranked_results) == 1 else 's'} "
                    f"with a scored profile"
                )

                for (
                    rank,
                    result,
                ) in enumerate(
                    ranked_results,
                    start=1,
                ):

                    plant = (
                        result[
                            "plant"
                        ]
                    )

                    profile = (
                        result[
                            "profile"
                        ]
                    )

                    overall = (
                        profile.get(
                            "evidence_relevance_score"
                        )
                    )

                    modern = (
                        profile.get(
                            "modern_evidence_score"
                        )
                    )

                    traditional = (
                        profile.get(
                            "traditional_support_score"
                        )
                    )

                    convergence = (
                        profile.get(
                            "source_convergence_score"
                        )
                    )

                    with st.container(
                        border=True
                    ):

                        meta = []

                        if plant.get(
                            "family"
                        ):

                            meta.append(
                                plant[
                                    "family"
                                ]
                            )

                        meta.extend(
                            (
                                plant.get(
                                    "common_names"
                                )
                                or []
                            )[:2]
                        )

                        meta_text = (
                            " · ".join(meta)
                        )

                        category = (
                            profile.get(
                                "evidence_category"
                            )
                            or
                            "unclassified"
                        )

                        category = (
                            category
                            .replace(
                                "_",
                                " "
                            )
                            .title()
                        )

                        research = (
                            profile.get(
                                "research_opportunity"
                            )
                            or
                            "unclassified"
                        )

                        research = (
                            research
                            .replace(
                                "_",
                                " "
                            )
                            .title()
                        )

                        st.html(
                            f"""
                            <div class="evidence-result-top">

                                <div class="evidence-result-identity">

                                    <div class="result-rank">
                                        {rank:02d} · PLANT
                                    </div>

                                    <div class="result-name result-name-large">
                                        {html.escape(plant["scientific_name"])}
                                    </div>

                                    <div class="result-meta">
                                        {html.escape(meta_text)}
                                    </div>

                                    <div class="evidence-badges">
                                        <span class="tag tag-clinical">
                                            {html.escape(category)}
                                        </span>

                                        <span class="tag tag-research">
                                            Research opportunity · {html.escape(research)}
                                        </span>
                                    </div>

                                </div>

                                <div class="score-card score-card-main {score_css_class(overall)}">

                                    <div class="score-kicker">
                                        EVIDENCE SCORE
                                    </div>

                                    <div class="score-number-main">
                                        {score_display(overall)}
                                    </div>

                                    <div class="score-strength">
                                        {evidence_strength_label(overall)}
                                    </div>

                                    <div class="score-description">
                                        Overall strength of evidence for this plant
                                        and the selected indication.
                                    </div>

                                </div>

                            </div>
                            """
                        )

                        (
                            c1,
                            c2,
                            c3,
                        ) = st.columns(3)

                        with c1:

                            st.html(
                                f"""
                                <div class="score-card {score_css_class(modern)}">
                                    <div class="score-kicker">
                                        MODERN EVIDENCE
                                    </div>
                                    <div class="score-number">
                                        {score_display(modern)}
                                    </div>
                                    <div class="score-description">
                                        Support from human clinical studies
                                        and systematic reviews.
                                    </div>
                                </div>
                                """
                            )

                        with c2:

                            st.html(
                                f"""
                                <div class="score-card {score_css_class(traditional)}">
                                    <div class="score-kicker">
                                        TRADITIONAL SUPPORT
                                    </div>
                                    <div class="score-number">
                                        {score_display(traditional)}
                                    </div>
                                    <div class="score-description">
                                        EMA/HMPC traditional or established-use
                                        support for this indication.
                                    </div>
                                </div>
                                """
                            )

                        with c3:

                            convergence_state = (
                                convergence_label(
                                    convergence
                                )
                            )

                            st.html(
                                f"""
                                <div class="score-card {convergence_css_class(convergence)}">
                                    <div class="score-kicker">
                                        SOURCE CONVERGENCE
                                    </div>
                                    <div class="score-number">
                                        {convergence_display(convergence)}
                                    </div>
                                    {
                                        (
                                            '<div class="convergence-label">'
                                            + html.escape(convergence_state)
                                            + '</div>'
                                        )
                                        if convergence_state
                                        else ''
                                    }
                                    <div class="score-description">
                                        {
                                            html.escape(
                                                convergence_description(
                                                    convergence,
                                                    traditional,
                                                )
                                            )
                                        }
                                    </div>
                                </div>
                                """
                            )

                        st.html(
                            f"""
                            <div class="score-explanation">
                                <strong>Why this score?</strong>
                                {html.escape(score_summary(profile))}
                            </div>
                            """
                        )

                        if st.button(
                            "Open evidence profile",
                            key=(
                                "open_indication_"
                                + plant["id"]
                                + "_"
                                + profile[
                                    "indication_id"
                                ]
                            ),
                            width="stretch",
                        ):

                            st.session_state[
                                "selected_plant_id"
                            ] = plant[
                                "id"
                            ]

                            st.session_state[
                                "selected_indication_id"
                            ] = profile[
                                "indication_id"
                            ]

                            st.session_state[
                                "scroll_to_profile"
                            ] = True

                            st.rerun()

                # ----------------------------------
                # Score explanation
                # ----------------------------------

                with st.expander(
                    "How the PhyThera evidence "
                    "score is calculated"
                ):

                    st.markdown(
                        """
**PhyThera Evidence Score** is a transparent ranking score for a plant–indication profile.

- **Modern Evidence** summarizes the available human clinical evidence.
- **Traditional Support** reflects documented EMA/HMPC traditional or regulatory support.
- **Evidence Score** combines the available evidence layers. Modern evidence is the main component and traditional support is an additional component. If one layer is unavailable, the score is calculated from the available evidence rather than treating missing data as negative evidence.
- **Source Convergence** compares European and TCM use concepts. It is displayed separately and does not increase the Evidence Score.

Higher scores mean **stronger evidence support for the searched indication**. They do not represent percentage efficacy, probability of benefit, or a treatment recommendation.
                        """
                    )

                    profile_rationale = (
                        ranked_results[
                            0
                        ][
                            "profile"
                        ].get(
                            "profile_rationale"
                        )
                    )

                    scoring_version = (
                        ranked_results[
                            0
                        ][
                            "profile"
                        ].get(
                            "scoring_version"
                        )
                    )

                    if scoring_version:

                        st.caption(
                            "Stored scoring version: "
                            + scoring_version
                        )

                    if profile_rationale:

                        st.caption(
                            profile_rationale
                        )

            else:

                st.warning(
                    "The indication is recognized, "
                    "but no scored plant profile "
                    "is available yet."
                )

        else:

            st.warning(
                f"No curated indication found "
                f"for “{indication_query}”."
            )


# ==================================================
# PLANT / CONSTITUENT SEARCH
# ==================================================

with search_product:

    product_query = (
        st.text_input(
            "Plant or constituent",
            placeholder=(
                "e.g. Panax ginseng, valerian, "
                "ginsenoside Rg1"
            ),
            label_visibility="collapsed",
            key="product_search",
        )
    )

    st.caption(
        "Investigate a plant or constituent "
        "and evaluate claims for specific "
        "indications."
    )

    if (
        database_ready
        and len(
            product_query.strip()
        ) >= 2
    ):

        results = (
            search_plants_and_constituents(
                product_query
            )
        )

        if results:

            st.markdown(
                "### Search results"
            )

            st.caption(
                f"{len(results)} result"
                f"{'' if len(results) == 1 else 's'} "
                f"for “{product_query}”"
            )

            for (
                index,
                result,
            ) in enumerate(
                results,
                start=1,
            ):

                # ----------------------------------
                # Plant
                # ----------------------------------

                if (
                    result[
                        "result_type"
                    ]
                    == "plant"
                ):

                    names = list(
                        dict.fromkeys(
                            [
                                *(
                                    result.get(
                                        "common_names"
                                    )
                                    or []
                                ),
                                *(
                                    result.get(
                                        "aliases"
                                    )
                                    or []
                                ),
                            ]
                        )
                    )

                    names_text = (
                        " · ".join(
                            names[:4]
                        )
                    )

                    family = (
                        result.get(
                            "family"
                        )
                        or
                        "Family not yet curated"
                    )

                    st.html(
                        f"""
                        <div class="result-card">

                            <div class="result-rank">
                                {index:02d} · PLANT
                            </div>

                            <div class="result-name">
                                {
                                    html.escape(
                                        result["title"]
                                    )
                                }
                            </div>

                            <div class="result-meta">
                                {
                                    html.escape(
                                        family
                                    )
                                }

                                {
                                    " · "
                                    if names_text
                                    else ""
                                }

                                {
                                    html.escape(
                                        names_text
                                    )
                                }
                            </div>

                            <span class="
                                tag tag-regulatory
                            ">
                                Medicinal plant
                            </span>

                        </div>
                        """
                    )

                    if st.button(
                        "Open evidence profile",
                        key=(
                            "open_plant_"
                            + result["id"]
                        ),
                    ):

                        st.session_state[
                            "selected_plant_id"
                        ] = result[
                            "plant_id"
                        ]

                        st.session_state[
                            "scroll_to_profile"
                        ] = True

                        st.rerun()

                # ----------------------------------
                # Constituent
                # ----------------------------------

                else:

                    linked_names = [
                        plant[
                            "scientific_name"
                        ]
                        for plant
                        in result.get(
                            "linked_plants",
                            [],
                        )
                    ]

                    role = (
                        result.get(
                            "roles"
                        )
                        or [
                            "Role not yet curated"
                        ]
                    )[0]

                    st.html(
                        f"""
                        <div class="result-card">

                            <div class="result-rank">
                                {index:02d}
                                · CONSTITUENT
                            </div>

                            <div class="result-name">
                                {
                                    html.escape(
                                        result["title"]
                                    )
                                }
                            </div>

                            <div class="result-meta">
                                {
                                    html.escape(
                                        result.get(
                                            "compound_group"
                                        )
                                        or ""
                                    )
                                }
                            </div>

                            <div class="result-meta">
                                Found in:
                                {
                                    html.escape(
                                        " · ".join(
                                            linked_names
                                        )
                                    )
                                }
                            </div>

                            <span class="
                                tag tag-clinical
                            ">
                                {
                                    html.escape(
                                        role
                                    )
                                }
                            </span>

                        </div>
                        """
                    )

        else:

            st.warning(
                f"No result found for "
                f"“{product_query}”."
            )


# ==================================================
# SELECTED PLANT
# ==================================================

selected_plant_id = (
    st.session_state.get(
        "selected_plant_id"
    )
)


if selected_plant_id:

    st.html(
        '<div id="evidence-profile-anchor"></div>'
    )

    if st.session_state.pop(
        "scroll_to_profile",
        False,
    ):

        st_components.html(
            """
            <script>
            const anchor =
                window.parent.document.getElementById(
                    "evidence-profile-anchor"
                );

            if (anchor) {
                anchor.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
            </script>
            """,
            height=0,
        )

    st.divider()

    if st.button(
        "← Back to search"
    ):

        st.session_state.pop(
            "selected_plant_id",
            None,
        )

        st.session_state.pop(
            "selected_indication_id",
            None,
        )

        st.rerun()

    try:

        profile = get_plant_profile(
            selected_plant_id
        )

    except Exception as error:

        st.error(
            "The evidence profile could "
            "not be loaded."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                str(error)
            )

        st.stop()

    plant = profile[
        "plant"
    ]

    if not plant:

        st.error(
            "Plant record not found."
        )

        st.stop()

    aliases = list(
        dict.fromkeys(
            record["name"]
            for record
            in profile[
                "names"
            ]
        )
    )

    st.caption(
        "MEDICINAL PLANT EVIDENCE PROFILE"
    )

    st.title(
        plant[
            "scientific_name"
        ]
    )

    metadata_line = []

    if plant.get(
        "family"
    ):

        metadata_line.append(
            plant[
                "family"
            ]
        )

    metadata_line.extend(
        aliases[:4]
    )

    st.caption(
        " · ".join(
            metadata_line
        )
    )


    # ==================================================
    # PROFILE DATA
    # ==================================================

    mapping_run = (
        profile[
            "mapping_run"
        ]
    )

    mapping_profile = (
        mapping_run.get(
            "profile_json"
        )
        if mapping_run
        else {}
    )

    if not isinstance(
        mapping_profile,
        dict,
    ):

        mapping_profile = {}

    ema_profile = (
        (
            profile[
                "ema_run"
            ]
            or {}
        ).get(
            "profile_json"
        )
        or {}
    )

    tcm_profile = (
        (
            profile[
                "tcm_run"
            ]
            or {}
        ).get(
            "profile_json"
        )
        or {}
    )

    if not isinstance(
        ema_profile,
        dict,
    ):

        ema_profile = {}

    if not isinstance(
        tcm_profile,
        dict,
    ):

        tcm_profile = {}

    source_context = (
        mapping_profile.get(
            "source_context"
        )
        or {}
    )

    strongest = (
        mapping_profile.get(
            "strongest_convergence"
        )
    )

    selected_indication_id = (
        st.session_state.get(
            "selected_indication_id"
        )
    )

    indication_profile = next(
        (
            row
            for row
            in profile.get(
                "indication_profiles",
                [],
            )
            if row.get(
                "indication_id"
            )
            ==
            selected_indication_id
        ),
        None,
    )


    # ==================================================
    # PROFILE TABS
    # ==================================================

    (
        tab_overview,
        tab_mapping,
        tab_evidence,
        tab_constituents,
        tab_safety,
        tab_sources,
    ) = st.tabs(
        [
            "Overview",
            "Europe ↔ TCM",
            "Clinical evidence",
            "Constituents",
            "Safety",
            "Sources",
        ]
    )


    # ==================================================
    # OVERVIEW
    # ==================================================

    with tab_overview:

        st.subheader(
            "Evidence snapshot"
        )

        if indication_profile:

            (
                s1,
                s2,
                s3,
                s4,
            ) = st.columns(4)

            with s1:

                st.caption(
                    "EVIDENCE SCORE"
                )

                st.markdown(
                    "**"
                    + score_display(
                        indication_profile.get(
                            "evidence_relevance_score"
                        )
                    )
                    + "**"
                )

            with s2:

                st.caption(
                    "MODERN EVIDENCE"
                )

                st.markdown(
                    "**"
                    + score_display(
                        indication_profile.get(
                            "modern_evidence_score"
                        )
                    )
                    + "**"
                )

            with s3:

                st.caption(
                    "TRADITIONAL SUPPORT"
                )

                st.markdown(
                    "**"
                    + score_display(
                        indication_profile.get(
                            "traditional_support_score"
                        )
                    )
                    + "**"
                )

            with s4:

                st.caption(
                    "SOURCE CONVERGENCE"
                )

                overview_convergence = (
                    indication_profile.get(
                        "source_convergence_score"
                    )
                )

                st.markdown(
                    "**"
                    + convergence_display(
                        overview_convergence
                    )
                    + "**"
                )

                overview_convergence_label = (
                    convergence_label(
                        overview_convergence
                    )
                )

                if overview_convergence_label:

                    st.caption(
                        overview_convergence_label
                    )

            st.caption(
                "Evidence relevance is a ranking "
                "score, not an efficacy percentage. "
                "Cross-cultural convergence is not "
                "included in the ranking score."
            )

        st.markdown(
            "### European use"
        )

        medicinal_use = (
            ema_profile.get(
                "medicinal_use"
            )
            or {}
        )

        indications = (
            medicinal_use.get(
                "indications"
            )
            or []
        )

        if indications:

            for item in indications:

                st.write(
                    item.get(
                        "source_wording"
                    )
                )

                st.caption(
                    item.get(
                        "regulatory_basis"
                    )
                    or ""
                )

        else:

            ema_metadata = (
                ema_profile.get(
                    "profile_metadata"
                )
                or {}
            )

            if (
                ema_profile
                and ema_metadata.get(
                    "source_url"
                )
            ):

                st.caption(
                    "EMA/HMPC assessment report available. "
                    "No structured medicinal-use indication "
                    "was extracted into the current profile."
                )

            else:

                st.caption(
                    "No EMA/HMPC assessment profile available."
                )

        st.markdown(
            "### TCM profile"
        )

        tcm_properties = (
            tcm_profile.get(
                "tcm_properties"
            )
            or {}
        )

        medicinal_group = (
            (
                tcm_profile.get(
                    "identity"
                )
                or {}
            ).get(
                "medicinal_group"
            )
        )

        if medicinal_group:

            st.write(
                "**Medicinal group:** "
                + medicinal_group
            )

        if tcm_properties.get(
            "nature"
        ):

            st.write(
                "**Nature:** "
                + tcm_properties[
                    "nature"
                ]
            )

        if tcm_properties.get(
            "flavors"
        ):

            st.write(
                "**Flavors:** "
                + ", ".join(
                    tcm_properties[
                        "flavors"
                    ]
                )
            )

        if tcm_properties.get(
            "meridian_affinity"
        ):

            st.write(
                "**Meridian affinity:** "
                + ", ".join(
                    tcm_properties[
                        "meridian_affinity"
                    ]
                )
            )

        st.info(
            "Traditional-use documentation "
            "and cross-cultural convergence "
            "are shown separately from "
            "clinical efficacy."
        )


    # ==================================================
    # MAPPING
    # ==================================================

    with tab_mapping:

        st.subheader(
            "Cross-cultural mapping"
        )

        if strongest:

            (
                europe,
                middle,
                china,
            ) = st.columns(
                [1, 0.8, 1]
            )

            with europe:

                st.caption(
                    "EUROPE · EMA/HMPC"
                )

                st.markdown(
                    "**European use**"
                )

                st.write(
                    strongest[
                        "european_indication"
                    ][
                        "source_wording"
                    ]
                )

            with middle:

                st.caption(
                    "SEMANTIC MAPPING"
                )

                category = (
                    strongest.get(
                        "mapping_category",
                        "",
                    )
                    .replace(
                        "_",
                        " ",
                    )
                    .title()
                )

                st.markdown(
                    "**"
                    + category
                    + "**"
                )

                confidence = (
                    strongest.get(
                        "confidence"
                    )
                )

                if confidence is not None:

                    st.write(
                        f"{confidence:.0%} "
                        "classification confidence"
                    )

            with china:

                st.caption(
                    "CHINA · TCM"
                )

                st.markdown(
                    "**Traditional use**"
                )

                st.write(
                    strongest[
                        "tcm_indication"
                    ][
                        "source_wording"
                    ]
                )

            st.markdown(
                "#### Shared concept"
            )

            shared = (
                strongest.get(
                    "mapping_basis",
                    {},
                ).get(
                    "shared_concept"
                )
            )

            st.write(
                shared
                or
                "No shared concept."
            )

            st.markdown(
                "#### Interpretation"
            )

            st.write(
                strongest.get(
                    "semantic_overlap"
                )
                or ""
            )

            st.caption(
                strongest.get(
                    "key_difference"
                )
                or ""
            )

            st.warning(
                "Semantic convergence does "
                "not demonstrate clinical "
                "efficacy."
            )

        else:

            st.info(
                "No cross-cultural mapping "
                "available for this plant."
            )

        mappings = (
            mapping_profile.get(
                "mappings"
            )
            or []
        )

        if mappings:

            with st.expander(
                "View all mapped use concepts"
            ):

                for item in mappings:

                    st.markdown(
                        "**"
                        + item[
                            "tcm_indication"
                        ][
                            "source_wording"
                        ]
                        + "**"
                    )

                    st.caption(
                        item.get(
                            "mapping_category",
                            "",
                        )
                        .replace(
                            "_",
                            " ",
                        )
                    )

                    st.write(
                        item.get(
                            "key_difference"
                        )
                        or ""
                    )

                    st.divider()


    # ==================================================
    # EVIDENCE
    # ==================================================

    with tab_evidence:

        st.subheader(
            "Modern and regulatory evidence"
        )

        clinical = (
            ema_profile.get(
                "clinical_efficacy"
            )
            or {}
        )

        has_ema_clinical = (
            isinstance(
                clinical,
                dict,
            )
            and any(
                [
                    clinical.get(
                        "evidence_summary"
                    ),
                    clinical.get(
                        "overall_efficacy_conclusion"
                    ),
                    clinical.get(
                        "investigated_areas"
                    ),
                    clinical.get(
                        "supporting_quotes"
                    ),
                ]
            )
        )

        if has_ema_clinical:

            with st.container(
                border=True
            ):

                st.caption(
                    "EMA / HMPC · REGULATORY CLINICAL ASSESSMENT"
                )

                ema_metadata = (
                    ema_profile.get(
                        "profile_metadata"
                    )
                    or {}
                )

                st.markdown(
                    "**"
                    + (
                        ema_metadata.get(
                            "document_title"
                        )
                        or
                        "EMA/HMPC assessment report"
                    )
                    + "**"
                )

                summary = (
                    clinical.get(
                        "evidence_summary"
                    )
                    or clinical.get(
                        "overall_efficacy_conclusion"
                    )
                )

                if summary:
                    st.write(summary)

                investigated = (
                    clinical.get(
                        "investigated_areas"
                    )
                    or []
                )

                if investigated:

                    st.markdown(
                        "**Investigated areas**"
                    )

                    for item in investigated:
                        st.write(
                            "• "
                            + str(item)
                        )

                weu = clinical.get(
                    "well_established_use_supported"
                )

                if weu is True:
                    st.success(
                        "Well-established use is supported "
                        "for at least one assessed preparation "
                        "or indication."
                    )

                elif weu is False:
                    st.info(
                        "The EMA/HMPC assessment does not "
                        "support well-established use for "
                        "the assessed indication."
                    )

                limitations = (
                    clinical.get(
                        "methodological_limitations"
                    )
                    or []
                )

                uncertainties = (
                    clinical.get(
                        "uncertainties"
                    )
                    or []
                )

                if limitations or uncertainties:

                    with st.expander(
                        "Limitations and uncertainties"
                    ):

                        render_profile_list(
                            "Methodological limitations",
                            limitations,
                        )

                        render_profile_list(
                            "Uncertainties",
                            uncertainties,
                        )

                source_url = (
                    ema_metadata.get(
                        "source_url"
                    )
                )

                if source_url:
                    st.link_button(
                        "Open EMA source",
                        source_url,
                    )

        evidence_records = [
            record
            for record
            in profile.get(
                "evidence",
                [],
            )
            if record.get(
                "record_origin"
            )
            !=
            "ema_extraction_fallback"
        ]

        if evidence_records:

            st.markdown(
                "### Detailed clinical evidence records"
            )


            for record in evidence_records:

                source = (
                    record.get(
                        "source"
                    )
                    or {}
                )

                with st.container(
                    border=True
                ):

                    domain = (
                        record.get(
                            "evidence_domain"
                        )
                        or
                        "evidence"
                    )

                    st.caption(
                        domain.upper()
                    )

                    title = (
                        source.get(
                            "title"
                        )
                        or
                        record.get(
                            "evidence_type"
                        )
                        or
                        "Evidence record"
                    )

                    st.markdown(
                        "**"
                        + title
                        + "**"
                    )

                    details = [
                        str(value)
                        for value in [
                            source.get(
                                "publication_year"
                            ),
                            record.get(
                                "study_design"
                            ),
                        ]
                        if value
                    ]

                    if details:
                        st.caption(
                            " · ".join(details)
                        )

                    if record.get(
                        "outcome_direction"
                    ):

                        st.write(
                            "**Outcome:** "
                            + record[
                                "outcome_direction"
                            ].title()
                        )

                    summary = (
                        record.get(
                            "summary"
                        )
                    )

                    if summary:
                        st.write(summary)


                    if source.get(
                        "url"
                    ):
                        st.link_button(
                            "Open source",
                            source["url"],
                        )

        if (
            not has_ema_clinical
            and not evidence_records
        ):

            modern_score = (
                indication_profile.get(
                    "modern_evidence_score"
                )
                if indication_profile
                else None
            )

            if modern_score is not None:

                st.warning(
                    "A Modern Evidence Score is stored for "
                    "this plant–indication profile, but the "
                    "individual study records used to derive "
                    "it were not persisted. The score can be "
                    "shown, but detailed study-level provenance "
                    "is not available in the current database."
                )

            else:

                st.info(
                    "No structured clinical evidence "
                    "is available for this plant yet."
                )

        elif (
            has_ema_clinical
            and not evidence_records
        ):

            st.caption(
                "Individual PubMed study records were "
                "not persisted for this profile. The "
                "EMA/HMPC assessment above is therefore "
                "shown as the structured clinical-evidence "
                "source."
            )


    # ==================================================
    # CONSTITUENTS
    # ==================================================

    with tab_constituents:

        st.subheader(
            "Characteristic constituents"
        )

        st.info(
            "Presence or analytical use of a "
            "constituent does not establish "
            "that it is responsible for the "
            "therapeutic effect of the plant."
        )

        constituents = (
            profile[
                "constituents"
            ]
        )

        if constituents:

            table_data = [
                {
                    "Constituent":
                        item.get(
                            "name"
                        ),

                    "Group":
                        item.get(
                            "compound_group"
                        ),

                    "Plant part":
                        item.get(
                            "plant_part"
                        ),

                    "Role":
                        item.get(
                            "proposed_role"
                        ),
                }
                for item
                in constituents
            ]

            st.dataframe(
                table_data,
                width="stretch",
                hide_index=True,
            )

            with st.expander(
                "Scientific interpretation"
            ):

                note = (
                    constituents[
                        0
                    ].get(
                        "evidence_note"
                    )
                )

                if note:

                    st.write(
                        note
                    )


    # ==================================================
    # SAFETY
    # ==================================================

    with tab_safety:

        st.subheader(
            "Source-specific safety"
        )

        safety_sources = []

        ema_safety = (
            ema_profile.get(
                "safety"
            )
            or {}
        )

        if (
            isinstance(
                ema_safety,
                dict,
            )
            and ema_safety
        ):

            safety_sources.append(
                (
                    "EMA / HMPC",
                    ema_safety,
                    ema_profile,
                )
            )

        tcm_safety = (
            tcm_profile.get(
                "safety"
            )
            or {}
        )

        if (
            isinstance(
                tcm_safety,
                dict,
            )
            and tcm_safety
        ):

            safety_sources.append(
                (
                    "TCM source",
                    tcm_safety,
                    tcm_profile,
                )
            )

        if safety_sources:

            for (
                source_label,
                safety,
                source_profile,
            ) in safety_sources:

                with st.container(
                    border=True
                ):

                    st.caption(
                        source_label.upper()
                    )

                    metadata = (
                        source_profile.get(
                            "profile_metadata"
                        )
                        or {}
                    )

                    st.markdown(
                        "**"
                        + (
                            metadata.get(
                                "document_title"
                            )
                            or metadata.get(
                                "source_name"
                            )
                            or source_label
                        )
                        + "**"
                    )

                    overall = (
                        safety.get(
                            "overall_safety_summary"
                        )
                    )

                    if overall:

                        st.write(overall)

                    rendered = False

                    rendered = (
                        render_profile_list(
                            "Contraindications",
                            safety.get(
                                "contraindications"
                            )
                            or [],
                        )
                        or rendered
                    )

                    rendered = (
                        render_profile_list(
                            "Precautions",
                            (
                                safety.get(
                                    "precautions"
                                )
                                or []
                            )
                            +
                            (
                                safety.get(
                                    "cautions"
                                )
                                or []
                            )
                            +
                            (
                                safety.get(
                                    "other_safety_notes"
                                )
                                or []
                            ),
                        )
                        or rendered
                    )

                    rendered = (
                        render_profile_list(
                            "Interactions",
                            (
                                safety.get(
                                    "interactions"
                                )
                                or []
                            )
                            +
                            (
                                safety.get(
                                    "interaction_warnings"
                                )
                                or []
                            ),
                        )
                        or rendered
                    )

                    rendered = (
                        render_profile_list(
                            "Adverse effects",
                            safety.get(
                                "adverse_effects"
                            )
                            or [],
                        )
                        or rendered
                    )

                    rendered = (
                        render_profile_list(
                            "Age restrictions",
                            safety.get(
                                "age_restrictions"
                            )
                            or [],
                        )
                        or rendered
                    )

                    pregnancy = (
                        display_item(
                            safety.get(
                                "pregnancy_lactation"
                            )
                        )
                    )

                    if pregnancy:

                        st.markdown(
                            "**Pregnancy / lactation**"
                        )

                        st.write(pregnancy)

                        rendered = True

                    if (
                        not rendered
                        and not overall
                    ):

                        st.caption(
                            "No detailed safety statements "
                            "were extracted from this source."
                        )

                    source_url = (
                        metadata.get(
                            "source_url"
                        )
                    )

                    if source_url:

                        st.link_button(
                            "Open source",
                            source_url,
                        )

        else:

            normalized_safety = (
                profile.get(
                    "safety",
                    [],
                )
            )

            if normalized_safety:

                for record in normalized_safety:

                    source = (
                        record.get(
                            "source"
                        )
                        or {}
                    )

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            "**"
                            + (
                                source.get(
                                    "title"
                                )
                                or
                                "Safety source"
                            )
                            + "**"
                        )

                        render_profile_list(
                            "Contraindications",
                            record.get(
                                "contraindications"
                            )
                            or [],
                        )

                        render_profile_list(
                            "Precautions",
                            record.get(
                                "precautions"
                            )
                            or [],
                        )

                        render_profile_list(
                            "Interactions",
                            record.get(
                                "interactions"
                            )
                            or [],
                        )

                        render_profile_list(
                            "Adverse effects",
                            record.get(
                                "adverse_effects"
                            )
                            or [],
                        )

                        render_profile_list(
                            "Age restrictions",
                            record.get(
                                "age_restrictions"
                            )
                            or [],
                        )

                        pregnancy = (
                            display_item(
                                record.get(
                                    "pregnancy_lactation"
                                )
                            )
                        )

                        if pregnancy:

                            st.markdown(
                                "**Pregnancy / lactation**"
                            )

                            st.write(pregnancy)

                        if source.get(
                            "url"
                        ):

                            st.link_button(
                                "Open source",
                                source["url"],
                            )

            else:

                st.info(
                    "No structured safety information "
                    "is available for this plant yet."
                )


    # ==================================================
    # SOURCES
    # ==================================================

    with tab_sources:

        st.subheader(
            "Source provenance"
        )

        source_entries = {}

        def add_source(
            url,
            title,
            source_type,
        ):

            if not url:
                return

            source_entries[url] = {
                "title":
                    title
                    or url,

                "source_type":
                    source_type
                    or "source",
            }

        ema_metadata = (
            ema_profile.get(
                "profile_metadata"
            )
            or {}
        )

        add_source(
            ema_metadata.get(
                "source_url"
            ),
            ema_metadata.get(
                "document_title"
            )
            or "EMA/HMPC assessment report",
            "EMA / HMPC",
        )

        tcm_metadata = (
            tcm_profile.get(
                "profile_metadata"
            )
            or {}
        )

        add_source(
            tcm_metadata.get(
                "source_url"
            ),
            tcm_metadata.get(
                "source_name"
            )
            or tcm_metadata.get(
                "document_title"
            )
            or "Traditional source",
            "Traditional source",
        )

        european_source = (
            source_context.get(
                "european"
            )
            or {}
        )

        add_source(
            european_source.get(
                "source_url"
            ),
            european_source.get(
                "source_title"
            )
            or "EMA/HMPC",
            "EMA / HMPC",
        )

        tcm_source = (
            source_context.get(
                "tcm"
            )
            or {}
        )

        add_source(
            tcm_source.get(
                "source_url"
            ),
            tcm_source.get(
                "source_name"
            )
            or "Traditional source",
            "Traditional source",
        )

        for record in (
            profile.get(
                "evidence",
                [],
            )
            +
            profile.get(
                "safety",
                [],
            )
        ):

            source = (
                record.get(
                    "source"
                )
                or {}
            )

            add_source(
                source.get(
                    "url"
                ),
                source.get(
                    "title"
                ),
                source.get(
                    "source_type"
                ),
            )

        if source_entries:

            for (
                url,
                source,
            ) in source_entries.items():

                with st.container(
                    border=True
                ):

                    st.caption(
                        str(
                            source[
                                "source_type"
                            ]
                        ).upper()
                    )

                    st.write(
                        "**"
                        + source[
                            "title"
                        ]
                        + "**"
                    )

                    st.link_button(
                        "Open source",
                        url,
                    )

        else:

            st.info(
                "No source provenance is available "
                "for this plant yet."
            )

        st.caption(
            "Source provenance is preserved separately "
            "from evidence scoring. AI-extracted profiles "
            "retain their source URL and validation metadata."
        )


# ==================================================
# GLOBAL GUARDRAIL
# ==================================================

st.divider()

st.info(
    "PhyThera is designed for healthcare "
    "professionals and research use. "
    "Traditional-use documentation, semantic "
    "convergence and clinical efficacy are "
    "displayed as distinct evidence layers."
)