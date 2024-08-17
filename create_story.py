import json
from datetime import datetime

from dataclasses import dataclass
import jsonargparse

import text
import audio

@dataclass
class Opts:
    date: str = datetime.now().strftime('%Y-%m-%d')


if __name__ == '__main__':
    opts = jsonargparse.CLI(Opts, as_positional=False)

    story_fname = f'static/stories/daily-{opts.date}.json'
    audio_fname = f'static/stories/daily-{opts.date}.mp3'

    story = text.generator.generate_story()
    story = audio.generator.generate_audio(story, audio_fname)
    with open(story_fname, 'w') as f:
        json.dump(story.dict(), f, indent=2)
