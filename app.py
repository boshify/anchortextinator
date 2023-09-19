import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

def get_body_text(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join([p.text for p in soup.find_all('p')])
    except Exception as e:
        st.warning(f"Failed to crawl {url}. Error: {e}")
        return None

def get_recommendations(body_text, target_keyword):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # Using chat-based approach for gpt-3.5-turbo model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Find the best placements in the text for the keyword '{target_keyword}' linking to a destination page.\n\nText: {body_text}\n"},
        ]
    )
    
    # Assuming the assistant's reply is what we want
    text = response['choices'][0]['message']['content']
    # Splitting the text into separate recommendations for simplicity
    recommendations = text.split('\n')
    return recommendations

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
                recommendations = get_recommendations(body_text, target_keyword)
                st.subheader(f"Recommendations for {url}")
                for idx, rec in enumerate(recommendations, 1):
                    st.text_area(f"Option {idx}", rec)

if __name__ == "__main__":
    main()
