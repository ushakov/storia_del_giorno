import random
import subprocess
from typing import List
from dataclasses import dataclass
from pathlib import Path
import re

import edge_tts

import stories


def get_duration(file):
    result = subprocess.run(['ffmpeg', '-i', file], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    duration = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr.decode('utf-8'))
    if duration:
        hours, minutes, seconds = map(float, duration.groups())
        return hours * 3600 + minutes * 60 + seconds
    return 0


@dataclass
class AudioGenerator:
    language: str
    speakers_f: List[str]
    speakers_m: List[str]
    rate: str = '-20%'

    def generate_line(self, text, voice, output_file) -> None:
        communicate = edge_tts.Communicate(text, voice, rate=self.rate)
        last_time = 0
        with open(output_file, 'wb') as f:
            for message in communicate.stream_sync():
                if message['type'] == 'audio':
                    f.write(message['data'])
                elif message['type'] == 'WordBoundary':
                    last_time = message['offset'] + message['duration']
        length = last_time + 8_750_000  # magic number corresponding to silence typically added at the end
        return length / 1e7  # convert to seconds

    def assign_speakers(self, story: stories.DailyStory):
        male_characters = set(line.character for line in story.story.foreign_language if line.gender == 'm')
        female_characters = set(line.character for line in story.story.foreign_language if line.gender == 'f')

        mapping = {
            character: random.choice(self.speakers_m) for character in male_characters
        } | {
            character: random.choice(self.speakers_f) for character in female_characters
        }

        return mapping

    def generate_audio(self, story: stories.DailyStory, output_file: str) -> stories.DailyStory:
        mapping = self.assign_speakers(story)
        
        tmp_dir = Path('./tmp/')
        tmp_dir.mkdir(exist_ok=True)

        out_file = Path(output_file).resolve()

        with open(tmp_dir / 'list.txt', 'w') as list_file:
            cur_time = 0
            for i, line in enumerate(story.story.foreign_language):
                voice = mapping[line.character]
                fname = f'line-{i}-{line.character}.mp3'
                fname = re.sub(r'\s+', '_', fname)
                fname = re.sub(r'[^\w\s-]', '', fname)
                duration = self.generate_line(line.line, voice, tmp_dir / fname)
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

generator = AudioGenerator('it', ['it-IT-ElsaNeural', 'it-IT-IsabellaNeural'], ['it-IT-DiegoNeural', 'it-IT-GiuseppeNeural'])
