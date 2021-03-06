# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models

from elements.models import BaseEntityManager, BaseEntityModel, entity_class, HTMLField

class ProjectManager(BaseEntityManager):
    def get_info(self, data, ids):
        for id in ids:
            data[id]['providers'] = len(data[id]['resources'])
            if 'none' in data[id]['resources']:
                data[id]['providers'] -= 1

@entity_class(['locations', 'participants', 'resources', 'comments'])
class Project(BaseEntityModel):
    title = models.CharField(u'Формулировка', max_length=250, help_text=u'краткая формулировка сути проекта в одном предложении, например: "Постройка футбольной коробки во дворе домов таких-то"')
    deadline = models.CharField(u'Дедлайн', max_length=250, blank=True, help_text=u'дата, к которой необходимо собрать ресурсы на проект. Лучше не ставить ее слишком близко или далеко. Хороший диапазон от недели до месяца.')
    goals = HTMLField(u'Цели', help_text=u'какие цели преследует проект? Как можно определить, что проект закончен успешно?')
    about = HTMLField(u'План', help_text=u'подробное объяснение плана действий по реализации проекта. Что будет сделано? Когда?')
    team = HTMLField(u'Команда', blank=True, help_text=u'участники проекта на и вовне площадки. Кто уже помогает/помог проекту ресурсами?')

    objects = ProjectManager()

    entity_name = 'projects'
    entity_title = u'Проекты'
    cache_prefix = 'projects/'
    editable_fields = ['title', 'deadline', 'goals', 'about', 'team']

    roles = ['admin', 'follower']

    follow_button = {
        'role': 'follower',
        'cancel_msg': u'Вы хотите отписаться от новостей об этом проекте?',
        'cancel_btn': u'Отписаться',
        'cancel_btn_long': u'Отписаться',
        'confirm_msg': u'Вы хотите следить за этим проектом?',
        'confirm_btn': u'Следить',
        'confirm_btn_long': u'Следить за проектом',
    }

    def calc_rating(self):
        # Number of people provided resources for project
        info = self.info()

        providers = info['resources'].keys()
        providers_count = len(providers) - 1 if 'none' in providers else len(providers)

        return 5*providers_count + info['participants']['follower']['count']

    @models.permalink
    def get_absolute_url(self):
        return ('project', [self.id])

    def __unicode__(self):
        return self.title

class ProjectIdeas(models.Model):
    project = models.ForeignKey(Project, related_name='ideas')
    idea = models.ForeignKey('ideas.Idea', related_name='projects')

    class Meta:
        unique_together = ('project', 'idea')
