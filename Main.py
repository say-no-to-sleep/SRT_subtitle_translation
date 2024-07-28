import srt
from deep_translator import GoogleTranslator
from tqdm import tqdm

def translate_srt(file_path, output_path, source_lang='en', target_lang='zh-CN'):
    # Read the SRT file
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()

    # Parse the SRT content
    subtitles = list(srt.parse(srt_content))
    
    # Initialize the translator
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    
    # Translate the subtitles with progress bar
    translated_subtitles = []
    for subtitle in tqdm(subtitles, desc="Translating subtitles"):
        # Translate the text
        translated_text = translator.translate(subtitle.content)
        
        # Create a new subtitle object with the translated text
        translated_subtitle = srt.Subtitle(index=subtitle.index,
                                           start=subtitle.start,
                                           end=subtitle.end,
                                           content=translated_text)
        translated_subtitles.append(translated_subtitle)
    
    # Convert the list of translated subtitles back to SRT format
    translated_srt = srt.compose(translated_subtitles)
    
    # Write the translated SRT to a new file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(translated_srt)

    print(f"Translation completed. Translated file saved to {output_path}")

# Example usage
translate_srt('Introduction.srt', 'Introduction_CN.srt')
