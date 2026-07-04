from django.test import TestCase
from django.urls import reverse

from .models import TeamGroup, TeamMember


class TeamGroupTests(TestCase):
    def test_str(self):
        group = TeamGroup.objects.create(name='Руководство', order=1)
        self.assertEqual(str(group), 'Руководство')

    def test_ordering(self):
        TeamGroup.objects.all().delete()   # убираем seed-группы
        TeamGroup.objects.create(name='Third', order=30)
        TeamGroup.objects.create(name='First', order=10)
        TeamGroup.objects.create(name='Second', order=20)
        names = list(TeamGroup.objects.values_list('name', flat=True))
        self.assertEqual(names, ['First', 'Second', 'Third'])


class TeamMemberTests(TestCase):
    def setUp(self):
        self.group = TeamGroup.objects.create(name='Руководство', order=1)

    def test_str(self):
        member = TeamMember.objects.create(
            group=self.group, name='Анна Соколова', position='Директор',
        )
        self.assertEqual(str(member), 'Анна Соколова — Директор')

    def test_ordering_within_group(self):
        TeamMember.objects.create(group=self.group, name='B', position='p', order=2)
        TeamMember.objects.create(group=self.group, name='A', position='p', order=1)
        names = list(TeamMember.objects.values_list('name', flat=True))
        self.assertEqual(names, ['A', 'B'])


class TeamViewTests(TestCase):
    def setUp(self):
        self.leadership = TeamGroup.objects.create(name='Руководство', order=1)
        self.coordination = TeamGroup.objects.create(name='Координация', order=2)
        TeamMember.objects.create(group=self.leadership, name='Анна', position='Директор')
        TeamMember.objects.create(group=self.leadership, name='Дмитрий', position='Зам', is_active=False)
        TeamMember.objects.create(group=self.coordination, name='Мария', position='Координатор')

    def test_view_returns_200(self):
        response = self.client.get(reverse('team'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('team'))
        self.assertTemplateUsed(response, 'team.html')

    def test_shows_active_members(self):
        response = self.client.get(reverse('team'))
        self.assertContains(response, 'Анна')
        self.assertContains(response, 'Мария')

    def test_hides_inactive_members(self):
        response = self.client.get(reverse('team'))
        self.assertNotContains(response, 'Дмитрий')


class SeedDataTests(TestCase):
    def test_default_groups_seeded(self):
        names = set(TeamGroup.objects.values_list('name', flat=True))
        expected = {'Руководство', 'Координация проектов', 'Обучение и развитие', 'Актив волонтёров'}
        self.assertTrue(expected.issubset(names))
