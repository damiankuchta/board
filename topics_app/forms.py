from django import forms

from .models import Topic, Post

class CreateTopicForm(forms.Form):

    title = forms.CharField()
    content = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.board = kwargs.pop('board', None)
        super(CreateTopicForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
       topic = Topic(title=self.cleaned_data['title'],
                     user=self.user,
                     board=self.board)
       topic.save()

       post = Post(content=self.cleaned_data['content'],
                   user=self.user,
                   topic=topic,
                   is_topic_post=True)
       post.save()

       return topic