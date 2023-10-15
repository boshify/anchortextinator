import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

def get_body_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)  # Added timeout
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extracting text from p, div, and span tags
        return ' '.join([tag.text for tag in soup.find_all(['p', 'div', 'span'])])
    except requests.RequestException as e:  # Modified exception type
        st.warning(f"Failed to crawl {url}. Error: {e}")
        return None

def get_recommendations(body_text, target_keyword, destination_url):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    prompt = (f"Given the text, where would you suggest adding a link with the anchor text '{target_keyword}' pointing to '{destination_url}'? "
              f"Please specify if the keyword can be directly linked or if a modification to the sentence is needed.\n\nText: {body_text}\n")
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an SEO expert and master of internal linking."},
            {"role": "user", "content": prompt},
        ]
    )
    
    return response['choices'][0]['message']['content']

def main():
    st.title('The Anchor Textinator')

    destination_url = st.text_input("Enter destination page URL")
    source_urls = st.text_area("Enter list of source URLs (one per line)")
    target_keyword = st.text_input("Enter target keyword")

    if st.button('Get Recommendations'):
        urls = [url.strip() for url_segment in source_urls.split('\n') for url in url_segment.split('\t') if url.strip()]
        
        for url in urls:
            body_text = get_body_text(url)
            if body_text:
                recommendations = get_recommendations(body_text, target_keyword, destination_url)
                st.subheader(f"Recommendations for {url}")
                st.write(recommendations)

if __name__ == "__main__":
    main()
