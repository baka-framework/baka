from baka import Baka
from baka.log import log


app = Baka(__name__)


@app.route('/')
def home_index(req):
    log.info('/')
    return {'home_page': 'Hello World'}


@app.route('/home')
def index_home(req):
    log.info('/home')
    return {'index_home': 'Baka Framework'}


@app.resource('/event', renderer='restful')
class EventPage(object):
    def __init__(self, request):
        self._name = u'event_page'


@EventPage.GET()
def event_get(root, request):
    return {
        'hello': 'world from even get %s' % root._name
    }


@EventPage.POST()
def event_post(root, request):
    log.info(request.params)

    log.info(root._name)
    params = request.params
    log.info(params.get('ok'))
    return {
        'post': 'event post post'
    }


@app.error_handler(404, renderer='restful')
def error_page_notfound(context, request):
    return {'found': 'clearing context'}


app.include('simpleapp.view')
