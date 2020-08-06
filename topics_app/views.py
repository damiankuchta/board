from django.views.generic import CreateView, UpdateView, FormView
from django.shortcuts import reverse, redirect, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from hitcount.views import HitCountMixin
from hitcount.models import HitCount

from boards_app import models as board_models
from . import models
from . import forms

# Create your views here.


class Topic(CreateView, HitCountMixin):
    template_name = "topics_app/topics.html"
    model = models.Post
    fields = ['content']

    def get_success_url(self, **kwargs):
        topic = self.get_context_data()['topic']
        return reverse('topic', args={"page": topic.get_pagnatinated_posts.num_pages}, kwargs={"topic_id": kwargs.get('topic_id')})


    def get_context_data(self, **kwargs):
        context = super(Topic, self).get_context_data()
        context['topic'] = models.Topic.objects.get(id=self.kwargs.get("topic_id"))

        #count views
        hit_count = HitCount.objects.get_for_object(context['topic'])
        self.hit_count(self.request, hit_count)

        context['pagination'] = context['topic'].get_page(page=self.request.GET.get("page", 1))
        return context

    # todo test it
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        topic = models.Topic.objects.get(id=self.kwargs['topic_id'])
        if not topic.can_user_add_new_posts(self.request.user):
            self.form_invalid()
        obj.topic = topic
        return super(self.__class__, self).form_valid(form)



    def form_invalid(self, form):
        return HttpResponse("No Authorization to add the post")

class NewTopic(FormView):
    template_name = "topics_app/new_topic.html"
    form_class = forms.CreateTopicForm


    def get_form_kwargs(self):
        kwargs = super(NewTopic, self).get_form_kwargs()
        kwargs.update({'user': self.request.user,
                       'board': models.Board.objects.get(id=self.kwargs["board_id"])})
        print(kwargs)
        return kwargs


    def form_valid(self, form):
        board = board_models.Board.objects.get(id=self.kwargs['board_id'])
        if board.can_user_add_new_topics(self.request.user):
            topic = form.save()
            self.success_url = reverse("topic", kwargs={"topic_id": topic.id})
            return super(self.__class__, self).form_valid(form)
        return False

    def form_invalid(self, form):
        return HttpResponse("No Authorization to add the post")

@staff_member_required
def close_topic(request, topic_id):
    topic = models.Topic.objects.get(id=topic_id)
    topic.close_topic()
    topic.save()
    return redirect(reverse("topic", kwargs={"topic_id": topic_id}))


@staff_member_required
def open_topic(request, topic_id):
    topic = models.Topic.objects.get(id=topic_id)
    topic.open_topic()
    topic.save()
    return redirect(reverse("topic", kwargs={"topic_id": topic_id}))


class EditPost(UpdateView):
    pass


class EditTopic(UpdateView):
    pass