# -*- coding:utf-8 -*-
from django.http import HttpResponse

from elements.resources.models import EntityResource
from elements.resources.notification import NewResourceNotification
from elements.utils import entity_post_method, provided_entity_method

@entity_post_method
@provided_entity_method
def add_resource(request, entity, provider):
    """ Добавляет ресурс """
    res = EntityResource.objects.add(entity, request.POST.get('resource', ''),
            description=request.POST.get('description', ''), provider=provider)

    if type(res) is not unicode:
        NewResourceNotification.send(res.id)

    # TODO: return error HttpResponse(res) is type(res) is unicode + show it in client
    return HttpResponse('ok')

@entity_post_method
@provided_entity_method
def update_resource(request, entity, provider):
    """ Редактирует существующий ресурс """
    EntityResource.objects.edit(entity, request.POST.get('old_resource', ''),
            request.POST.get('resource', ''), description=request.POST.get('description', ''),
            provider=provider)

    return HttpResponse('ok')

@entity_post_method
@provided_entity_method
def remove_resource(request, entity, provider):
    """ Удаляет ресурс """
    EntityResource.objects.remove(entity, request.POST.get('resource', ''), provider=provider)
    return HttpResponse('ok')
