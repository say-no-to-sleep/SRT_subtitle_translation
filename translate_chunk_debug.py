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

def split_translated_text(text, chunk_count):
    words = text.split()
    avg_words_per_chunk = len(words) // chunk_count
    punctuation_marks = ['。', '，', '？', '！']  # Full stop, comma, question mark, exclamation mark
    
    result = []
    start = 0
    
    for _ in range(chunk_count - 1):
        end = start + avg_words_per_chunk
        
        # Look for a punctuation mark to split on
        while end < len(words) and not any(words[end-1].endswith(mark) for mark in punctuation_marks):
            end += 1
        
        # If we couldn't find a punctuation mark, just split at the average point
        if end == len(words):
            end = start + avg_words_per_chunk
        
        result.append(' '.join(words[start:end]))
        start = end
    
    # Add the remaining text
    result.append(' '.join(words[start:]))
    
    return result

def process_file(input_file, output_file):
    chunks = extract_content(input_file)
    processed_chunks, full_text = process_chunks(chunks)
    
    translated_text = translate_text(full_text)
    split_texts = split_translated_text(translated_text, len(processed_chunks))
    print(split_texts)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for (subtitle_number, timestamp), text in zip(processed_chunks, split_texts):
            f.write(f"{subtitle_number}\n{timestamp}\n{text}\n\n")
        
        
process_file("chunks/chunk_101.srt", "test.srt")

