/**
 * Vue-остров: фильтр проектов по категориям.
 *
 * Работает без запросов к серверу — Django отдаёт все проекты сразу
 * в data-атрибутах, Vue переключает видимость по категории.
 *
 * Требует глобальный Vue 3.
 */
(function () {
  var mountEl = document.getElementById('projects-filter-app');
  if (!mountEl || typeof Vue === 'undefined') return;

  // Данные приходят из Django-шаблона через JSON в data-атрибуте
  var categories = JSON.parse(mountEl.dataset.categories || '[]');
  var projects = JSON.parse(mountEl.dataset.projects || '[]');

  Vue.createApp({
    compilerOptions: { delimiters: ['[[', ']]'] },

    data: function () {
      return {
        categories: categories,
        projects: projects,
        activeSlug: 'all',
      };
    },

    computed: {
      visibleProjects: function () {
        if (this.activeSlug === 'all') return this.projects;
        return this.projects.filter(function (p) {
          return p.category_slug === this.activeSlug;
        }, this);
      },
    },

    methods: {
      setFilter(slug) { this.activeSlug = slug; },
      statusClass(status) {
        return {
          'active': 'project-card__badge',
          'recruiting': 'project-card__badge project-card__badge--blue',
          'archived': 'project-card__badge project-card__badge--gray',
        }[status] || 'project-card__badge';
      },
      statusLabel(status) {
        return {
          'active': 'Активен',
          'recruiting': 'Идёт набор',
          'archived': 'Архив',
        }[status] || status;
      },
    },

    template: `
      <div>
        <div class="filter-tabs">
          <button
            type="button"
            :class="{ active: activeSlug === 'all' }"
            @click="setFilter('all')"
          >Все проекты</button>
          <button
            v-for="cat in categories"
            :key="cat.slug"
            type="button"
            :class="{ active: activeSlug === cat.slug }"
            @click="setFilter(cat.slug)"
          >[[ cat.name ]]</button>
        </div>

        <div v-if="visibleProjects.length" class="projects-grid">
          <article v-for="p in visibleProjects" :key="p.id" class="project-card">
            <span :class="statusClass(p.status)">[[ statusLabel(p.status) ]]</span>
            <h3 class="project-card__title">[[ p.title ]]</h3>
            <p class="project-card__lead">[[ p.lead ]]</p>
            <div v-if="p.stats && p.stats.length" class="project-card__stats">
              <div v-for="(s, i) in p.stats" :key="i">
                <strong>[[ s.num ]]</strong>[[ s.label ]]
              </div>
            </div>
          </article>
        </div>

        <div v-else style="text-align: center; padding: 60px 0; color: var(--text-muted);">
          В этой категории пока нет проектов.
        </div>
      </div>
    `,
  }).mount('#projects-filter-app');
})();
