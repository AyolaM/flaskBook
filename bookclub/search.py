import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from bookclub.auth import login_required
from bookclub.db import get_db

bp = Blueprint('search', __name__)

@bp.route('/')
def index():
    return render_template('search/index.html')


import requests


@bp.route('/search')
def search():
    query = request.args.get('query')
    response = requests.get(f'http://openlibrary.org/search.json?q={query}&limit=10')
    data = response.json()
    results = data.get('docs', [])
    # extract relevant information from the search results, such as title, author, and cover image URL
    # and store the information in a list of dictionaries to be displayed in the search results template
    search_results = []
    for book in results:
        book_info = {
            'title': book.get('title', ''),
            'author': ', '.join(book.get('author_name', [])),
            'cover_image': f'http://covers.openlibrary.org/b/id/{book.get("cover_i", "")}-M.jpg',
            'id': (book.get('key', '')).replace('/books/', '').replace('/works/', '')
        }
        search_results.append(book_info)

    # render the search results template with the results and the original search query
    return render_template('search/search_results.html', query=query, results=search_results)

@bp.route('/search/<string:id>', methods=('GET',))
def search_detail(id):
    print("call was made")
    # Make an API call to Open Library to get details about the book with the specified ID
    url_to_call = f'http://openlibrary.org/works/{id}.json'
    print(url_to_call)
    response = requests.get(url_to_call)
    if response.status_code == 404:
        return render_template('404.html'), 404
    book_data = response.json()
    book_info = {
        'title': book_data.get('title', ''),
        'author': ', '.join(book_data.get('author_name', [])),
        'description': book_data.get('description'),
        'id': (book_data.get('key', '')).replace('/books/', '').replace('/works/', '')
    }
    return render_template('search/book_detail.html', book=book_info)
