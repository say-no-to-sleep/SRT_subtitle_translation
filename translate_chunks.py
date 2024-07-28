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

def split_translated_text(text, original_chunks):
    words = text.split()
    punctuation_marks = ['。', '，', '？', '！']  # Full stop, comma, question mark, exclamation mark
    
    # Calculate target lengths based on original chunk lengths
    total_original_length = sum(len(' '.join(chunk[2:])) for chunk in original_chunks if len(chunk) > 2)
    target_lengths = [
        int(len(' '.join(chunk[2:])) / total_original_length * len(words)) if len(chunk) > 2 else 0 
        for chunk in original_chunks
    ]
    
    result = []
    start = 0
    
    for target_length in target_lengths:
        if target_length == 0:
            result.append('')
            continue
        
        end = start + target_length
        
        # Look for a punctuation mark to split on
        split_index = min(end, len(words) - 1)
        while split_index > start and not any(words[split_index-1].endswith(mark) for mark in punctuation_marks):
            split_index -= 1
        
        # If we couldn't find a punctuation mark, just split at the target length
        if split_index == start:
            split_index = min(end, len(words))
        
        result.append(' '.join(words[start:split_index]))
        start = split_index
    
    # Add any remaining words to the last chunk
    if start < len(words):
        result[-1] += ' ' + ' '.join(words[start:])
    
    return result

def process_file(input_file, output_file):
    chunks = extract_content(input_file)
    full_text = ' '.join(' '.join(chunk[2:]) for chunk in chunks if len(chunk) > 2)
    
    translated_text = translate_text(full_text)
    split_texts = split_translated_text(translated_text, chunks)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk, text in zip(chunks, split_texts):
            subtitle_number = chunk[0] if chunk[0].isdigit() else ''
            timestamp = chunk[1] if '-->' in chunk[1] else chunk[0]
            f.write(f"{subtitle_number}\n{timestamp}\n{text}\n\n")

def main():
    # Use absolute paths
    input_dir = r'C:\Users\Coffee Nebula\Desktop\Python\chunks'
    output_dir = r'C:\Users\Coffee Nebula\Desktop\Python\chunks_translated'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Get list of all .srt files
    srt_files = [f for f in os.listdir(input_dir) if f.endswith('.srt')]
    
    # Use tqdm for progress bar
    for filename in tqdm(srt_files, desc="Processing files"):
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, filename)
        process_file(input_file, output_file)

if __name__ == "__main__":
    main()