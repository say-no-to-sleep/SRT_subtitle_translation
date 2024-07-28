import re

def increment_subtitle_numbers(input_file, output_file, start_number):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        content = infile.read()
        
        # Split the content into subtitle blocks
        subtitle_blocks = re.split(r'\n\s*\n', content)
        
        current_number = 1
        for block in subtitle_blocks:
            lines = block.split('\n')
            if lines and lines[0].isdigit():
                subtitle_number = int(lines[0])
                if subtitle_number >= start_number:
                    lines[0] = str(subtitle_number + 1)
                else:
                    lines[0] = str(current_number)
                current_number += 1
            
            outfile.write('\n'.join(lines) + '\n\n')

def main():
    input_file = r'C:\Users\Coffee Nebula\Desktop\Python\combined_translated.srt'
    output_file = r'C:\Users\Coffee Nebula\Desktop\Python\combined_translated_incremented.srt'
    start_number = 1538 # The number from which to start incrementing
    
    increment_subtitle_numbers(input_file, output_file, start_number)
    print(f"Subtitle numbers have been incremented. New file created: {output_file}")

if __name__ == "__main__":
    main()