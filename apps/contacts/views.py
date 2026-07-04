import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import View

from .forms import ContactForm


class ContactsView(View):
    """
    Страница /contacts/.
    GET — рендерит страницу.
    POST — noscript-fallback: если Vue не загрузился, форма отправляется классически.
    """

    template_name = 'contacts.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Сообщение отправлено, свяжемся в течение пары дней.')
        else:
            messages.error(request, 'Проверьте поля формы.')
        return redirect('contacts')


@require_POST
def api_contact(request):
    """
    JSON API для Vue-острова.
    Ожидает JSON в теле запроса: {"name": "...", "contact": "...", "message": "..."}
    Возвращает 200 при успехе, 400 с ошибками валидации при неудаче.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'detail': 'Неправильный формат JSON.'}, status=400)

    form = ContactForm(data)
    if form.is_valid():
        form.save()
        return JsonResponse({'ok': True})

    # form.errors: {'field': ['error msg 1', 'error msg 2']}
    return JsonResponse(form.errors, status=400)
