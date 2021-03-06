"""
Localized view (i.e. language-specific subsites).
"""

from cStringIO import StringIO
import mimetypes
from os.path import join, exists
import re
import datetime
from PIL import Image

from flask import Blueprint, request, render_template, make_response, g, url_for
from flask import current_app as app
from flask.ext.babel import gettext as _

from ..config import MAIN_MENU, FEED_MAX_LINKS, IMAGE_SIZES
from ..content import Page, get_news, get_page_or_404, get_pages, get_blocks


__all__ = ['setup']

blueprint = Blueprint('localized', __name__, url_prefix='/<string(length=2):lang>')


#
# Menu management
#
class MenuEntry(object):
  def __init__(self, path, label):
    self.path = path
    self.label = label
    self.active = False
    self.css_classes = []

  def __getitem__(self, key):
    if key == 'class':
      return " ".join(self.css_classes)
    raise IndexError


def get_menu():
  menu = []
  for t in MAIN_MENU.get(g.lang, ()):
    entry = MenuEntry(t[0], t[1])

    if entry.path == '':
      if re.match("^/../$", request.path):
        entry.active = True
    else:
      if request.path[len("/../"):].startswith(entry.path):
        entry.active = True
    if entry.active:
      entry.css_classes.append("active")
    if len(t) > 2:
      entry.css_classes.append(t[2])
    menu.append(entry)
  return menu


@blueprint.context_processor
def inject_menu():
  return dict(menu=get_menu())


#
# Deal with language
#
def alt_url_for(*args, **kw):
  if isinstance(args[0], Page):
    page = args[0]
    if re.match("../news/", page.path):
      return url_for(".news_item", slug=page.meta['slug'])
    else:
      return url_for(".page", path=page.meta['path'][3:])
  else:
    return url_for(*args, lang=g.lang, **kw)


@blueprint.context_processor
def inject_context_variables():
  return dict(lang=g.lang,
              url_for=alt_url_for)


@blueprint.url_defaults
def add_language_code(endpoint, values):
  values.setdefault('lang', g.lang)


@blueprint.url_value_preprocessor
def pull_lang(endpoint, values):
  g.lang = values.pop('lang')


#
# Localized routes
#
@blueprint.route('/')
def home():
  template = "index.html"
  page = {'title': 'Open World Forum 2013'}
  news = get_news(lang=g.lang, limit=6)
  blocks = get_blocks(g.lang)
  return render_template(template, page=page, news=news, blocks=blocks)


@blueprint.route('/<path:path>/')
def page(path=""):
  page = get_page_or_404(g.lang + "/" + path + "/index")
  template = page.meta.get('template', '_page.html')
  return render_template(template, page=page)


@blueprint.route('/news/')
def news():
  all_news = get_news(lang=g.lang)
  recent_news = get_news(lang=g.lang, limit=5)
  page = {'title': _("News") }
  return render_template('news.html', page=page, news=all_news,
                         recent_news=recent_news)


@blueprint.route('/news/<slug>/')
def news_item(slug):
  page = get_page_or_404(g.lang + "/news/" + slug)
  recent_news = get_news(lang=g.lang, limit=5)
  return render_template('news_item.html', page=page,
                         recent_news=recent_news)


@blueprint.route('/news/<slug>/image')
def image_for_news(slug):
  assert not '/' in slug
  size = request.args.get('size', 'large')

  file_path = join(app.root_path, "..", "pages", g.lang, "news", slug, "image.png")
  if not exists(file_path):
    file_path = join(app.root_path, "..", "pages", g.lang, "news", slug, "image.jpg")

  if not exists(file_path):
    file_path = join(app.root_path, "static", "pictures", "actu.png")

  img = Image.open(file_path)
  x, y = img.size
  x1, y1 = IMAGE_SIZES[size]
  r = float(x) / y
  r1 = float(x1) / y1
  if r > r1:
    y2 = y1
    x2 = int(float(x) * y1 / y)
    assert x2 >= x1
    img1 = img.resize((x2, y2), Image.ANTIALIAS)
    x3 = (x2-x1)/2
    img2 = img1.crop((x3, 0, x1+x3, y1))
  else:
    x2 = x1
    y2 = int(float(y) * x1 / x)
    assert y2 >= y1
    img1 = img.resize((x2, y2), Image.ANTIALIAS)
    y3 = (y2-y1)/2
    img2 = img1.crop((0, y3, x1, y1+y3))

  assert img2.size == (x1, y1)

  output = StringIO()
  if file_path.endswith(".jpg"):
    img2.save(output, "JPEG")
  else:
    img2.save(output, "PNG")
  data = output.getvalue()

  response = make_response(data)
  response.headers['content-type'] = mimetypes.guess_type(file_path)
  return response


@blueprint.route('/feed/')
def feed():
  news_items = get_news(lang=g.lang, limit=FEED_MAX_LINKS)
  now = datetime.datetime.now()

  response = make_response(render_template('base.rss',
                                           news_items=news_items, build_date=now))
  response.headers['Content-Type'] = 'text/xml'
  return response


@blueprint.route('/sitemap/')
def sitemap():
  page = {'title': _(u"Site map")}
  pages = get_pages()
  pages = [ p for p in pages if p.path.startswith(g.lang) ]

  return render_template('sitemap.html', page=page, pages=pages)


@blueprint.route('/search')
def search():
  page = {'title': _(u"Search results")}
  qs = request.args.get('qs', '')
  whoosh = app.extensions['whoosh']
  results = whoosh.search(qs)
  results = [ r for r in results if r['path'].startswith(g.lang) ]
  return render_template("search.html", page=page, results=results)


@blueprint.errorhandler(404)
def page_not_found(error):
  page = {'title': _(u"Page not found")}
  return render_template('404.html', page=page), 404


#
# Register blueprint on app
#
def register_plugin(app):
  app.register_blueprint(blueprint)
