import json

from django.test import TestCase
from django.urls import reverse

from .models import Project, ProjectCategory


class ProjectCategoryTests(TestCase):
    def test_str(self):
        cat = ProjectCategory.objects.create(name='Тестовая', slug='test-cat', order=99)
        self.assertEqual(str(cat), 'Тестовая')


class ProjectTests(TestCase):
    def setUp(self):
        self.cat = ProjectCategory.objects.create(name='Тестовая', slug='test-cat', order=99)

    def test_str(self):
        p = Project.objects.create(title='Помощь в больницах', category=self.cat, lead='Описание')
        self.assertEqual(str(p), 'Помощь в больницах')

    def test_get_stats_filters_empty(self):
        p = Project.objects.create(
            title='Проект', category=self.cat, lead='',
            stat_1_num='48', stat_1_label='волонтёров',
            stat_2_num='', stat_2_label='',                     # пустой — не покажется
            stat_3_num='2 раза', stat_3_label='в неделю',
        )
        stats = p.get_stats()
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0], {'num': '48', 'label': 'волонтёров'})
        self.assertEqual(stats[1], {'num': '2 раза', 'label': 'в неделю'})


class ProjectsViewTests(TestCase):
    def setUp(self):
        # Убираем seed-категории — так проще проверить фикстуру целиком
        ProjectCategory.objects.all().delete()

        self.eco = ProjectCategory.objects.create(name='Экологические', slug='eco', order=1)
        self.social = ProjectCategory.objects.create(name='Социальные', slug='social', order=2)
        Project.objects.create(title='Субботник', category=self.eco, lead='Уборка')
        Project.objects.create(title='Приют', category=self.social, lead='Помощь животным')
        Project.objects.create(title='Скрытый', category=self.eco, lead='', is_active=False)

    def test_view_returns_200(self):
        response = self.client.get(reverse('projects'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('projects'))
        self.assertTemplateUsed(response, 'projects.html')

    def test_projects_json_has_active_only(self):
        response = self.client.get(reverse('projects'))
        projects = json.loads(response.context['projects_json'])
        titles = [p['title'] for p in projects]
        self.assertIn('Субботник', titles)
        self.assertIn('Приют', titles)
        self.assertNotIn('Скрытый', titles)

    def test_categories_json(self):
        response = self.client.get(reverse('projects'))
        cats = json.loads(response.context['project_categories_json'])
        slugs = [c['slug'] for c in cats]
        self.assertEqual(slugs, ['eco', 'social'])

    def test_json_has_category_slug_per_project(self):
        response = self.client.get(reverse('projects'))
        projects = json.loads(response.context['projects_json'])
        for p in projects:
            self.assertIn(p['category_slug'], ['eco', 'social'])


class SeedDataTests(TestCase):
    def test_default_categories_seeded(self):
        slugs = set(ProjectCategory.objects.values_list('slug', flat=True))
        expected = {'social', 'eco', 'edu', 'events'}
        self.assertTrue(expected.issubset(slugs))
