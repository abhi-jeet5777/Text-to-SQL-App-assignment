import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from bedrock_utils import get_sql_from_nl
from sql_utils import get_schema, run_sql

st.set_page_config(page_title="Text-to-SQL with Bedrock", layout="wide")
st.title("Text-to-SQL Query App")

db_path = "chinook.db"
schema = get_schema(db_path)

nl_query = st.text_area("Enter your question in natural language")

if st.button("Generate SQL & Run"):
    if nl_query.strip():
        with st.spinner("Generating SQL using Bedrock..."):
            sql_query = get_sql_from_nl(nl_query, schema)
        st.code(sql_query, language="sql")

        df, error = run_sql(db_path, sql_query)
        if error:
            st.error(f"Error executing SQL: {error}")
        elif df.empty:
            st.warning("No data returned.")
        else:
            st.subheader("Results")
            st.dataframe(df)

            # Heuristics to decide plot
            chart_type = None
            if any(x in nl_query.lower() for x in ["trend", "over time", "growth"]):
                chart_type = "line"
            elif any(x in nl_query.lower() for x in ["distribution", "share", "ratio", "percent"]):
                chart_type = "pie"
            elif any(x in nl_query.lower() for x in ["compare", "comparison", "most", "top", "count"]):
                chart_type = "bar"

            if chart_type:
                st.subheader("Visualization")
                fig, ax = plt.subplots()

                try:
                    if chart_type == "bar":
                        df.plot(kind="bar", x=df.columns[0], y=df.columns[1], ax=ax)
                    elif chart_type == "line":
                        df.plot(kind="line", x=df.columns[0], y=df.columns[1], ax=ax)
                    elif chart_type == "pie":
                        df.set_index(df.columns[0]).plot.pie(y=df.columns[1], ax=ax, autopct='%1.1f%%')
                    st.pyplot(fig)
                except Exception as e:
                    st.warning(f"Could not plot graph: {e}")
