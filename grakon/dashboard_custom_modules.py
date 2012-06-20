# -*- coding:utf-8 -*-
from admin_tools.dashboard import modules
#from admin_tools.utils import AppListElementMixin, uniquify
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django import forms
from django.contrib.auth.models import User
from services.models import Email
from tools.ideas.models import Idea
from tools.projects.models import Project
from tools.tasks.models import Task
from users.models import Message

#Message
from django.utils.timezone import utc
import qsstats
from qsstats import QuerySetStats

from datetime import datetime,timedelta

class PeriodForm(forms.Form):
    start = forms.DateTimeField()
    end = forms.DateTimeField()
    mailtypes = forms.Select()

class AllRecentActions(modules.RecentActions):
    title = _('Common stats')
    template = 'dashboard/recent_actions.html'
    limit = 10
    include_list = None
    exclude_list = None

    filter_title = _("Select period for report")
    start_title = _("Start")
    end_title= _("End")
    submit_title = _("Apply")

    def init_with_context(self, context):
        if self._initialized:
            return
        from django.db.models import Q
        from django.contrib.admin.models import LogEntry

        request = context['request']
        def get_qset(list):
            qset = None
            for contenttype in list:
                if isinstance(contenttype, ContentType):
                    current_qset = Q(content_type__id=contenttype.id)
                else:
                    try:
                        app_label, model = contenttype.split('.')
                    except:
                        raise ValueError('Invalid contenttype: "%s"' % contenttype)
                    current_qset = Q(
                        content_type__app_label=app_label,
                        content_type__model=model
                    )
                if qset is None:
                    qset = current_qset
                else:
                    qset = qset | current_qset
            return qset
        
        #Data for graphics
        #if len(request.GET)>0 and  request.GET["start"] and request.GET["end"]:
        if len(request.GET)>0 and "start" in request.GET and "end" in request.GET:
            enddate = datetime.strptime(request.GET["end"],'%d.%m.%Y %X').replace(tzinfo=utc)
            startdate = datetime.strptime(request.GET["start"], '%d.%m.%Y %X').replace(tzinfo=utc)
        else:
            enddate = datetime.today().replace(tzinfo=utc)
            startdate = enddate-timedelta(days=30)
        
        mailtype = None
        if len(request.GET)>0 and "mailtype" in request.GET:
            if (request.GET["mailtype"]!="all"):
                mailtype = request.GET["mailtype"]
        
        self.mailtype = mailtype

        self.mailtypes = []
        self.mailtype_title = _("e-mail type")
        self.all_title = _("All")

        for tp in Email.objects.values("type"):
            self.mailtypes.append(tp)
        
        qs = LogEntry.objects.filter(action_time__lte=enddate, action_time__gte=startdate)
        self.periodForm = PeriodForm({"start":startdate,"end":enddate,"mailtypes.choices":self.mailtypes})
        
        if self.include_list:
            qs = qs.filter(get_qset(self.include_list))
        if self.exclude_list:
            qs = qs.exclude(get_qset(self.exclude_list))

        self.children = qs.select_related('content_type', 'user')[:self.limit]

        if not len(self.children):
            self.pre_content = _('No recent actions.')
        
        #E-mails
        if (mailtype):
            mails = Email.objects.filter(type=mailtype)
        else:
            mails = Email.objects.all()
        
        qss = QuerySetStats(mails,"time")
        data = qss.time_series(startdate,enddate)
 
        if (mailtype):
            mailsRead = Email.objects.filter(is_read=True,type=mailtype)
        else:
            mailsRead = Email.objects.filter(is_read=True)

        qss_read = QuerySetStats(mailsRead,"time")
        #data = qss.time_series(startdate,enddate)
        
        self.mail_values = [t[1] for t in data]
        self.mail_captions = [t[0].day for t in data]
        self.mtoday = _("Today: ")+'<strong>%s/%s</strong>'%(qss.this_day(),qss_read.this_day()) + _(' sent/read.') 
        self.mweek =  _("This week: ")+'<strong>%s/%s</strong>' % (qss.this_week(),qss_read.this_week()) + _(' sent/read.')
        self.mmonth = _("This month: ")+ '<strong>%s/%s</strong>'% (qss.this_month(),qss_read.this_month()) + _(' sent/read.')
        #self.iyear =  _("This year: ")+ '<strong>%s</strong>'% qss.this_year() + _(' new idea(s).')
        #self.iuntil_now =  _("Until now: ")+ '<strong>%s</strong>'% qss.until_now() + _(' new idea(s).')

        #Users
        grqs = User.objects.filter(is_active=True)
        qss = QuerySetStats(grqs, 'date_joined')
        data = qss.time_series(startdate, enddate)
        self.uvalues = [t[1] for t in data]
        self.ucaptions = [t[0].day for t in data]
        self.utoday = _("Today: ")+'<strong>%s</strong>' % qss.this_day() + _(' new account(s).') 
        self.uweek =  _("This week: ")+'<strong>%s</strong>' % qss.this_week() + _(' new account(s).')
        self.umonth =  _("This month: ")+ '<strong>%s</strong>'% qss.this_month() + _(' new account(s).')
        #self.uyear =  _("This year: ")+ '<strong>%s</strong>'% qss.this_year() + _(' new account(s).')
        #self.uuntil_now =  _("Until now: ")+ '<strong>%s</strong>'% qss.until_now() + _(' new account(s).')
        
        #Ideas
        ideasQs = Idea.objects.all()
        #ct = ContentType.objects.get(model='idea')
        #ideasQs = ideasQs.filter(get_qset([ct]))
        qss = QuerySetStats(ideasQs,"add_time")
        data = qss.time_series(startdate,enddate)
        self.idea_values = [t[1] for t in data]
        self.idea_captions = [t[0].day for t in data]
        self.itoday = _("Today: ")+'<strong>%s</strong>' % qss.this_day() + _(' new idea(s).') 
        self.iweek =  _("This week: ")+'<strong>%s</strong>' % qss.this_week() + _(' new idea(s).')
        self.imonth =  _("This month: ")+ '<strong>%s</strong>'% qss.this_month() + _(' new idea(s).')
        #self.iyear =  _("This year: ")+ '<strong>%s</strong>'% qss.this_year() + _(' new idea(s).')
        #self.iuntil_now =  _("Until now: ")+ '<strong>%s</strong>'% qss.until_now() + _(' new idea(s).')

        #Projects
        projectQs = Project.objects.all()
        #ct = ContentType.objects.get(model='project')
        #projectQs = projectQs.filter(get_qset([ct]))
        #print "Count of projects:", projectQs.count()

        qss = QuerySetStats(projectQs,"add_time")
        data = qss.time_series(startdate,enddate)
        self.project_values = [t[1] for t in data]
        self.project_captions = [t[0].day for t in data]
        self.ptoday = _("Today: ")+'<strong>%s</strong>' % qss.this_day() + _(' new project(s).') 
        self.pweek =  _("This week: ")+'<strong>%s</strong>' % qss.this_week() + _(' new project(s).')
        self.pmonth =  _("This month: ")+ '<strong>%s</strong>'% qss.this_month() + _(' new project(s).')
        #self.pyear =  _("This year: ")+ '<strong>%s</strong>'% qss.this_year() + _(' new project(s).')
        #self.puntil_now =  _("Until now: ")+ '<strong>%s</strong>'% qss.until_now() + _(' new project(s).')

        #Tasks
        taskQs = Task.objects.all()
        #ct = ContentType.objects.get(model='task')
        #taskQs = taskQs.filter(get_qset([ct]))
        qss = QuerySetStats(taskQs,"add_time")
        data = qss.time_series(startdate,enddate)
        self.task_values = [t[1] for t in data]
        self.task_captions = [t[0].day for t in data]
        self.ttoday = _("Today: ")+'<strong>%s</strong>' % qss.this_day() + _(' new task(s).') 
        self.tweek =  _("This week: ")+'<strong>%s</strong>' % qss.this_week() + _(' new task(s).')
        self.tmonth =  _("This month: ")+ '<strong>%s</strong>'% qss.this_month() + _(' new task(s).')
        #self.eyear =  _("This year: ")+ '<strong>%s</strong>'% qss.this_year() + _(' new task(s).')
        #self.euntil_now =  _("Until now: ")+ '<strong>%s</strong>'% qss.until_now() + _(' new task(s).')

        #Messages
        messageQs = Message.objects.all()
        #ct = ContentType.objects.get(model='message')
        #messageQs = messageQs.filter(get_qset([ct]))
        qss = QuerySetStats(messageQs,"time")
        data = qss.time_series(startdate,enddate)
        self.message_values = [t[1] for t in data]
        self.message_captions = [t[0].day for t in data]
        self.mstoday = _("Today: ")+'<strong>%s</strong>' % qss.this_day() + _(' new message(s).') 
        self.msweek =  _("This week: ")+'<strong>%s</strong>' % qss.this_week() + _(' new message(s).')
        self.msmonth =  _("This month: ")+ '<strong>%s</strong>'% qss.this_month() + _(' new message(s).')

        self._initialized = True
