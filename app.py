from functools import lru_cache
import logging
import os
from datetime import datetime

from flask import Flask, request, redirect, url_for, Response
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.atom import AtomFeed

from parser import parse_list, parse_page, parse_icon


SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)


from db import Topic


@app.route('/')
def home():
    return redirect(url_for('feed'))


@app.route('/topics.atom')
def feed():
    feed = AtomFeed('forum.poehali.net', feed_url=request.url, url=request.url_root, icon=url_for('favicon'))
    for topic in db.session.query(Topic).order_by(Topic.updated.desc()).limit(20).all():
        feed.add(topic.title, topic.body, content_type='html', url=topic.url,
                 published=topic.published, updated=topic.updated)
    db.session.rollback()
    return feed.get_response()


@app.route('/schedule')
@app.route('/schedule/<path:url>')
def scheduler(url=None):
    for url, updated in [('http://' + request.full_path[10:], datetime.now())] if url else parse_list():
        topic = db.session.query(Topic).filter(Topic.url == url).first()
        if topic and topic.updated == updated:
            continue
        title, published, body = parse_page(url)
        if topic:
            topic.title = title
            topic.body = body
            topic.updated = updated
        else:
            topic = Topic(url, title, published, updated, body)
        db.session.add(topic)
    db.session.commit()
    return 'ok'


@app.route('/favicon.ico')
@lru_cache()
def favicon():
    return Response(parse_icon(), mimetype='image/x-icon')
