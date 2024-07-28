import os
import re
from deep_translator import GoogleTranslator
from tqdm import tqdm

def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip().split('\n\n')
    return [chunk.split('\n') for chunk in content]

def translate_text(text, target_language='zh-CN'):
    translator = GoogleTranslator(source='auto', target=target_language)
    return translator.translate(text)

def process_chunks(chunks):
    processed_chunks = []
    full_text = []
    
    for chunk in chunks:
        if len(chunk) < 2:  # Skip invalid chunks
            continue
        
        subtitle_number = chunk[0] if chunk[0].isdigit() else ''
        timestamp = chunk[1] if '-->' in chunk[1] else chunk[0]
        text = ' '.join(chunk[2:]) if len(chunk) > 2 else ''
        
        processed_chunks.append((subtitle_number, timestamp))
        full_text.append(text)
    
    return processed_chunks, ' '.join(full_text)

def character_weight(char):
    """Determine the visual weight of a character."""
    if '\u4e00' <= char <= '\u9fff':  # Chinese character range
        return 2
    elif char.isascii():
        return 1
    else:
        return 2  # Treat other characters (e.g., punctuation) as full-width

def split_translated_text(text, chunk_count):
    """Split the translated text into chunks based on visual weight and punctuation."""
    # Calculate total weight of the text
    total_weight = sum(character_weight(char) for char in text)
    
    # Calculate target weight per chunk
    target_weight_per_chunk = total_weight / chunk_count
    
    chunks = []
    current_chunk = []
    current_weight = 0
    
    words = re.findall(r'\S+|\s+', text)
    
    for word in words:
        word_weight = sum(character_weight(char) for char in word)
        
        if current_weight + word_weight > target_weight_per_chunk and current_chunk:
            # Check if there's a punctuation mark near the end
            chunk_text = ''.join(current_chunk)
            match = re.search(r'[，。！？；：、](?=[^，。！？；：、]{0,5}$)', chunk_text)
            if match:
                split_index = match.end()
                chunks.append(chunk_text[:split_index])
                current_chunk = [chunk_text[split_index:]]
                current_weight = sum(character_weight(char) for char in current_chunk[0])
            else:
                chunks.append(chunk_text)
                current_chunk = []
                current_weight = 0
        
        current_chunk.append(word)
        current_weight += word_weight
    
    # Add any remaining text as the last chunk
    if current_chunk:
        chunks.append(''.join(current_chunk))
    
    # If we have fewer chunks than expected, add empty strings
    while len(chunks) < chunk_count:
        chunks.append('')
    
    return chunks

def process_file(input_file, output_file):
    chunks = extract_content(input_file)
    full_text = ' '.join(' '.join(chunk[2:]) for chunk in chunks if len(chunk) > 2)
    
    translated_text = translate_text(full_text)
    split_texts = split_translated_text(translated_text, len(chunks))
    print(split_texts)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk, text in zip(chunks, split_texts):
            subtitle_number = chunk[0] if chunk[0].isdigit() else ''
            timestamp = chunk[1] if '-->' in chunk[1] else chunk[0]
            f.write(f"{subtitle_number}\n{timestamp}\n{text.strip()}\n\n")

        
process_file("chunks/chunk_1.srt", "test.srt")

