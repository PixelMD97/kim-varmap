st.title("Data source system")
st.markdown("Select which system(s) you want to extract variables from.")

choice = st.radio(
    "Available source",
    options=["Both", "EPIC", "PDMS"],
    index=["Both", "EPIC", "PDMS"].index(
        st.session_state.get("source_filter", "Both")
    ),
)

st.session_state["source_filter"] = choice
