import streamlit as st
import news_collection_sl
import fact_collection_sl

def upload_news_file():
    st.markdown("<h2><b>Choose your <b>.csv NEWS file</b></h2>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: smaller;'>Please place the news URL and publication date in columns 1 and 2 of the table respectively.</p >", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload multiple.csv news files", type=["csv"], accept_multiple_files=True)

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            news_collection_sl.process_news_file(uploaded_file)
        

def upload_fact_file():
    st.markdown("<h2><b>Choose your <b>.csv FACT file</b></h2>", unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Upload multiple.csv fact files", type=["csv"], accept_multiple_files=True)

    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            fact_collection_sl.process_fact_file(uploaded_file)