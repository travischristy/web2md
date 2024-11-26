from web2md import Web2MD

urls = [
    # Getting Started
    "https://www.suno.wiki/faq/getting-started/",
    "https://www.suno.wiki/faq/getting-started/simple-mode/",
    "https://www.suno.wiki/faq/getting-started/how-do-i-write-a-simple-prompt/",
    "https://www.suno.wiki/faq/getting-started/custom-mode-how-do-i-write-a-style-prompt/",
    "https://www.suno.wiki/faq/getting-started/custom-mode-how-do-i-write-lyrics/",
    
    # Making Music
    "https://www.suno.wiki/faq/making-music/",
    "https://www.suno.wiki/faq/making-music/how-do-i-make-the-song-longer/",
    "https://www.suno.wiki/faq/making-music/my-words-are-wrong-after-continue/",
    "https://www.suno.wiki/faq/making-music/extend-from-time/",
    "https://www.suno.wiki/faq/making-music/how-do-i-end-the-song/",
    "https://www.suno.wiki/faq/making-music/why-cant-i-hear-my-lyrics/",
    
    # Metatags
    "https://www.suno.wiki/faq/metatags/",
    "https://www.suno.wiki/faq/metatags/verse-and-chorus/",
    "https://www.suno.wiki/faq/metatags/pre-chorus-and-bridge/",
    "https://www.suno.wiki/faq/metatags/song-structure/",
    "https://www.suno.wiki/faq/metatags/instrumental-tags/",
    "https://www.suno.wiki/faq/metatags/voice-tags/",
    
    # Style and Lyrics
    "https://www.suno.wiki/faq/style-and-lyrics/",
    "https://www.suno.wiki/faq/style-and-lyrics/styles-and-genres/",
    "https://www.suno.wiki/faq/style-and-lyrics/prompts-for-ai-dance-music/",
    "https://www.suno.wiki/faq/style-and-lyrics/should-my-style-prompt-use-commas/",
    "https://www.suno.wiki/faq/style-and-lyrics/how-do-i-make-an-instrumental/",
    "https://www.suno.wiki/faq/style-and-lyrics/voice-hallucinations/",
    "https://www.suno.wiki/faq/style-and-lyrics/duets/"
]

if __name__ == '__main__':
    converter = Web2MD(output_dir='suno_wiki_output')
    converter.convert_urls_to_markdown(urls, output_filename='suno_wiki_guide.md')
