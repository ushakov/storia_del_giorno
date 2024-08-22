from pathlib import Path
import datetime
import json
import shelve
import os
import time

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import flask
from flask import Flask, render_template, redirect, url_for

import text
import audio

app = Flask(__name__, static_folder='static', template_folder='html')
storage = shelve.open('static/stories/storage')
print('opened storage', [t for t in storage.items()])
bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'], parse_mode=None)

ROOT = os.environ['STORIA_URL']

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


def generate_story():
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    story_fname = f'static/stories/daily-{date}.json'
    audio_fname = f'static/stories/daily-{date}.mp3'

    story = text.generator.generate_story()
    story = audio.generator.generate_audio(story, audio_fname)
    with open(story_fname, 'w') as f:
        json.dump(story.dict(), f, indent=2)

    story_url = f'{ROOT}/{date}'
    
    for user_id, active in storage.items():
        if active:
            bot.send_message(int(user_id), "I've created a new story for you! Check it out here: " + story_url)


@app.route('/tgwebhook', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    storage[str(message.from_user.id)] = True
    storage.sync()
    bot.reply_to(message, "Cool, hi! I'll send you updates until you turn me off with /stop")


@bot.message_handler(commands=['stop'])
def send_welcome(message):
    storage[str(message.from_user.id)] = False
    storage.sync()
    bot.reply_to(message, "I've turned updates off. See ya!")


sched = BackgroundScheduler()
sched.add_job(generate_story, 'cron', hour=5)
sched.start()

bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=f'{ROOT}/tgwebhook')
