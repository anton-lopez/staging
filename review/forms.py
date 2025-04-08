from django import forms
from .models import Post, PostImage, Dorm, Room


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class DormForm(forms.ModelForm):
    class Meta:
        model = Dorm
        fields = ['name', 'description', 'image']


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['dorm', 'room_number', 'floor', 'description', 'image']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'room', 'liked']
        widgets = {
            'liked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'liked': 'I liked this room',
        }
        help_texts = {
            'liked': 'Check this box if you had a positive experience with this room.'
        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.all().order_by('dorm__name', 'room_number')
        self.fields['room'].empty_label = "Select a room"
        # Make sure the liked field appears after content
        field_order = ['title', 'content', 'room', 'liked']
        self.order_fields(field_order)


class PostImageForm(forms.ModelForm):
    image = MultipleFileField(label='Images')

    class Meta:
        model = PostImage
        fields = ['image']