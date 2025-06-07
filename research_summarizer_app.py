import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Load summarization model
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

# Search arXiv API
def search_arxiv(query, max_results=5):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml-xml')
    entries = soup.find_all('entry')

    papers = []
    for entry in entries:
        papers.append({
            'title': entry.title.text.strip().replace('\n', ' '),
            'summary': entry.summary.text.strip().replace('\n', ' '),
            'link': entry.id.text
        })
    return papers

# Summarize text
def summarize_text(text):
    if len(text.split()) < 50:
        return "Abstract too short for summarization."
    return summarizer(text, max_length=200, min_length=60, do_sample=False)[0]['summary_text']

# Streamlit UI
st.title("📚 AI Research Summarizer Agent")
query = st.text_input("Enter your research topic (e.g., 'quantum machine learning')")

num_results = st.slider("Number of papers", min_value=1, max_value=10, value=5)

if st.button("Search and Summarize"):
    with st.spinner("Fetching and summarizing papers..."):
        papers = search_arxiv(query, num_results)

        if not papers:
            st.warning("No papers found. Try a different query.")
        else:
            for i, paper in enumerate(papers):
                st.subheader(f"{i+1}. {paper['title']}")
                st.markdown(f"[Read Full Paper]({paper['link']})")
                st.write("**Original Abstract:**")
                st.info(paper['summary'])

                st.write("**Summarized Abstract:**")
                summarized = summarize_text(paper['summary'])
                st.success(summarized)

                st.markdown("---")
