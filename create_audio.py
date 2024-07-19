# %%
import json
import random
import subprocess
import argparse
import datetime
from pathlib import Path
import re

import edge_tts

import local_init
import stories

# %%
today = datetime.datetime.now().strftime("%Y-%m-%d")


parser = argparse.ArgumentParser(description='Generate audio for a story')
parser.add_argument('--input', default=f'static/stories/daily-{today}.json', help='Input story JSON file')
parser.add_argument('--output', default=f'static/stories/daily-{today}.mp3', help='Output audio file')

args = parser.parse_args()

# %%
def generate(text, voice, output_file) -> None:
    """Main function"""
    communicate = edge_tts.Communicate(text, voice, rate='-20%')
    # communicate.save_sync(output_file)
    last_time = 0
    with open(output_file, 'wb') as f:
        for message in communicate.stream_sync():
            if message['type'] == 'audio':
                f.write(message['data'])
            elif message['type'] == 'WordBoundary':
                last_time = message['offset'] + message['duration']
    length = last_time + 8_750_000  # magic number corresponding to silence typically added at the end
    return length / 1e7  # convert to seconds

# %%
story_json = json.load(open(args.input))
story = stories.DailyStory.parse_obj(story_json)

# %%
speakers_f = [
    'it-IT-ElsaNeural',
    'it-IT-IsabellaNeural',
]
speakers_m = [
    'it-IT-DiegoNeural',
    'it-IT-GiuseppeNeural',
]
# %%
male_characters = set(line.character for line in story.story.foreign_language if line.gender == 'm')
female_characters = set(line.character for line in story.story.foreign_language if line.gender == 'f')

# %%
mapping = {
    character: random.choice(speakers_m) for character in male_characters
} | {
    character: random.choice(speakers_f) for character in female_characters
}
# %%
def get_duration(file):
    result = subprocess.run(['ffmpeg', '-i', file], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    duration = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr.decode('utf-8'))
    if duration:
        hours, minutes, seconds = map(float, duration.groups())
        return hours * 3600 + minutes * 60 + seconds
    return 0

def generate_audio(story: stories.DailyStory, mapping: dict[str, str], output_file: str) -> stories.DailyStory:
    tmp_dir = Path('./tmp/')
    tmp_dir.mkdir(exist_ok=True)

    out_file = Path(output_file).resolve()

    with open(tmp_dir / 'list.txt', 'w') as list_file:
        cur_time = 0
        for i, line in enumerate(story.story.foreign_language):
            voice = mapping[line.character]
            fname = f'line-{i}-{line.character}.mp3'
            duration = generate(line.line, voice, tmp_dir / fname)
            actual_duration = get_duration(tmp_dir / fname)
            if actual_duration != 0:
                duration = actual_duration

            print(f'file {fname}', file=list_file)
            
            line.start_sec = cur_time
            line.end_sec = cur_time + duration

            story.story.english[i].start_sec = line.start_sec
            story.story.english[i].end_sec = line.end_sec

            cur_time += duration

    res = subprocess.run(['ffmpeg', '-f', 'concat', '-i', 'list.txt', '-c', 'copy', '-y', str(out_file.absolute())], cwd=tmp_dir)
    if res.returncode != 0:
        raise RuntimeError(f'ffmpeg failed with code {res.returncode}')
    
    subprocess.run(['rm', '-rf', tmp_dir])
    return story

# %%
story = generate_audio(story, mapping, args.output)
# %%
with open(args.input, 'w') as f:
    f.write(story.json(indent=2))
