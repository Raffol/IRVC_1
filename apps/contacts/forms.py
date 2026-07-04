from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'contact', 'message']
        error_messages = {
            'name': {'required': 'Укажите имя.'},
            'contact': {'required': 'Укажите email или телефон.'},
            'message': {'required': 'Напишите сообщение.'},
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('Имя слишком короткое.')
        return name

    def clean_contact(self):
        contact = self.cleaned_data['contact'].strip()
        if len(contact) < 5:
            raise forms.ValidationError('Укажите корректный email или телефон.')
        return contact

    def clean_message(self):
        message = self.cleaned_data['message'].strip()
        if len(message) < 5:
            raise forms.ValidationError('Сообщение слишком короткое.')
        if len(message) > 500:
            raise forms.ValidationError('Сообщение не должно превышать 500 символов.')
        return message
