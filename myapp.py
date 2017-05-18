#!/usr/bin/env python
import random
import string

from pieweb import PieWeb, Response

app = PieWeb(__name__)


@app.route('/get/')
def get(request):
    return Response(data=request.GET)


@app.route('/post/')
def post(request):
    return Response(data=request.POST)


@app.route('/json/')
def json(request):
    return Response(data={
        x: ''.join(
            random.choices(string.ascii_uppercase + string.digits, k=20))
        for x in range(10000)
    })


if __name__ == '__main__':
    app.run()
