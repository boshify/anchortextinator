import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai

def get_body_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join([tag.text for tag in soup.find_all(['p', 'div', 'span'])])
    except requests.RequestException as e:
        st.warning(f"Failed to crawl {url}. Error: {e}")
        return None

def get_recommendations(body_text, target_keyword, destination_url):
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    prompt = (f"Target content: {body_text}\n\n"
              f"Destination:{destination_url}\n\n"
              f"Anchor text: {target_keyword}\n\n"
              "Provide 3 recommendations for where an internal link to the destination URL could be added using the specified anchor text. "
              "The anchor text does not have to be exact. It just needs to be contextually similar. "
              "Your output must include the following: \"**Change this sentence:**(insert the sentence here)\n\n**To this:**\"(modified sentence with internal link and anchor text added) "
              "Internal links should be added contextually to existing text. Internal links must closely match the anchor text. If there is no close match, modify so it makes sense to the reader. "
              "Do not output the entire page content. Only output recommendations. Separate recommendations with headings, line breaks, and dividers.")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are an SEO expert who excels at internal linking and anchor text. Your recommendations must be highly logical. They should make sense contextually. Your response must always be in markdown format. Use line breaks, dividers, and bold text to make output easy to read. Do not add introductions, summaries, or conclusions."},
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
