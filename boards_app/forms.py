from itertools import chain
from sys import modules

from django import forms

from .models import Board, BoardGroup

class BoardAdminForm(forms.ModelForm):

    class Meta:
        model = Board
        exclude = ['content_type', 'object_id']
        fields = ['name', 'description', 'position', 'get_parent',  'visibility', 'visibility_groups',
                  'add_new_posts_restictions', 'new_posts_groups',
                  'add_new_topics_restrictions', 'new_topics_groups']


    #this will be used to pick parent to avoid using generics relations object_id and content_type
    # choices are set in __init__
    get_parent = forms.TypedChoiceField(choices=(None, None))

    def return_model_choice(self, object):
        return  ("{object_id} {object_type}".format(object_id=object.id,
                                                               object_type=object.__class__.__name__),

                            "{type} | {name}".format(type=object.__class__.__name__,
                                                             name=object.name))

    #todo test it
    """ get choices for get_parent"""
    def get_model_choices(self):
        objetcs = chain(Board.objects.all(),  BoardGroup.objects.all() )
        choices = []

        for object in objetcs:
            if self.instance == object:
                continue
            choices.append(self.return_model_choice(object))
        return choices

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        super(BoardAdminForm, self).__init__(*args, **kwargs)
        self.fields['get_parent'].choices = self.get_model_choices()


        if instance:
            if instance.parent:
                self.fields['get_parent'].initial = self.return_model_choice(instance.parent)

                # todo test it
                """if parent exisst do not allow lower restrictions settings than its parents"""
                for field in ["visibility", "add_new_topics_restrictions", "add_new_posts_restictions"]:
                    chosed = getattr(self.instance.parent, field)
                    new_choices = []

                    for choice in self.instance.parent.restriction_choices:
                        if choice[0] <= int(chosed):
                            new_choices.append(choice)

                    self.fields[field].choices = new_choices

                #todo test it
                """if parent exisst do not allow groups that are not picked in the parent """
                for field in ["visibility_groups", "new_topics_groups", "new_posts_groups"]:
                    self.fields[field] = forms.ModelMultipleChoiceField(queryset=getattr(instance.parent, field),
                                                                        required=False)




        else:
            #todo test it
            """change help text if object does not exists yet and disable changes to fields as admin doesen't know 
            what groups/restriction choices object will be allowed to take"""
            for field in [ 'visibility', 'add_new_topics_restrictions', 'add_new_posts_restictions',
                           "visibility_groups", "new_topics_groups", "new_posts_groups"]:
                self.fields[field].help_text = 'Aviable to set after object creation'
                self.fields[field].disabled = True


    def save(self, commit=True):
        #change instance.parent to object from get_parent field
        #todo test it
        data = self.cleaned_data['get_parent'].split(" ")
        self.instance.parent = getattr(modules[__name__], data[1]).objects.get(id= data[0])
        return super().save(commit)




