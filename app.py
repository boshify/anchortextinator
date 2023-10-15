import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import http.client

def get_body_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'
    }
    try:
        # Prevent http.client from raising an exception for too many headers
        http.client._MAXHEADERS = 1000  # Increase max header limit
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join([tag.text for tag in soup.find_all(['p', 'div', 'span'])])
    except requests.RequestException as e:
        st.warning(f"Failed to crawl {url}. Error: {e}")
        return None
    finally:
        http.client._MAXHEADERS = 100  # Reset max header limit to default

def get_recommendations(body_text, target_keyword, destination_url):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    prompt = (f"Given the text, where would you suggest adding a link with the anchor text '{target_keyword}' pointing to '{destination_url}'? "
              f"Please specify if the keyword can be directly linked or if a modification to the sentence is needed.\n\nText: {body_text}\n")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
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
        total_urls = len(urls)
        progress_bar = st.progress(0)
        
        for index, url in enumerate(urls, start=1):
            body_text = get_body_text(url)
            if body_text:
                truncated_text = body_text[:5000]
                recommendations = get_recommendations(truncated_text, target_keyword, destination_url)
                box_content = f"**Recommendations for {url}**\n\n{recommendations}"
                st.markdown(f'<div style="border:2px solid #F0F2F6; padding:10px; border-radius:10px; margin-bottom: 10px;">{box_content}</div>', unsafe_allow_html=True)
                progress_bar.progress(index / total_urls)
        
        progress_bar.empty()  # Hide progress bar when done

    st.markdown("---")  # Horizontal line
    st.markdown('Made by [Jonathanboshoff.com](https://jonathanboshoff.com)')

if __name__ == "__main__":
    main()
