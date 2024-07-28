# read from Introduction.srt

srt_content = None

with open('Introduction.srt', 'r', encoding='utf-8') as file:
    srt_content = file.read()

# go through each line in the srt file and mark the lines number of the lines that ends with a period

lines = srt_content.split('\n')
lines_with_period = []

for i, line in enumerate(lines):
    if line.endswith('.'):
        lines_with_period.append(i)

print(lines_with_period)

# separate the srt file into chunks based on the lines that end with a period.
# For example, if the lines with period are [7, 13, 15, 27], then the chunks will be:
# [1 to 7], [8 to 13], [14 to 15], [16 to 27], [28 to end of file]
# And store them in separate files under /chunks folder

import os

# Create a directory to store the chunks
os.makedirs('chunks', exist_ok=True)

# Split the SRT content into chunks based on the lines with period
for i, end_line in enumerate(lines_with_period):
    start_line = lines_with_period[i-1] + 1 if i > 0 else 0
    chunk = '\n'.join(lines[start_line:end_line+1])
    
    # Write the chunk to a new file
    with open(f'chunks/chunk_{i+1}.srt', 'w', encoding='utf-8') as file:
        file.write(chunk)

print("SRT file separated into chunks.")
