import json

from django.test import Client, TestCase
from django.urls import reverse

from .forms import ContactForm
from .models import ContactMessage


class ContactMessageTests(TestCase):
    def test_str(self):
        msg = ContactMessage.objects.create(name='Иван', contact='ivan@test.ru', message='Привет')
        self.assertIn('Иван', str(msg))


class ContactFormTests(TestCase):
    VALID_DATA = {'name': 'Анна', 'contact': 'anna@example.com', 'message': 'Здравствуйте, интересуюсь волонтёрством'}

    def test_valid_form(self):
        form = ContactForm(self.VALID_DATA)
        self.assertTrue(form.is_valid())

    def test_short_name_invalid(self):
        form = ContactForm({**self.VALID_DATA, 'name': 'A'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_short_contact_invalid(self):
        form = ContactForm({**self.VALID_DATA, 'contact': 'a@b'})
        self.assertFalse(form.is_valid())
        self.assertIn('contact', form.errors)

    def test_short_message_invalid(self):
        form = ContactForm({**self.VALID_DATA, 'message': 'hi'})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_long_message_invalid(self):
        form = ContactForm({**self.VALID_DATA, 'message': 'x' * 501})
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)

    def test_required_fields(self):
        form = ContactForm({})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('contact', form.errors)
        self.assertIn('message', form.errors)


class ContactsViewTests(TestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts.html')

    def test_post_valid_saves_and_redirects(self):
        response = self.client.post(reverse('contacts'), {
            'name': 'Анна',
            'contact': 'anna@example.com',
            'message': 'Здравствуйте, хочу помогать',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_post_invalid_does_not_save(self):
        self.client.post(reverse('contacts'), {'name': '', 'contact': '', 'message': ''})
        self.assertEqual(ContactMessage.objects.count(), 0)


class ApiContactTests(TestCase):
    def setUp(self):
        # CSRF в JSON-эндпоинтах включён по умолчанию — используем enforce_csrf_checks=False
        self.client = Client(enforce_csrf_checks=False)
        self.url = reverse('api-contact')
        self.valid_data = {
            'name': 'Мария',
            'contact': 'maria@example.com',
            'message': 'Хочу быть волонтёром на «Днях города»',
        }

    def test_get_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_valid_post_creates_message(self):
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'ok': True})
        self.assertEqual(ContactMessage.objects.count(), 1)

        msg = ContactMessage.objects.get()
        self.assertEqual(msg.name, 'Мария')
        self.assertEqual(msg.contact, 'maria@example.com')

    def test_invalid_post_returns_400_with_errors(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'name': '', 'contact': '', 'message': ''}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        errors = response.json()
        self.assertIn('name', errors)
        self.assertIn('contact', errors)
        self.assertIn('message', errors)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_malformed_json_returns_400(self):
        response = self.client.post(
            self.url,
            data='not-a-json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.json())

    def test_short_message_returns_error_under_message_key(self):
        response = self.client.post(
            self.url,
            data=json.dumps({**self.valid_data, 'message': 'hi'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('message', response.json())
