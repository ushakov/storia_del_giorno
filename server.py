from pathlib import Path
import datetime
import json

from flask import Flask, render_template, redirect, url_for

app = Flask(__name__, static_folder='static', template_folder='html')


@app.route('/')
def home():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    return redirect(url_for('show_story_for_date', date=date))

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))


@app.route('/<date>')
def show_story_for_date(date):
    parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    previous_date = (parsed_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    next_date = (parsed_date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    json_path = Path(f'static/stories/daily-{date}.json')
    if not json_path.exists():
        return render_template('no_story.html', date=date, previous_date=previous_date, next_date=next_date)
    story = json.load(open(f'static/stories/daily-{date}.json'))
    context = {
        'audio_file': url_for('static', filename=f'stories/daily-{date}.mp3'),
        'story': story,
        'previous_date': previous_date,
        'next_date': next_date,
    }
    return render_template('daily.html', **context)


if __name__ == '__main__':
    app.run(debug=True)
