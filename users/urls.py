from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('users.views',
    url(r'^profile$', 'my_profile', name='my_profile'),
    url(r'^profile/edit$', 'edit_profile', name='edit_profile'),
    url(r'^user/(?P<username>[\w\.]+)$', 'view_profile', name='profile'),
)
