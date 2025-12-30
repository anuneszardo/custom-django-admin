import csv
import json
from datetime import datetime, timedelta

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import Group, User
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.aggregates import Count
from django.db.models.functions.datetime import TruncDay

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.html import format_html

from sample_app.models import *



class MyUltimateAdminSite(AdminSite):
    site_header = 'My Django Admin ultimate guide'
    site_title = 'My Django Admin ultimate guide Administration'
    index_title = 'Welcome to my "sample_app"'
    index_template = 'sample_app/templates/admin/my_index.html'
    login_template = 'sample_app/templates/admin/login.html'

    def get_app_list(self, request, app_label: str | None = None):
        app_dict = self._build_app_dict(request)
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())
        for app in app_list:
            if app['app_label'] == 'auth':
                ordering = {'Users': 1, 'Groups': 2}
                app['models'].sort(key=lambda x: ordering[x['name']])
            else:
                ordering = {"The Choices": 1, "The Questions": 2,
                            "The Authors": 3, "The Authors clone": 4}
                app['models'].sort(key=lambda x: ordering[x['name']])
        return app_list

site = MyUltimateAdminSite()

class QuestionInline(admin.StackedInline):
    model = Question


class AuthorAdmin(admin.ModelAdmin):
    empty_value_display = 'Unknown'
    inlines = [QuestionInline,]
    save_on_top = True
    fieldsets = [
        (None, {'fields': ['name']}),
    ]
    list_display = ('name','createdDate','updatedDate',)
    list_per_page = 50
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        print("Author saved by user %s" %request.user)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(AuthorAdmin, self).get_queryset(request)
        return qs.filter(name__startswith='a')

    def change_view(self, request, object_id, form_url='', extra_context=None):
        nbQuestion = Question.objects.filter(refAuthor=object_id).count()
        response_data = [nbQuestion]

        extra_context = extra_context or {}

        # Serialize and attach the chart data to the template contexz
        as_json = json.dumps(response_data, cls=DjangoJSONEncoder)
        extra_context = extra_context or {"nbQuestion": as_json}
        return super().change_view(request, object_id, form_url, extra_context=extra_context,)

    def changelist_view(self, request, extra_context=None):
        # Aggregate new authors per day
        chart_data = (
            Author.objects.annotate(date=TruncDay("updatedDate"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        print("Json %s"%as_json)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

class AuthorCloneAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Author information", {'fields': ['name','createdDate','updatedDate']}),
    ]
    list_display = ('name','createdDate','updatedDate',)
    search_fields = ('name',)

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'choice_text','votes','createdDate', 'updatedDate',)
    list_filter = ('question__refAuthor','question',)
    ordering = ('-createdDate',)
    search_fields = ('choice_text','question__refAuthor__name','question__question_text',)
    list_select_related = ('question','question__refAuthor',)

class QuestionPublishedListFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ('Published questions')
    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'pub_date'
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('Published', ('Published questions')),
            ('Unpublished', ('Unpublished questions')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'Published':
            return queryset.filter(pub_date__lt=datetime.now())
        if self.value() == 'Unpublished':
            return queryset.filter(pub_date__gte=datetime.now())

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Question information", {
            'fields': ('question_text',)
        }),
        ("Date", {
            'fields': ('pub_date',)
        }),
        ('The author', {
            'classes': ('collapse',),
            'fields': ('refAuthor',),
        }),
    ]
    list_display = ('colored_question_text', 'refAuthor','has_been_published','pub_date','createdDate', 'updatedDate','goToChoices')
    list_display_links = ('refAuthor','colored_question_text', 'goToChoices')
    ordering = ('-pub_date', 'createdDate',)
    date_hierarchy = 'pub_date'
    list_select_related = ('refAuthor',)
    autocomplete_fields = ['refAuthor']
    list_filter = (QuestionPublishedListFilter, 'refAuthor', )

    def has_been_published(self, obj):
        present = datetime.now()
        return obj.pub_date.date() < present.date()

    def make_published(modeladmin, request, queryset):
        queryset.update(pub_date=datetime.now()- timedelta(days=1))

    make_published.short_description = "Mark selected questions as published"

    def colored_question_text(self,obj):
        return format_html('<span style="color: #{};">{}</span>', "ff5733", obj.question_text, )

    has_been_published.boolean = True
    has_been_published.short_description = 'Published?'
    colored_question_text.short_description = 'Question text'

    def goToChoices(self, obj):
        return format_html('<a class="button" href="/admin/sample_app/choice/?question__id__exact={}" target="blank">Choices</a>&nbsp;', obj.pk)

    goToChoices.short_description = 'Choices'

    def export_to_csv(self, request, queryset):
        opts = self.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; \
            filename={}.csv'.format(opts.verbose_name)
        writer = csv.writer(response)
        fields = [field for field in opts.get_fields()
                  if not field.many_to_many and not field.one_to_many]
        # Write a first row with header information
        writer.writerow([field.verbose_name for field in fields])
        # Write data rows
        for obj in queryset:
            data_row = []
            for field in fields:
                value = getattr(obj, field.name)
                if isinstance(value, datetime):
                    value = value.strftime('%d/%m/%Y %H:%M')
                data_row.append(value)
            writer.writerow(data_row)
        return response

    export_to_csv.short_description = 'Export to CSV'

    def make_published_custom(self, request, queryset):
        if 'apply' in request.POST:
            # The user clicked submit on the intermediate form.
            # # Perform our update action:
            queryset.update(pub_date=datetime.now()- timedelta(days=1))
            # Redirect to our admin view after our update has
            # completed with a nice little info message saying
            # our models have been updated:
            self.message_user(request,
                              "Changed to published on {} questions".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

        return render(request, 'admin/sample_app/custom_makepublished.html', context={'questions':queryset})
    make_published_custom.short_description = 'Mark selected questions as published customized'

    actions = [make_published, export_to_csv, make_published_custom]


## Register your models here.
site.register(Author,AuthorAdmin)
site.register(Question,QuestionAdmin)
site.register(Choice,ChoiceAdmin)
site.register(Group)
site.register(User)