from .app import app, log


@app.route('/view-page')
def home_page(req):
    log.info('/view-page')
    return {'view_page': 'Hello World'}


@app.resource('/res-view-page', renderer='restful')
class ViewPage(object):
    def __init__(self, request):
        self._name = u'res-view-page'


@ViewPage.GET()
def view_get(root, request):
    return {
        'hello': 'world from even get %s' % root._name
    }


@ViewPage.POST()
def view_post(root, request):
    log.info(request.params)

    log.info(root._name)
    params = request.params
    log.info(params.get('ok'))
    return {
        'post': 'event post post'
    }


def includeme(config):
    pass
