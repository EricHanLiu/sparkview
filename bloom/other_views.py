from __future__ import unicode_literals
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def release_notes(request):
    """
    We just have to write release notes in this html file
    :param request:
    :return:
    """
    return render(request, 'release_notes.html')
