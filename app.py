import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="NEXUS | Student Intelligence",
    page_icon="🎓",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #050816, #0b1026);
    color: white;
}

[data-testid="stSidebar"] {
    background: #080d1f;
}

.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    color: #00e5ff;
}

.metric-card {
    background: linear-gradient(145deg, #101936, #0b1229);
    border: 1px solid #1c2d5a;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 0 20px rgba(0,229,255,0.08);
}

.metric-title {
    color: #8ea4d2;
    font-size: 14px;
}

.metric-value {
    color: #00e5ff;
    font-size: 30px;
    font-weight: bold;
}

.risk-high {
    color: #ff4b6e;
    font-weight: bold;
}

.risk-medium {
    color: #ffc857;
    font-weight: bold;
}

.risk-low {
    color: #00ff9c;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.title("🎓 NEXUS")
st.subheader("Student Performance Intelligence System")

st.write(
    "Upload student data to analyse performance, rankings, "
    "risk levels and subject-wise results."
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙️ Control Center")

uploaded_file = st.sidebar.file_uploader(
    "Upload Student CSV",
    type=["csv"]
)


# =========================================================
# MAIN APPLICATION
# =========================================================

if uploaded_file is not None:

    # -----------------------------------------------------
    # LOAD DATA
    # -----------------------------------------------------

    try:
        df = pd.read_csv(uploaded_file)

    except Exception as e:
        st.error(f"Unable to read CSV file: {e}")
        st.stop()

    # Remove spaces from column names
    df.columns = df.columns.str.strip()

    # -----------------------------------------------------
    # REQUIRED COLUMNS
    # -----------------------------------------------------

    subjects = ["Python", "Java", "DBMS"]

    required_columns = ["Name"] + subjects

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error(
            f"❌ Missing columns: {', '.join(missing_columns)}"
        )

        st.info(
            "Your CSV must contain these columns:"
        )

        st.code(
            "Name, Python, Java, DBMS"
        )

        st.write(
            "Columns detected in your CSV:"
        )

        st.write(df.columns.tolist())

        st.stop()

    # -----------------------------------------------------
    # CLEAN DATA
    # -----------------------------------------------------

    for subject in subjects:

        df[subject] = pd.to_numeric(
            df[subject],
            errors="coerce"
        )

    df = df.dropna(
        subset=subjects
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # CALCULATIONS
    # -----------------------------------------------------

    df["Average"] = df[subjects].mean(axis=1)

    df["Total"] = df[subjects].sum(axis=1)

    df["Percentage"] = (
        df["Total"] / (len(subjects) * 100)
    ) * 100

    df["Rank"] = (
        df["Average"]
        .rank(
            ascending=False,
            method="min"
        )
        .astype(int)
    )

    # -----------------------------------------------------
    # RISK CALCULATION
    # -----------------------------------------------------

    def calculate_risk(row):

        average = row["Average"]

        failed_subjects = sum(
            row[subject] < 40
            for subject in subjects
        )

        if average < 40 or failed_subjects >= 2:
            return "HIGH"

        elif average < 60 or failed_subjects == 1:
            return "MEDIUM"

        else:
            return "LOW"

    df["Risk"] = df.apply(
        calculate_risk,
        axis=1
    )

    # -----------------------------------------------------
    # PERFORMANCE CATEGORY
    # -----------------------------------------------------

    def performance_category(avg):

        if avg >= 85:
            return "Excellent"

        elif avg >= 70:
            return "Very Good"

        elif avg >= 60:
            return "Good"

        elif avg >= 40:
            return "Pass"

        else:
            return "Fail"

    df["Performance"] = df["Average"].apply(
        performance_category
    )

    # =====================================================
    # SIDEBAR FILTERS
    # =====================================================

    st.sidebar.markdown("---")
    st.sidebar.subheader("🔎 Filters")

    risk_filter = st.sidebar.multiselect(
        "Risk Level",
        ["LOW", "MEDIUM", "HIGH"],
        default=["LOW", "MEDIUM", "HIGH"]
    )

    performance_filter = st.sidebar.multiselect(
        "Performance",
        [
            "Excellent",
            "Very Good",
            "Good",
            "Pass",
            "Fail"
        ],
        default=[
            "Excellent",
            "Very Good",
            "Good",
            "Pass",
            "Fail"
        ]
    )

    minimum_average = st.sidebar.slider(
        "Minimum Average",
        0,
        100,
        0
    )

    maximum_average = st.sidebar.slider(
        "Maximum Average",
        0,
        100,
        100
    )

    # =====================================================
    # FILTER DATA
    # =====================================================

    filtered_df = df[
        (df["Risk"].isin(risk_filter)) &
        (df["Performance"].isin(performance_filter)) &
        (df["Average"] >= minimum_average) &
        (df["Average"] <= maximum_average)
    ]

    # =====================================================
    # KPI SECTION
    # =====================================================

    st.markdown("## 📊 System Overview")

    total_students = len(df)

    class_average = df["Average"].mean()

    highest_average = df["Average"].max()

    pass_rate = (
        (df["Average"] >= 40).sum()
        / len(df)
    ) * 100

    high_risk = (
        df["Risk"] == "HIGH"
    ).sum()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">TOTAL STUDENTS</div>
                <div class="metric-value">{total_students}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">CLASS AVERAGE</div>
                <div class="metric-value">
                    {class_average:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">HIGHEST SCORE</div>
                <div class="metric-value">
                    {highest_average:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">PASS RATE</div>
                <div class="metric-value">
                    {pass_rate:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">HIGH RISK</div>
                <div class="metric-value">
                    {high_risk}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📈 Analytics",
            "👤 Student Intelligence",
            "🏆 Rankings",
            "⚠️ Risk Center",
            "📋 Dataset"
        ]
    )

    # =====================================================
    # TAB 1 - ANALYTICS
    # =====================================================

    with tab1:

        st.subheader("📚 Subject Performance")

        subject_average = pd.DataFrame({
            "Subject": subjects,
            "Average": [
                df[subject].mean()
                for subject in subjects
            ]
        })

        col1, col2 = st.columns(2)

        with col1:

            fig = px.bar(
                subject_average,
                x="Subject",
                y="Average",
                color="Average",
                color_continuous_scale="blues",
                title="Average Marks by Subject"
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            risk_counts = df["Risk"].value_counts()

            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title="Student Risk Distribution",
                color=risk_counts.index,
                color_discrete_map={
                    "LOW": "#00ff9c",
                    "MEDIUM": "#ffc857",
                    "HIGH": "#ff4b6e"
                }
            )

            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # -------------------------------------------------
        # SCORE DISTRIBUTION
        # -------------------------------------------------

        st.subheader("📊 Score Distribution")

        fig = px.histogram(
            df,
            x="Average",
            nbins=15,
            color="Performance",
            title="Distribution of Student Averages"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # -------------------------------------------------
        # CORRELATION
        # -------------------------------------------------

        st.subheader("🔬 Subject Correlation")

        correlation = df[subjects].corr()

        fig = px.imshow(
            correlation,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Correlation Between Subjects"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # TAB 2 - STUDENT INTELLIGENCE
    # =====================================================

    with tab2:

        st.subheader("👤 Individual Student Analysis")

        selected_student = st.selectbox(
            "Select Student",
            df["Name"].tolist()
        )

        student = df[
            df["Name"] == selected_student
        ].iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Average",
            f"{student['Average']:.1f}%"
        )

        col2.metric(
            "Rank",
            f"#{student['Rank']}"
        )

        col3.metric(
            "Total",
            f"{student['Total']}"
        )

        col4.metric(
            "Risk",
            student["Risk"]
        )

        # -------------------------------------------------
        # RADAR CHART
        # -------------------------------------------------

        st.subheader("🎯 Subject Skill Profile")

        fig = go.Figure()

        fig.add_trace(
            go.Scatterpolar(
                r=[
                    student["Python"],
                    student["Java"],
                    student["DBMS"]
                ],
                theta=subjects,
                fill="toself",
                name=selected_student
            )
        )

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # -------------------------------------------------
        # AI-LIKE RECOMMENDATION ENGINE
        # -------------------------------------------------

        st.subheader("🧠 Performance Intelligence")

        weakest_subject = min(
            subjects,
            key=lambda subject: student[subject]
        )

        strongest_subject = max(
            subjects,
            key=lambda subject: student[subject]
        )

        st.write(
            f"💪 **Strongest Subject:** {strongest_subject} "
            f"({student[strongest_subject]:.1f}%)"
        )

        st.write(
            f"📉 **Weakest Subject:** {weakest_subject} "
            f"({student[weakest_subject]:.1f}%)"
        )

        if student["Risk"] == "HIGH":

            st.error(
                "🚨 HIGH RISK: Immediate academic intervention recommended."
            )

            st.write(
                f"Focus strongly on **{weakest_subject}** "
                "and improve fundamentals."
            )

        elif student["Risk"] == "MEDIUM":

            st.warning(
                "⚠️ MEDIUM RISK: Student requires additional practice."
            )

            st.write(
                f"Recommended focus: **{weakest_subject}**"
            )

        else:

            st.success(
                "🟢 LOW RISK: Student is performing well."
            )

            st.write(
                f"Continue strengthening **{strongest_subject}** "
                "while maintaining other subjects."
            )

        # -------------------------------------------------
        # MARKS TABLE
        # -------------------------------------------------

        student_marks = pd.DataFrame({
            "Subject": subjects,
            "Marks": [
                student[subject]
                for subject in subjects
            ]
        })

        st.dataframe(
            student_marks,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # TAB 3 - RANKINGS
    # =====================================================

    with tab3:

        st.subheader("🏆 Student Ranking")

        ranking_df = df.sort_values(
            "Average",
            ascending=False
        ).copy()

        ranking_df["Rank"] = range(
            1,
            len(ranking_df) + 1
        )

        display_columns = [
            "Rank",
            "Name",
            "Python",
            "Java",
            "DBMS",
            "Average",
            "Performance",
            "Risk"
        ]

        st.dataframe(
            ranking_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("🥇 Top Performers")

        top_students = ranking_df.head(10)

        fig = px.bar(
            top_students,
            x="Average",
            y="Name",
            orientation="h",
            color="Average",
            color_continuous_scale="viridis",
            title="Top 10 Students"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # TAB 4 - RISK CENTER
    # =====================================================

    with tab4:

        st.subheader("⚠️ Student Risk Center")

        high_risk_students = df[
            df["Risk"] == "HIGH"
        ]

        medium_risk_students = df[
            df["Risk"] == "MEDIUM"
        ]

        low_risk_students = df[
            df["Risk"] == "LOW"
        ]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "🔴 High Risk",
            len(high_risk_students)
        )

        col2.metric(
            "🟡 Medium Risk",
            len(medium_risk_students)
        )

        col3.metric(
            "🟢 Low Risk",
            len(low_risk_students)
        )

        st.markdown("---")

        if len(high_risk_students) > 0:

            st.subheader("🔴 Students Requiring Attention")

            st.dataframe(
                high_risk_students[
                    [
                        "Name",
                        "Python",
                        "Java",
                        "DBMS",
                        "Average",
                        "Risk"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "🎉 No high-risk students detected."
            )

        st.subheader("⚠️ Subject Failure Analysis")

        failure_data = []

        for subject in subjects:

            failed = (
                df[subject] < 40
            ).sum()

            failure_data.append({
                "Subject": subject,
                "Failed Students": failed
            })

        failure_df = pd.DataFrame(
            failure_data
        )

        fig = px.bar(
            failure_df,
            x="Subject",
            y="Failed Students",
            color="Failed Students",
            title="Students Below Passing Marks"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # TAB 5 - DATASET
    # =====================================================

    with tab5:

        st.subheader("📋 Student Dataset")

        search = st.text_input(
            "🔎 Search Student"
        )

        dataset_view = filtered_df.copy()

        if search:

            dataset_view = dataset_view[
                dataset_view["Name"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            dataset_view,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------------
        # DOWNLOAD
        # -------------------------------------------------

        csv_data = dataset_view.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Filtered Dataset",
            data=csv_data,
            file_name="student_analysis.csv",
            mime="text/csv"
        )

else:

    # =====================================================
    # WELCOME SCREEN
    # =====================================================

    st.markdown("## 🚀 Welcome to NEXUS")

    st.info(
        "Upload a student CSV file from the sidebar "
        "to activate the intelligence dashboard."
    )

    st.markdown("""
    ### Required CSV format

    Your CSV should contain:

    `Name, Python, Java, DBMS`

    Example:

    | Name | Python | Java | DBMS |
    |---|---:|---:|---:|
    | Rahul | 85 | 72 | 90 |
    | Priya | 78 | 88 | 82 |
    | Amit | 35 | 42 | 38 |
    | Sneha | 92 | 95 | 89 |

    ### Features

    - 📊 Advanced analytics
    - 🏆 Student ranking
    - 👤 Individual profiles
    - 🎯 Radar skill analysis
    - ⚠️ Risk detection
    - 🔬 Subject correlation
    - 🔎 Student search
    - 📥 Data export
    - 🌌 Futuristic interface
    """)
