# -*- coding:utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView

from locations.models import Location
from locations.utils import subregion_list
from users.models import Profile

class LocationView(TemplateView):
    template_name = 'locations/base.html'

    def update_context(self):
        """ Override in child classes to add context variables """
        return {}

    def get_context_data(self, **kwargs):
        ctx = super(LocationView, self).get_context_data(**kwargs)

        loc_id = int(kwargs['loc_id'])
        try:
            self.location = location = Location.objects.select_related().get(id=loc_id)
        except Location.DoesNotExist:
            raise Http404(u'Район не найден')

        tab = self.request.GET.get('tab', '')
        if tab not in ('wall', 'map', 'tools'):
            tab = 'wall'

        from elements.models import EntityLocation
        from django.contrib.contenttypes.models import ContentType
        entities_by_ct = EntityLocation.objects.for_location(loc_id)
        profile_ct_id = ContentType.objects.get_for_model(Profile).id

        # TODO: get related info instead
        # TODO: get top 3 instances (using points to sort?)
        profiles = []
        if entities_by_ct.get(profile_ct_id):
            profiles = list(Profile.objects.filter(id__in=entities_by_ct[profile_ct_id]))

        # TODO: automate generating it + move it to class attributes (?)
        # TODO: come back to several views
        tabs = [
            ('wall', u'Стена', location.get_absolute_url()+'?tab=wall', 'locations/wall.html', ''),
            ('map', u'Карта', location.get_absolute_url()+'?tab=map', 'locations/map.html', ''),
            ('tools', u'Инструменты', location.get_absolute_url()+'?tab=tools', 'locations/tools.html', ''),
        ]

        ctx.update({
            'loc_id': kwargs['loc_id'],
            'tab': tab,
            'tabs': tabs,
            'location': location,
            'subregions': subregion_list(location),
            'participants': profiles,
        })

        ctx.update(self.update_context())
        return ctx

def get_subregions(request):
    if not request.is_ajax():
        return HttpResponse('[]')

    loc_id = request.GET.get('loc_id', '')

    if loc_id:
        try:
            location = Location.objects.get(id=int(loc_id))
        except ValueError, Location.DoesNotExist:
            return HttpResponse('[]')
    else:
        location = None

    return HttpResponse(json.dumps(subregion_list(location), ensure_ascii=False))

# TODO: take tab as a parameter
def goto_location(request):
    loc_id = request.GET.get('loc_id', '')

    try:
        int(loc_id)
    except ValueError:
        return HttpResponseRedirect(reverse('main')) # TODO: redirect to country page?

    url = reverse('location', args=[loc_id])
    return HttpResponseRedirect(url)
