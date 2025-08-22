import streamlit as st
import pandas as pd
import re
from pathlib import Path
import html
import altair as alt

# --- Set wide layout ---
st.set_page_config(page_title="NLP Model Test Reports", layout="wide")

# --- Utility functions ---
def plot_metrics(chart_df):
    chart = alt.Chart(chart_df).mark_bar().encode(
        x=alt.X('Metric:N', axis=alt.Axis(labelAngle=0, title=None)),  # Landscape display
        y='Score:Q',
        color='Metric:N',  # Different metrics has different colors
        tooltip=['Metric','Score']
    )
    st.altair_chart(chart, use_container_width=True)


def parse_summary_stats(md_text):
    stats = {}
    for line in md_text.splitlines():
        match = re.match(r"- \*\*(.*?)\*\*: (.*)", line)
        if match:
            key, value = match.groups()
            try:
                value = float(value)
                if value.is_integer():
                    value = int(value)
            except ValueError:
                pass
            stats[key] = value
    return stats


def parse_table(md_text):
    lines = [line for line in md_text.splitlines() if line.strip() and '|' in line]
    
    # Header
    header_line = lines[0]
    header = [html.unescape(h.strip()) for h in header_line.strip('|').split('|')]
    
    rows = []
    for row_line in lines[2:]:  # Skip header + separator
        cells = [html.unescape(c.strip()) for c in row_line.strip('|').split('|')]
        # If there are not enough columns, fill the missing ones with empty strings
        if len(cells) < len(header):
            cells += [''] * (len(header) - len(cells))
        rows.append(cells)
    
    df = pd.DataFrame(rows, columns=header)
    
    # Convert numeric column to float
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    
    return df


def render_table(df):
    if df.empty:
        st.write("No data")
        return

    html_str = '<div style="overflow-x:auto;"><table style="width:100%;border-collapse:collapse;">'

    # Table header
    html_str += '<tr>'
    for col in df.columns:
        html_str += f'<th style="font-weight:bold;text-align:center;padding:6px;border:1px solid #ddd;">{col}</th>'
    html_str += '</tr>'

    # Table rows
    for _, row in df.iterrows():
        html_str += '<tr>'
        for col in df.columns:
            if col.lower() == 'input':  # Input align left
                html_str += f'<td style="text-align:left;vertical-align:top;padding:6px;border:1px solid #ddd;">{row[col]}</td>'
            else:
                html_str += f'<td style="text-align:center;vertical-align:top;padding:6px;border:1px solid #ddd;">{row[col]}</td>'
        html_str += '</tr>'

    html_str += '</table></div>'
    st.markdown(html_str, unsafe_allow_html=True)

# --- Load Reports ---
qa_path = Path("reports/summary_qa.md")
sa_path = Path("reports/summary_sa.md")

qa_text = qa_path.read_text(encoding="utf-8") if qa_path.exists() else ""
sa_text = sa_path.read_text(encoding="utf-8") if sa_path.exists() else ""

# --- Streamlit UI ---
st.title("📊 NLP Model Test Reports Dashboard")

st.sidebar.title("Reports")
report_choice = st.sidebar.radio("Select Report", ("Question Answering", "Sentiment Analysis"))

if report_choice == "Question Answering" and qa_text:
    st.header("Question Answering Report")

    stats = parse_summary_stats(qa_text)
    df = parse_table(qa_text)

    st.subheader("Summary Statistics")
    cols = st.columns(len(stats))
    for i, (k, v) in enumerate(stats.items()):
        cols[i].metric(k, v)

    st.subheader("Detailed Results")
    render_table(df)

    if not df.empty:
        st.subheader("Performance Metrics")
        metric_cols = [c for c in df.columns if any(m in c for m in ["Exact Match", "F1"])]
        chart_df = df[metric_cols].mean().reset_index()
        chart_df.columns = ["Metric", "Score"]
        plot_metrics(chart_df)

elif report_choice == "Sentiment Analysis" and sa_text:
    st.header("Sentiment Analysis Report")

    stats = parse_summary_stats(sa_text)
    df = parse_table(sa_text)

    st.subheader("Summary Statistics")
    cols = st.columns(len(stats))
    for i, (k, v) in enumerate(stats.items()):
        cols[i].metric(k, v)

    st.subheader("Detailed Results")
    render_table(df)

    if not df.empty:
        st.subheader("Performance Metrics")
        metric_cols = [c for c in df.columns if any(m in c for m in ["Accuracy", "Precision", "Recall", "F1"])]
        chart_df = df[metric_cols].mean().reset_index()
        chart_df.columns = ["Metric", "Score"]
        plot_metrics(chart_df)

else:
    st.warning("⚠️ Report file not found or empty.")
