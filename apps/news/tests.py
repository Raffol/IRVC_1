from datetime import datetime, timezone
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.core.models import SiteSettings

from .models import VkPost
from .tasks import sync_vk_feed_task
from .vk_sync import _extract_title, _first_photo_url, sync_vk_feed


class VkPostTests(TestCase):
    def test_str_uses_title(self):
        post = VkPost.objects.create(
            vk_id='1', title='Заголовок', text='Полный текст',
            url='https://vk.com/wall-1_1',
            published_at=datetime.now(timezone.utc),
        )
        self.assertEqual(str(post), 'Заголовок')

    def test_str_falls_back_to_text(self):
        post = VkPost.objects.create(
            vk_id='2', title='', text='Просто текст поста',
            url='https://vk.com/wall-1_2',
            published_at=datetime.now(timezone.utc),
        )
        self.assertIn('Просто текст', str(post))

    def test_ordering_newest_first(self):
        VkPost.objects.create(vk_id='1', text='old', url='x', published_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
        VkPost.objects.create(vk_id='2', text='new', url='x', published_at=datetime(2026, 6, 1, tzinfo=timezone.utc))
        texts = list(VkPost.objects.values_list('text', flat=True))
        self.assertEqual(texts, ['new', 'old'])


class NewsViewTests(TestCase):
    def test_returns_200(self):
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse('news'))
        self.assertTemplateUsed(response, 'news.html')

    def test_only_visible_posts_shown(self):
        VkPost.objects.create(vk_id='1', text='visible', url='x',
                              published_at=datetime.now(timezone.utc), is_visible=True)
        VkPost.objects.create(vk_id='2', text='hidden', url='x',
                              published_at=datetime.now(timezone.utc), is_visible=False)
        response = self.client.get(reverse('news'))
        self.assertContains(response, 'visible')
        self.assertNotContains(response, 'hidden')

    def test_pagination_kicks_in(self):
        for i in range(15):
            VkPost.objects.create(
                vk_id=str(i), text=f'post {i}', url='x',
                published_at=datetime(2026, 1, i + 1, tzinfo=timezone.utc),
            )
        response = self.client.get(reverse('news'))
        # paginate_by=9, значит должна быть пагинация
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['posts']), 9)


class VkSyncHelpersTests(TestCase):
    def test_extract_title_first_line(self):
        self.assertEqual(_extract_title('Первая строка\nВторая строка'), 'Первая строка')

    def test_extract_title_empty(self):
        self.assertEqual(_extract_title(''), '')

    def test_extract_title_truncates_to_200(self):
        long = 'x' * 300
        self.assertEqual(len(_extract_title(long)), 200)

    def test_first_photo_url_picks_largest(self):
        item = {
            'attachments': [
                {'type': 'audio'},
                {'type': 'photo', 'photo': {'sizes': [
                    {'url': 'https://x/s.jpg', 'width': 100, 'height': 100},
                    {'url': 'https://x/l.jpg', 'width': 1000, 'height': 800},
                    {'url': 'https://x/m.jpg', 'width': 500, 'height': 400},
                ]}},
            ]
        }
        self.assertEqual(_first_photo_url(item), 'https://x/l.jpg')

    def test_first_photo_url_none_if_no_photos(self):
        self.assertEqual(_first_photo_url({'attachments': []}), '')


@override_settings(VK_SERVICE_TOKEN='test-token')
class SyncVkFeedTests(TestCase):
    def _make_fetcher(self, response_data):
        """Мок для requests.get — возвращает response с .json()"""
        mock_response = Mock()
        mock_response.json.return_value = response_data
        return Mock(return_value=mock_response)

    def test_skipped_when_no_group_id(self):
        SiteSettings.get_solo()  # vk_group_id пустой по умолчанию
        result = sync_vk_feed(fetcher=self._make_fetcher({}))
        self.assertIn('vk_group_id', result['skipped_reason'])

    @override_settings(VK_SERVICE_TOKEN='')
    def test_skipped_when_no_token(self):
        s = SiteSettings.get_solo()
        s.vk_group_id = '12345'
        s.save()
        result = sync_vk_feed(fetcher=self._make_fetcher({}))
        self.assertIn('VK_SERVICE_TOKEN', result['skipped_reason'])

    def test_creates_new_posts(self):
        s = SiteSettings.get_solo()
        s.vk_group_id = '12345'
        s.save()

        fetcher = self._make_fetcher({
            'response': {
                'items': [
                    {
                        'id': 100,
                        'text': 'Заголовок поста\nВторой абзац',
                        'date': 1720000000,
                        'likes': {'count': 42},
                        'comments': {'count': 5},
                        'attachments': [],
                    },
                    {
                        'id': 101,
                        'text': 'Другой пост',
                        'date': 1720100000,
                        'likes': {'count': 10},
                        'comments': {'count': 2},
                        'attachments': [],
                    },
                ]
            }
        })
        result = sync_vk_feed(fetcher=fetcher)

        self.assertEqual(result['created'], 2)
        self.assertEqual(result['updated'], 0)
        self.assertEqual(VkPost.objects.count(), 2)
        post = VkPost.objects.get(vk_id='100')
        self.assertEqual(post.title, 'Заголовок поста')
        self.assertEqual(post.likes, 42)
        self.assertIn('wall-12345_100', post.url)

    def test_updates_existing_posts(self):
        s = SiteSettings.get_solo()
        s.vk_group_id = '12345'
        s.save()
        VkPost.objects.create(
            vk_id='100', title='old', text='old', url='x',
            published_at=datetime.fromtimestamp(1720000000, tz=timezone.utc),
            likes=1, comments=0,
        )

        fetcher = self._make_fetcher({
            'response': {
                'items': [
                    {
                        'id': 100, 'text': 'new title\nбольше лайков',
                        'date': 1720000000,
                        'likes': {'count': 99}, 'comments': {'count': 20},
                        'attachments': [],
                    }
                ]
            }
        })
        result = sync_vk_feed(fetcher=fetcher)

        self.assertEqual(result['created'], 0)
        self.assertEqual(result['updated'], 1)
        post = VkPost.objects.get(vk_id='100')
        self.assertEqual(post.likes, 99)
        self.assertEqual(post.title, 'new title')

    def test_handles_vk_api_error(self):
        s = SiteSettings.get_solo()
        s.vk_group_id = '12345'
        s.save()
        fetcher = self._make_fetcher({'error': {'error_code': 5, 'error_msg': 'Auth failed'}})
        result = sync_vk_feed(fetcher=fetcher)
        self.assertIn('Auth failed', result['skipped_reason'])


class CeleryTaskTests(TestCase):
    """Celery-задача — тонкая обёртка над sync_vk_feed(). Тестируем, что она правильно её зовёт."""

    @patch('apps.news.tasks._sync_vk_feed')
    def test_task_calls_sync_with_default_count(self, mock_sync):
        mock_sync.return_value = {'created': 3, 'updated': 1, 'skipped_reason': None}
        result = sync_vk_feed_task(count=20)
        mock_sync.assert_called_once_with(count=20)
        self.assertEqual(result['created'], 3)

    @patch('apps.news.tasks._sync_vk_feed')
    def test_task_passes_count_argument(self, mock_sync):
        mock_sync.return_value = {'created': 0, 'updated': 0, 'skipped_reason': None}
        sync_vk_feed_task(count=50)
        mock_sync.assert_called_once_with(count=50)


class SetupPeriodicTasksCommandTests(TestCase):
    """Проверяем, что команда setup_periodic_tasks создаёт запись в БД."""

    def test_command_creates_periodic_task(self):
        from django.core.management import call_command
        from django_celery_beat.models import PeriodicTask

        call_command('setup_periodic_tasks', interval=15)

        task = PeriodicTask.objects.get(name='Sync VK feed')
        self.assertEqual(task.task, 'news.sync_vk_feed')
        self.assertTrue(task.enabled)
        self.assertEqual(task.interval.every, 15)

    def test_command_updates_existing_task(self):
        from django.core.management import call_command
        from django_celery_beat.models import PeriodicTask

        call_command('setup_periodic_tasks', interval=15)
        call_command('setup_periodic_tasks', interval=30)

        # Одна и та же задача — просто обновилось расписание
        self.assertEqual(PeriodicTask.objects.filter(name='Sync VK feed').count(), 1)
        task = PeriodicTask.objects.get(name='Sync VK feed')
        self.assertEqual(task.interval.every, 30)
