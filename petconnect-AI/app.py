import os, sqlite3, uuid, io
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError

ROOT=Path(__file__).resolve().parent
UPLOAD=ROOT/'uploads'; UPLOAD.mkdir(exist_ok=True)
DB=ROOT/'pets.db'
app=Flask(__name__)
app.secret_key=os.environ.get('SECRET_KEY','local-demo-change-this-secret')
app.config['MAX_CONTENT_LENGTH']=8*1024*1024
MODEL=None

def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
    with conn() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY, name TEXT NOT NULL, species TEXT NOT NULL, age TEXT, location TEXT, description TEXT, image TEXT, category TEXT NOT NULL, contact TEXT, created TEXT)''')
        if not c.execute('SELECT COUNT(*) FROM pets').fetchone()[0]:
            c.executemany('INSERT INTO pets (name,species,age,location,description,image,category,contact,created) VALUES (?,?,?,?,?,?,?,?,?)', [
            ('Milo','Dog','Young adult','Talegaon','Friendly and playful. Sample adoption profile.',None,'adoption','Demo listing',datetime.now().isoformat()),
            ('Luna','Cat','Kitten','Pune','Curious and gentle. Sample adoption profile.',None,'adoption','Demo listing',datetime.now().isoformat()),
            ('Coco','Rabbit','Adult','Lonavla','Calm rabbit. Sample adoption profile.',None,'adoption','Demo listing',datetime.now().isoformat())])

def save_image(file):
    if not file or not file.filename: return None
    try:
        raw=file.read(); im=Image.open(io.BytesIO(raw)); im.verify()
        im=Image.open(io.BytesIO(raw)).convert('RGB'); im.thumbnail((1400,1400))
    except (UnidentifiedImageError, OSError, ValueError): raise ValueError('Please upload a valid image.')
    filename=uuid.uuid4().hex+'.jpg'; im.save(UPLOAD/filename,'JPEG',quality=86)
    return filename

@app.route('/')
def home():
    category=request.args.get('category','adoption')
    if category not in ('adoption','lost','found','sale'): category='adoption'
    with conn() as c: pets=c.execute('SELECT * FROM pets WHERE category=? ORDER BY id DESC',(category,)).fetchall()
    return render_template('index.html',pets=pets,category=category)

@app.route('/add',methods=['POST'])
def add():
    name=request.form.get('name','').strip()[:80]; species=request.form.get('species','').strip()[:60]
    category=request.form.get('category','adoption')
    if not name or not species or category not in ('adoption','lost','found','sale'):
        flash('Please enter a name, animal type and valid listing category.','error'); return redirect(url_for('home'))
    try: filename=save_image(request.files.get('image'))
    except ValueError as e: flash(str(e),'error'); return redirect(url_for('home'))
    with conn() as c:
        c.execute('INSERT INTO pets (name,species,age,location,description,image,category,contact,created) VALUES (?,?,?,?,?,?,?,?,?)',(
            name,species,request.form.get('age','')[:60],request.form.get('location','')[:100],request.form.get('description','')[:1200],filename,category,request.form.get('contact','')[:120],datetime.now().isoformat()))
    flash('Listing saved successfully!','success'); return redirect(url_for('home',category=category))

@app.route('/uploads/<path:name>')
def uploaded(name): return send_from_directory(UPLOAD,name)

@app.route('/scan',methods=['POST'])
def scan():
    global MODEL
    try:
        f=request.files.get('image')
        if not f: return jsonify(error='Choose or capture an image first.'),400
        raw=f.read(); im=Image.open(io.BytesIO(raw)).convert('RGB')
        if MODEL is None:
            from transformers import pipeline
            MODEL=pipeline('image-classification',model='google/vit-base-patch16-224')
        predictions=MODEL(im,top_k=5)
        return jsonify(labels=[{'name':p['label'],'confidence':round(p['score']*100,1)} for p in predictions],note='Image recognition estimates only. This model cannot reliably determine an animal’s exact age, health, or identity. For age and health, consult a veterinarian.' )
    except Exception as e:
        app.logger.exception('Scan failed')
        return jsonify(error='AI scanner is unavailable. Install dependencies and ensure internet is available for the first model download.'),503

@app.errorhandler(413)
def large(_): return jsonify(error='Image must be under 8 MB.'),413

init()
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=False)
