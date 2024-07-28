import os
import re

def natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def combine_srt_files(input_dir, output_file):
    # Get all .srt files in the input directory
    srt_files = [f for f in os.listdir(input_dir) if f.endswith('.srt')]
    
    # Sort the files naturally (so that 2 comes before 10)
    srt_files.sort(key=natural_sort_key)
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        subtitle_counter = 1
        for filename in srt_files:
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as infile:
                content = infile.read().strip()
                # Split the content into subtitle blocks
                subtitle_blocks = re.split(r'\n\s*\n', content)
                
                for block in subtitle_blocks:
                    lines = block.split('\n')
                    if len(lines) >= 3:  # Ensure we have at least 3 lines (number, timestamp, text)
                        # Write the new subtitle number
                        outfile.write(f"{subtitle_counter}\n")
                        # Write the timestamp and text
                        outfile.write('\n'.join(lines[1:]) + '\n\n')
                        subtitle_counter += 1

def main():
    input_dir = r'C:\Users\Coffee Nebula\Desktop\Python\chunks_translated'
    output_file = r'C:\Users\Coffee Nebula\Desktop\Python\combined_translated.srt'
    
    combine_srt_files(input_dir, output_file)
    print(f"Combined SRT file has been created: {output_file}")

if __name__ == "__main__":
    main()