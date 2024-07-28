import os
import re
import time
import logging
from deep_translator import GoogleTranslator
from tqdm import tqdm
import requests

# Set up logging
logging.basicConfig(filename='translation_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def extract_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip().split('\n\n')
    return [chunk.split('\n') for chunk in content]

def translate_text_with_rate_limit(text, target_language='zh-CN', max_retries=5, delay=1):
    translator = GoogleTranslator(source='auto', target=target_language)
    for attempt in range(max_retries):
        try:
            return translator.translate(text)
        except requests.exceptions.RequestException as e:
            logging.warning(f"Translation attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                sleep_time = delay * (2 ** attempt)
                logging.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)  # Exponential backoff
            else:
                logging.error(f"Max retries reached. Translation failed: {str(e)}")
                raise e

def process_chunks(chunks):
    processed_chunks = []
    full_text = []
    
    for chunk in chunks:
        if len(chunk) < 2:  # Skip invalid chunks
            continue
        
        subtitle_number = chunk[0] if chunk[0].isdigit() else ''
        timestamp = chunk[1] if len(chunk) > 1 and '-->' in chunk[1] else chunk[0]
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
    
    # Adjust the number of chunks to match chunk_count
    while len(chunks) != chunk_count:
        if len(chunks) < chunk_count:
            # If we have fewer chunks, split the longest chunk
            longest_chunk_index = max(range(len(chunks)), key=lambda i: len(chunks[i]))
            chunk_to_split = chunks.pop(longest_chunk_index)
            mid = len(chunk_to_split) // 2
            chunks.insert(longest_chunk_index, chunk_to_split[:mid])
            chunks.insert(longest_chunk_index + 1, chunk_to_split[mid:])
        else:
            # If we have more chunks, merge the two shortest
            shortest_chunks = sorted(range(len(chunks)), key=lambda i: len(chunks[i]))[:2]
            new_chunk = chunks[shortest_chunks[0]] + chunks[shortest_chunks[1]]
            chunks = [chunk for i, chunk in enumerate(chunks) if i not in shortest_chunks]
            chunks.append(new_chunk)
    
    return chunks

def process_file(input_file, output_file):
    try:
        logging.info(f"Processing file: {input_file}")
        chunks = extract_content(input_file)
        processed_chunks, full_text = process_chunks(chunks)
        
        logging.info(f"Translating text for file: {input_file}")
        translated_text = translate_text_with_rate_limit(full_text)
        split_texts = split_translated_text(translated_text, len(processed_chunks))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for (subtitle_number, timestamp), text in zip(processed_chunks, split_texts):
                f.write(f"{subtitle_number}\n{timestamp}\n{text.strip()}\n\n")
        
        logging.info(f"Successfully processed and translated file: {input_file}")
    except Exception as e:
        logging.error(f"Error processing file {input_file}: {str(e)}", exc_info=True)
        raise  # Re-raise the exception to stop processing if there's an error

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
        try:
            process_file(input_file, output_file)
        except Exception as e:
            logging.error(f"Failed to process file {filename}: {str(e)}")
            # Optionally, you can break the loop here if you want to stop on first error
            # break

if __name__ == "__main__":
    main()