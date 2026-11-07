from pathlib import Path

import streamlit as st


def inject_phytera_css():
    st.html(
        """
        <style>

        @import url(
            'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap'
        );

        html, body, [class*="css"] {
            font-family: "IBM Plex Sans", sans-serif;
        }

        .stApp {
            background-color: #F7F8F6;
        }

        .block-container {
            max-width: 1320px;
            padding-top: 3.2rem;
            padding-bottom: 4rem;
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* HEADER */

        .phytera-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3rem;
        }

        .phytera-logo {
            font-size: 1.5rem;
            font-weight: 600;
            letter-spacing: -0.03em;
            color: #1E2925;
        }

        .phytera-logo span {
            color: #1F5A48;
        }

        .hcp-badge {
            font-size: 0.78rem;
            font-weight: 500;
            color: #475651;
            border: 1px solid #CED6D2;
            background: #FFFFFF;
            padding: 0.38rem 0.72rem;
            border-radius: 999px;
        }

        /* HERO */

        .hero-kicker {
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.09em;
            text-transform: uppercase;
            color: #1F5A48;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: 2.65rem;
            line-height: 1.08;
            font-weight: 600;
            letter-spacing: -0.045em;
            color: #1E2925;
            max-width: none;
            white-space: nowrap;
            margin-bottom: 0.9rem;
        }

        .hero-text {
            font-size: 1.03rem;
            line-height: 1.65;
            color: #68736F;
            max-width: none;
            white-space: nowrap;
            margin-bottom: 2.2rem;
        }

        /* SECTION */

        .section-title {
            font-size: 1.15rem;
            font-weight: 600;
            color: #1E2925;
            margin-top: 2.6rem;
            margin-bottom: 1rem;
        }

        /* RESULT CARD */

        .result-card {
            background: #FFFFFF;
            border: 1px solid #DDE3DF;
            border-radius: 10px;
            padding: 1.35rem 1.45rem;
            margin-bottom: 0.85rem;
        }

        .result-rank {
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.72rem;
            color: #7A8681;
        }

        .result-name {
            font-size: 1.15rem;
            font-weight: 600;
            color: #1E2925;
            margin-top: 0.25rem;
        }

        .result-meta {
            font-size: 0.86rem;
            color: #68736F;
            margin-top: 0.28rem;
        }

        .evidence-score {
            font-family: "IBM Plex Mono", monospace;
            font-size: 1.25rem;
            font-weight: 500;
            color: #1F5A48;
        }

        /* EVIDENCE SCORE CARDS */

        .evidence-result-top {
            display: grid;
            grid-template-columns: minmax(0, 1fr) 270px;
            gap: 1.25rem;
            align-items: stretch;
            margin-bottom: 1rem;
        }

        .evidence-result-identity {
            padding: 0.2rem 0.1rem;
        }

        .result-name-large {
            font-size: 1.35rem;
            margin-top: 0.35rem;
        }

        .evidence-badges {
            margin-top: 0.35rem;
        }

        .score-card {
            border-radius: 12px;
            padding: 1rem 1.05rem;
            min-height: 132px;
            border: 1px solid rgba(30, 41, 37, 0.06);
        }

        .score-card-main {
            min-height: 170px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .score-kicker {
            font-family: "IBM Plex Mono", monospace;
            font-size: 0.69rem;
            font-weight: 500;
            letter-spacing: 0.045em;
            color: #5E6A65;
            margin-bottom: 0.35rem;
        }

        .score-number-main {
            font-family: "IBM Plex Mono", monospace;
            font-size: 2.25rem;
            line-height: 1.05;
            font-weight: 600;
            color: #1E2925;
        }

        .score-number {
            font-family: "IBM Plex Mono", monospace;
            font-size: 1.35rem;
            line-height: 1.15;
            font-weight: 600;
            color: #1E2925;
            margin-bottom: 0.35rem;
        }

        .score-strength {
            font-size: 0.86rem;
            font-weight: 600;
            color: #34433D;
            margin-top: 0.4rem;
        }

        .score-description {
            font-size: 0.79rem;
            line-height: 1.42;
            color: #5E6A65;
            margin-top: 0.35rem;
        }

        .score-excellent {
            background: #E7F4EA;
        }

        .score-good {
            background: #EFF5E8;
        }

        .score-moderate {
            background: #FFF3D8;
        }

        .score-low {
            background: #F9E7E6;
        }

        .score-na {
            background: #EEF1EF;
        }

        .convergence-strong {
            background: #EDE7F5;
        }

        .convergence-partial {
            background: #F1ECF7;
        }

        .convergence-limited {
            background: #EEF2F7;
        }

        .convergence-none {
            background: #EEF2F4;
        }

        .convergence-na {
            background: #F0F2F1;
        }

        .convergence-label {
            font-size: 0.78rem;
            font-weight: 600;
            color: #665779;
            margin-top: 0.15rem;
            margin-bottom: 0.15rem;
        }

        .score-explanation {
            background: #F6F8F6;
            border: 1px solid #E1E6E2;
            border-radius: 9px;
            padding: 0.8rem 0.95rem;
            margin-top: 0.85rem;
            margin-bottom: 0.8rem;
            font-size: 0.83rem;
            line-height: 1.48;
            color: #53605B;
        }

        .score-explanation strong {
            color: #26342F;
            margin-right: 0.25rem;
        }

        .tag-research {
            background: #F0EDF4;
            color: #65517E;
        }

        @media (max-width: 1100px) {

            .hero-title,
            .hero-text {
                white-space: normal;
            }

            .hero-title {
                max-width: 820px;
            }

            .hero-text {
                max-width: 760px;
            }
        }

        @media (max-width: 760px) {

            .evidence-result-top {
                grid-template-columns: 1fr;
            }

            .score-card-main {
                min-height: auto;
            }
        }

        /* TAGS */

        .tag {
            display: inline-block;
            margin-right: 0.35rem;
            margin-top: 0.7rem;
            padding: 0.25rem 0.5rem;
            border-radius: 5px;
            font-size: 0.72rem;
            font-weight: 500;
        }

        .tag-regulatory {
            background: #EAF2EE;
            color: #1F5A48;
        }

        .tag-clinical {
            background: #EDF2F5;
            color: #3F6F8F;
        }

        .tag-tcm {
            background: #F6EFE7;
            color: #8A592C;
        }

        .tag-mapping {
            background: #F0EDF4;
            color: #65517E;
        }

        /* SEARCH */

        div[data-baseweb="input"] {
            border-radius: 8px;
        }

        div[data-baseweb="tab-list"] {
            gap: 1rem;
        }

        button[data-baseweb="tab"] {
            font-family: "IBM Plex Sans", sans-serif;
        }

        </style>
        """
    )


def render_header():

    col_logo, col_title, col_badge = st.columns(
        [0.75, 4.8, 1.7],
        vertical_alignment="center",
    )

    with col_logo:

        logo_path = Path(
            "assets/phythera_gesundheitslogo.png"
        )

        if logo_path.exists():

            st.image(
                str(logo_path),
                width=90,
            )

        else:

            st.html(
                """
                <div style="
                    width:72px;
                    height:72px;
                    border:1px solid #CED6D2;
                    border-radius:18px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    color:#1F5A48;
                    font-weight:600;
                    font-size:1.25rem;
                    background:#FFFFFF;
                ">
                    PT
                </div>
                """
            )

    with col_title:
        st.html(
            """
            <div style="
                padding-left:0.15rem;
                padding-top:0.35rem;
                padding-bottom:0.35rem;
            ">
                <div style="
                    font-size:1.55rem;
                    font-weight:600;
                    letter-spacing:-0.03em;
                    color:#1E2925;
                    line-height:1.15;
                ">
                    PhyThera
                </div>

                <div style="
                    font-size:0.78rem;
                    color:#68736F;
                    margin-top:0.2rem;
                    letter-spacing:0.01em;
                ">
                    Evidence Navigation for Phytotherapy
                </div>
            </div>
            """
        )

    with col_badge:
        st.html(
            """
            <div style="
                display:flex;
                justify-content:flex-end;
            ">
                <div class="hcp-badge">
                    For healthcare professionals
                </div>
            </div>
            """
        )


def render_hero():
    st.html(
        """
        <div class="hero-kicker">
            Evidence intelligence for phytotherapy
        </div>

        <div class="hero-title">
            From traditional use to structured scientific evidence.
        </div>

        <div class="hero-text">
            Explore medicinal plants, constituents and indications across European phytotherapy, Traditional Chinese Medicine and modern scientific evidence.
        </div>
        """
    )


def render_demo_result():
    st.html(
        """
        <div class="result-card">

            <div style="
                display:flex;
                justify-content:space-between;
                gap:2rem;
                align-items:flex-start;
            ">

                <div>

                    <div class="result-rank">
                        01 · PLANT
                    </div>

                    <div class="result-name">
                        Panax ginseng C.A.Mey.
                    </div>

                    <div class="result-meta">
                        Araliaceae · Ginseng · 人參 · Ren Shen
                    </div>

                    <span class="tag tag-regulatory">
                        EMA traditional use
                    </span>

                    <span class="tag tag-clinical">
                        Clinical evidence: mixed
                    </span>

                    <span class="tag tag-tcm">
                        TCM documented use
                    </span>

                    <span class="tag tag-mapping">
                        Partial EU ↔ TCM overlap
                    </span>

                </div>

                <div style="
                    text-align:right;
                    min-width:125px;
                ">

                    <div class="result-rank">
                        EVIDENCE
                    </div>

                    <div class="evidence-score">
                        pending
                    </div>

                    <div class="result-meta">
                        score model
                    </div>

                </div>

            </div>

        </div>
        """
    )