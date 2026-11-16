from django import forms

from .models import Order, Profile


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


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'url',
            'text',
            'customer_url',
            'prospects_score',
            'estimated_time',
            'estimated_cost',
            'response_text',
        ]
        labels = {
            'url': 'URL заказа',
            'text': 'Текст заказа',
            'customer_url': 'URL профиля заказчика (необязательно)',
            'prospects_score': 'Оценка перспектив выполнить заказ (0–100)',
            'estimated_time': 'Оценка времени выполнения',
            'estimated_cost': 'Оценка стоимости',
            'response_text': 'Текст отклика',
        }
        widgets = {
            'url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://example.com/orders/123',
                }
            ),
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 8,
                    'placeholder': 'Опишите заказ...',
                }
            ),
            'customer_url': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://example.com/users/customer',
                }
            ),
            'prospects_score': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'min': 0,
                    'max': 100,
                    'placeholder': 'Например, 75',
                }
            ),
            'estimated_time': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Например, 5 рабочих дней',
                }
            ),
            'estimated_cost': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Например, 30 000 руб.',
                }
            ),
            'response_text': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 10,
                    'placeholder': 'Введите отклик вручную или сгенерируйте его с помощью LLM.',
                }
            ),
        }
