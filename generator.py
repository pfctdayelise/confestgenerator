#!/usr/bin/env python

import argparse
import random
import os
from flask import Flask, request, redirect, url_for, abort

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



parser = argparse.ArgumentParser(description='Generate a Confest workshop idea.')
parser.add_argument('adjectives', help='file containing adjectives, one per line')
parser.add_argument('nouns', help='file containing noun phrases, one per line')
parser.add_argument('audiences', help='file containing audiences (noun phrases), one per line')
parser.add_argument('--n', default=1, type=int, help='Number of ideas to generate')


def generate_one(adjs, nouns, audiences):
    adj = random.choice(adjs)
    noun = random.choice(nouns)
    audience = random.choice(audiences)
    art = 'an' if adj[0].lower() in 'aeiou' else 'a'
    s = '{art} {adj} {n}: For {aud}'.format(art=art.title(),
                                            adj=adj,
                                            n=noun,
                                            aud=audience)
    return s


def process(f):
    lines = [l.strip() for l in f.readlines()]
    lines = [l for l in lines if l]
    return lines

def generate_n(adjs, nouns, aud, n):
    with open(adjs, 'r') as a, open(nouns, 'r') as b, open(aud, 'r') as c:
        adjectives = process(a)
        nouns = process(b)
        audiences = process(c)
    result = [generate_one(adjectives, nouns, audiences) for i in range(n)]
    return result

##########################################################################################


@app.route('/')
def generate():
    adjs = 'uploads/a.txt'
    nouns = 'uploads/b.txt'
    audiences = 'uploads/c.txt'
    n = 1
    result = generate_n(adjs, nouns, audiences, n)
    return '''
    <!doctype html>
    <html>
    <head>
    <title>A Confest Workshop Idea</title>
    <style>
    #contents {{
        height: 200px;
    }}
    </style>
    </head>
    <body>
    <h1>A Confest Workshop Idea</h1>
    <div id="contents">{contents}
    </div>
    <div id="refresh">
    <input type="button" value="Refresh" onClick="window.location.reload()">
    </div>
    <div id="links">
    See <a href="/view/adjectives">Adjectives</a> - <a href="/view/nouns">Nouns</a> - <a href="/view/audiences">Audiences</a>
    </div>
    </body>
    </html>
    '''.format(contents=result[0])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/view/<title>', methods=['GET', 'POST'])
def upload_file(title):
    files = {'adjectives': 'a.txt',
             'nouns': 'b.txt',
             'audiences': 'c.txt'}
    if title not in files:
        abort(404)
    filename = files[title]
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    with open('uploads/{}'.format(filename), 'r') as f:
        contents = f.read()
    return '''
    <!doctype html>
    <title>{title} - view/upload</title>
    <h1>{title} - view/upload</h1>
    <div id="contents">
    <pre>{contents}
    </pre>
    </div>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <div id="links">
    <a href="/">home</a>
    </div>
    '''.format(title=title, contents=contents)



####################################################################################

def main():
    args = parser.parse_args()
    result = generate(args.adjectives, args.nouns, args.audiences, args.n)
    print(result)

if __name__ == "__main__":
    main()

