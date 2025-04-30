from django import forms
from .models import Post, PostImage, Dorm, Room, RoomImage


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
    labels = forms.CharField(
        label="Labels",
        help_text="Enter up to 3 labels separated by commas (e.g., 'Quiet, Spacious, Modern')",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., Quiet, Spacious, Modern'})
    )
    class Meta:
        model = Dorm
        fields = ['name', 'description', 'image', 'labels']
    
    def clean_labels(self):
        labels = self.cleaned_data.get('labels', '')
        label_list = [label.strip() for label in labels.split(',') if label.strip()]
        if len(label_list) > 3:
            raise forms.ValidationError("You can only add up to 3 labels.")
        return ','.join(label_list)


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['dorm', 'room_number', 'floor', 'description', 'image']
        labels = {
            'image': 'Cover Image'
        }
        help_texts = {
            'image': 'This image will be displayed as the main room image in listings.'
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'room', 'liked']
        widgets = {
            'liked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'liked': 'I liked this room',
            'room': 'Room (set from your profile)',
        }
        help_texts = {
            'liked': 'Check this box if you had a positive experience with this room.',
            'room': 'This is automatically set from your profile. To change it, update your profile.',
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


class RoomImageForm(forms.ModelForm):
    additional_images = MultipleFileField(label='Additional Images', required=False)

    class Meta:
        model = RoomImage
        fields = []  # We don't use any model fields directly

    def __init__(self, *args, **kwargs):
        super(RoomImageForm, self).__init__(*args, **kwargs)
        self.fields[
            'additional_images'].help_text = 'Optional: Select multiple images for the room gallery (Ctrl+click or Cmd+click to select multiple)'