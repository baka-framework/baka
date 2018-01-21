from baka import Baka
from baka.log import log


app = Baka(__name__, config_schema=True)


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
    params = request.param
    log.info(params.get('ok'))
    return {
        'post': 'event post post'
    }


@app.exception_handler()
def exception(context, request):
    return {'poll': 'good exception'}


@app.error_handler(500, renderer='restful')
def error_page_notfound(context, request):
    return {'found': 'clearing context'}


@app.error_handler(301, renderer='restful')
def error_page_server(context, request):
    return {'found': 'Internal server error'}

app.include('simpleapp.view')
