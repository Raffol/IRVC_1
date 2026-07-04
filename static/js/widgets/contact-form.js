/**
 * Vue-остров: форма обратной связи.
 *
 * Монтируется в <div id="contact-form-app">,
 * из data-атрибутов забирает endpoint (URL API) и CSRF-токен Django.
 *
 * Требует глобальный Vue 3 (подключается в base.html).
 */
(function () {
  var mountEl = document.getElementById('contact-form-app');
  if (!mountEl || typeof Vue === 'undefined') return;

  var endpoint = mountEl.dataset.endpoint || '/api/contact/';
  var csrfToken = mountEl.dataset.csrf || '';

  var MAX_MESSAGE = 500;

  Vue.createApp({
    // Используем [[ ]] вместо {{ }}, чтобы не конфликтовать с Django-шаблонами
    compilerOptions: { delimiters: ['[[', ']]'] },

    data: function () {
      return {
        name: '',
        contact: '',
        message: '',
        sending: false,
        done: false,
        errors: {},
        generalError: '',
      };
    },

    computed: {
      remaining: function () { return MAX_MESSAGE - this.message.length; },
      canSubmit: function () {
        return this.name.trim() && this.contact.trim() && this.message.trim() && !this.sending;
      },
    },

    methods: {
      async submit() {
        if (!this.canSubmit) return;
        this.sending = true;
        this.errors = {};
        this.generalError = '';

        try {
          var res = await fetch(endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken,
              'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify({
              name: this.name,
              contact: this.contact,
              message: this.message,
            }),
          });

          if (res.ok) {
            this.done = true;
          } else if (res.status === 400) {
            // Django-форма вернула ошибки валидации по полям
            this.errors = await res.json();
          } else {
            this.generalError = 'Не удалось отправить сообщение. Попробуйте позже.';
          }
        } catch (e) {
          this.generalError = 'Ошибка сети. Проверьте подключение и попробуйте ещё раз.';
        } finally {
          this.sending = false;
        }
      },

      reset() {
        this.name = '';
        this.contact = '';
        this.message = '';
        this.done = false;
        this.errors = {};
        this.generalError = '';
      },
    },

    template: `
      <div class="contact-form">
        <template v-if="done">
          <div class="notice notice--success">
            <div>
              <strong>Спасибо!</strong> Сообщение получено, свяжемся с вами
              в течение пары рабочих дней.
            </div>
          </div>
          <button type="button" class="btn btn--ghost btn--wide" @click="reset">Написать ещё</button>
        </template>

        <template v-else>
          <h3>Написать нам</h3>
          <p>Опишите, чем можем помочь. Ответим в течение пары рабочих дней.</p>

          <div v-if="generalError" class="notice notice--error">[[ generalError ]]</div>

          <div class="field">
            <label>Как к вам обращаться</label>
            <input
              type="text"
              v-model="name"
              placeholder="Имя"
              :class="{ 'has-error': errors.name }"
              @input="errors.name = null"
            >
            <div v-if="errors.name" class="field-error">[[ errors.name[0] ]]</div>
          </div>

          <div class="field">
            <label>Email или телефон</label>
            <input
              type="text"
              v-model="contact"
              placeholder="Куда написать в ответ"
              :class="{ 'has-error': errors.contact }"
              @input="errors.contact = null"
            >
            <div v-if="errors.contact" class="field-error">[[ errors.contact[0] ]]</div>
          </div>

          <div class="field">
            <label>
              Сообщение
              <span class="field__hint">[[ message.length ]] / ${MAX_MESSAGE}</span>
            </label>
            <textarea
              v-model="message"
              :maxlength="${MAX_MESSAGE}"
              placeholder="Расскажите свою историю или задайте вопрос"
              :class="{ 'has-error': errors.message }"
              @input="errors.message = null"
            ></textarea>
            <div v-if="errors.message" class="field-error">[[ errors.message[0] ]]</div>
          </div>

          <button
            type="button"
            class="btn btn--primary btn--lg btn--wide"
            :disabled="!canSubmit"
            @click="submit"
          >
            [[ sending ? 'Отправляем…' : 'Отправить' ]]
          </button>
        </template>
      </div>
    `,
  }).mount('#contact-form-app');
})();
