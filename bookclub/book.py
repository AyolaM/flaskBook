import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from bookclub.auth import login_required
from bookclub.db import get_db

bp = Blueprint('book', __name__)

@bp.route('/')
def index():
    db = get_db()
    books = db.execute(
        'SELECT b.id, title, author, created, created_by_id, username'
        ' FROM book b JOIN user u ON b.created_by_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('bookshelf/index.html', books=books)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO book (title, author, created_by_id)'
                ' VALUES (?, ?, ?)',
                (title, author, g.user['id'])
            )
            db.commit()
            return redirect(url_for('book.index'))

    return render_template('bookshelf/create.html')


def get_book(id, check_creator=True):
    book = get_db().execute(
        'SELECT b.id, title, author, created, created_by_id, username'
        ' FROM book b JOIN user u ON b.created_by_id = u.id'
        ' WHERE b.id = ?',
        (id,)
    ).fetchone()

    if book is None:
        abort(404, f"Book id {id} doesn't exist.")

    if check_creator and book['created_by_id'] != g.user['id']:
        abort(403)

    return book

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    book = get_book(id)

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE book SET title = ?, author = ?'
                ' WHERE id = ?',
                (title, author, id)
            )
            db.commit()
            return redirect(url_for('book.index'))

    return render_template('bookshelf/update.html', book=book)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_book(id)
    db = get_db()
    db.execute('DELETE FROM book WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('book.index'))

