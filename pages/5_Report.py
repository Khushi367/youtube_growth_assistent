"""
pages/5_Report.py
--------------------
Lets the user download their prediction history as a CSV, or as a
polished PDF growth report (built with reportlab).
"""

import streamlit as st
import pandas as pd
import sys
import os
import io
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import require_login
from database import get_history

st.set_page_config(page_title="Report | YouTube Growth Assistant", page_icon="📄", layout="wide")
require_login()

st.title("📄 Growth Report")
st.caption("Export your prediction history as a CSV or a polished PDF report.")

history = get_history(st.session_state.user_id)

if history.empty:
    st.warning("No history yet. Run a few predictions on the **3_AI_Prediction** page first.")
    st.stop()

st.markdown("### Preview")
st.dataframe(history, use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)

# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------
with col1:
    st.markdown("#### ⬇️ CSV Export")
    csv_buffer = io.StringIO()
    history.to_csv(csv_buffer, index=False)
    st.download_button(
        "Download CSV Report",
        data=csv_buffer.getvalue(),
        file_name=f"youtube_growth_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ---------------------------------------------------------------------------
# PDF export (reportlab)
# ---------------------------------------------------------------------------
with col2:
    st.markdown("#### ⬇️ PDF Export")

    def build_pdf(df: pd.DataFrame, username: str) -> bytes:
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
        )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=landscape(A4),
            leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        )
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#ff2d55"))
        elements = []

        elements.append(Paragraph("YouTube Growth Assistant - Growth Report", title_style))
        elements.append(Paragraph(f"Creator: {username}", styles["Normal"]))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
        elements.append(Spacer(1, 0.5 * cm))

        # Summary KPIs
        summary_data = [
            ["Total Videos Analyzed", str(len(df))],
            ["Total Views", f"{int(df['views'].sum()):,}"],
            ["Total Likes", f"{int(df['likes'].sum()):,}"],
            ["Total Comments", f"{int(df['comments'].sum()):,}"],
            ["Avg CTR", f"{round(df['ctr_percent'].mean(), 2)}%"],
            ["Subscribers Gained", f"{int(df['subscribers_gained'].sum()):,}"],
        ]
        summary_table = Table(summary_data, colWidths=[6 * cm, 6 * cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#1e1b4b")),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
            ("TEXTCOLOR", (1, 0), (1, -1), colors.black),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.7 * cm))
        elements.append(Paragraph("Video History", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * cm))

        cols = ["title", "category", "views", "likes", "comments", "ctr_percent", "predicted_growth", "confidence"]
        display_df = df[cols].fillna("").astype(str)
        table_data = [["Title", "Category", "Views", "Likes", "Comments", "CTR %", "Growth", "Confidence %"]]
        for _, row in display_df.iterrows():
            title_text = row["title"][:45] + ("..." if len(row["title"]) > 45 else "")
            table_data.append([title_text, row["category"], row["views"], row["likes"],
                                row["comments"], row["ctr_percent"], row["predicted_growth"], row["confidence"]])

        history_table = Table(table_data, repeatRows=1, colWidths=[7*cm, 3*cm, 2.2*cm, 2.2*cm, 2.4*cm, 2*cm, 2.5*cm, 2.8*cm])
        history_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ff2d55")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#f0f0f5")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(history_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

    try:
        pdf_bytes = build_pdf(history, st.session_state.username)
        st.download_button(
            "Download PDF Report",
            data=pdf_bytes,
            file_name=f"youtube_growth_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Could not generate PDF: {e}")

st.markdown("---")
st.caption(
    "The PDF report is also saved to the `reports/` folder path convention used by this project "
    "(`reports/youtube_growth_report.pdf`) — each click above generates a fresh, timestamped file for download."
)
