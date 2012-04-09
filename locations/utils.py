# -*- coding:utf-8 -*-
from locations.models import Location
from services.cache import cache_function

# TODO: add titles choosing command strings
@cache_function(lambda args, kwargs: 'subregions/'+(str(args[0].id) if args[0] else '0'), 500)
def subregion_list(location=None):
    """ location=None for country """
    if location is None or location.is_country():
        res = [('', u'Выбрать субъект РФ'), None, None] # reserve places for Moscow, St. Petersburg and foreign countries
        for loc_id, name in Location.objects.filter(region=None).order_by('name').values_list('id', 'name'):
            if name == u'Москва':
                res[1] = (loc_id, name)
            elif name == u'Санкт-Петербург':
                res[2] = (loc_id, name)
            #elif name == FOREIGN_TERRITORIES:
            #    res[3] = (loc_id, name)
            else:
                res.append((loc_id, name))
        return res
    elif location.is_region():
        print location.id, location

        print list(Location.objects.filter(region=location, district=None).order_by('name').values_list('id', 'name'))

        return [('', u'Выбрать район')]+list(Location.objects.filter(region=location, district=None)
                .order_by('name').values_list('id', 'name'))
    elif location.is_district():
        return [('', u'Выбрать город')]+list(Location.objects.filter(district=location).order_by('name').values_list('id', 'name'))
    else:
        return []
