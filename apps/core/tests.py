"""
Тесты приложения core.

Запуск: python manage.py test apps.core
"""
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .context_processors import site_context
from .models import HeroStat, NavigationItem, SiteSettings


class SiteSettingsTests(TestCase):
    def test_singleton_returns_same_instance(self):
        s1 = SiteSettings.get_solo()
        s2 = SiteSettings.get_solo()
        self.assertEqual(s1.pk, s2.pk)

    def test_str(self):
        self.assertEqual(str(SiteSettings.get_solo()), 'Настройки сайта')

    def test_default_values(self):
        s = SiteSettings.get_solo()
        self.assertEqual(s.hero_title, 'Помогаем людям, делаем город')
        self.assertEqual(s.hero_title_accent, 'лучше')
        self.assertEqual(s.cta_button_text, 'Заполнить анкету')

    def test_phone_clean_strips_non_digits(self):
        s = SiteSettings.get_solo()
        s.phone = '+7 (000) 123-45-67'
        self.assertEqual(s.phone_clean, '70001234567')

    def test_phone_clean_empty(self):
        s = SiteSettings.get_solo()
        s.phone = ''
        self.assertEqual(s.phone_clean, '')


class NavigationItemTests(TestCase):
    def test_str(self):
        item = NavigationItem.objects.create(label='Тестовый', slug='test-nav', url='/', order=1)
        self.assertEqual(str(item), 'Тестовый')

    def test_ordering_by_order_field(self):
        # Работаем на пустой таблице, чтобы seed-данные не мешали
        NavigationItem.objects.all().delete()
        NavigationItem.objects.create(label='Third', slug='c', url='/', order=30)
        NavigationItem.objects.create(label='First', slug='a', url='/', order=10)
        NavigationItem.objects.create(label='Second', slug='b', url='/', order=20)
        labels = list(NavigationItem.objects.values_list('label', flat=True))
        self.assertEqual(labels, ['First', 'Second', 'Third'])


class HeroStatTests(TestCase):
    def test_str(self):
        stat = HeroStat.objects.create(number='1 200+', label='волонтёров', order=1)
        self.assertEqual(str(stat), '1 200+ — волонтёров')


class SiteContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # Seed уже создал 5 активных пунктов. Добавляем один отключённый — он не должен появиться.
        NavigationItem.objects.create(
            label='Отключён', slug='ctx-hidden', url='/x/', order=99, is_active=False,
        )

    def test_returns_settings(self):
        request = self.factory.get('/')
        ctx = site_context(request)
        self.assertIn('settings', ctx)
        self.assertIsInstance(ctx['settings'], SiteSettings)

    def test_nav_items_only_active(self):
        request = self.factory.get('/')
        ctx = site_context(request)
        slugs = [item.slug for item in ctx['nav_items']]
        self.assertIn('home', slugs)                # seed
        self.assertNotIn('ctx-hidden', slugs)       # is_active=False → скрыт


class HomeViewTests(TestCase):
    def test_home_returns_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')

    def test_home_context_has_stats_and_previews(self):
        response = self.client.get(reverse('home'))
        self.assertIn('hero_stats', response.context)
        self.assertIn('news_preview', response.context)
        self.assertIn('team_preview', response.context)

    def test_home_shows_default_hero_title(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Помогаем людям')


class SeedDataTests(TestCase):
    """Проверяем, что seed-миграция 0002 создала начальные данные."""

    def test_navigation_items_seeded(self):
        slugs = set(NavigationItem.objects.values_list('slug', flat=True))
        expected = {'home', 'team', 'news', 'projects', 'contacts'}
        self.assertTrue(expected.issubset(slugs))

    def test_navigation_has_correct_order(self):
        items = list(NavigationItem.objects.order_by('order').values_list('slug', flat=True))
        # После главной идёт команда
        self.assertEqual(items[0], 'home')
        self.assertEqual(items[-1], 'contacts')

    def test_hero_stats_seeded(self):
        self.assertGreaterEqual(HeroStat.objects.count(), 4)

    def test_site_settings_created(self):
        # get_solo не должен создавать запись повторно — она уже есть после seed
        settings = SiteSettings.get_solo()
        self.assertEqual(settings.pk, 1)
