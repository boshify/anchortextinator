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

def get_recommendations(body_text, target_keyword, destination_url):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    # Refining the prompt
    prompt = (f"Given the text, identify complete sentences where a link with the anchor text '{target_keyword}' pointing to "
              f"'{destination_url}' can be added. Modify the sentence minimally, ensuring the original meaning is preserved and the anchor text is hyperlinked. "
              f"Provide the recommendations as 'original sentence' with 'modified sentence'.\n\nText: {body_text}\n")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are an SEO expert and master of internal linking."},
            {"role": "user", "content": prompt},
        ]
    )
    
    # Extracting the recommendations
    text = response['choices'][0]['message']['content']
    recommendations = [rec.strip() for rec in text.split('\n') if " with " in rec and target_keyword in rec]
    return recommendations[:3]  # Limit to 3 recommendations

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
                for rec in recommendations:
                    # Displaying the original and modified sentences with enhanced formatting
                    original, modified = rec.split(" with ", 1)  
                    st.markdown(f"### Replace:\n\n{original}\n\n### With:\n\n{modified}", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
