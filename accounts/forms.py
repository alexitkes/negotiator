from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['about']
        labels = {'about': 'О себе'}
        widgets = {
            'about': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 6,
                    'maxlength': Profile.MAX_ABOUT_LENGTH,
                    'placeholder': 'Расскажите о себе...',
                }
            ),
        }

    def clean_about(self):
        about = self.cleaned_data.get('about', '')
        if len(about) > Profile.MAX_ABOUT_LENGTH:
            raise forms.ValidationError(
                f'Текст о себе не может превышать {Profile.MAX_ABOUT_LENGTH} символов.'
            )
        return about
