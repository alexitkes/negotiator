"""Взаимодействие с OpenAI-совместимым LLM API."""

import json

from django.conf import settings
from openai import OpenAI


class LLMError(Exception):
    """Ошибка при обращении к LLM."""


SYSTEM_PROMPT = (
    'Ты — опытный помощник фрилансера на бирже заказов. '
    'По описанию навыков фрилансера и тексту заказа ты оцениваешь, насколько он подходит '
    'для выполнения заказа, оцениваешь срок и стоимость работ, а также пишешь отклик, '
    'который имеет шанс заинтересовать заказчика. Отвечай только на русском языке.'
)


def build_user_prompt(order_text, skills, customer_url=''):
    parts = [
        'Описание навыков и опыта фрилансера:',
        skills or '(не заполнено)',
        '',
        'Текст заказа:',
        order_text,
    ]
    if customer_url:
        parts.extend(['', f'Профиль заказчика: {customer_url}'])
    parts.extend(
        [
            '',
            'Верни ответ строго в виде JSON-объекта без пояснений и markdown:',
            '{',
            '  "prospects_score": <целое число от 0 до 100 — насколько фрилансер способен выполнить заказ>,',
            '  "estimated_time": "<оценка времени выполнения заказа, например: 5 рабочих дней>",',
            '  "estimated_cost": "<оценка стоимости выполнения заказа, например: 30 000 руб.>",',
            '  "response_text": "<готовый текст отклика на заказ, который заинтересует заказчика>"',
            '}',
        ]
    )
    return '\n'.join(parts)


def generate_order_response(order_text, skills, customer_url=''):
    """Запрашивает у LLM оценки и текст отклика по заказу.

    Возвращает словарь с результатами генерации, названием модели и расходом токенов.
    """
    if not settings.OPENAI_API_KEY:
        raise LLMError('Не задан токен доступа к LLM. Укажите OPENAI_API_KEY в файле .env.')
    if not settings.OPENAI_MODEL:
        raise LLMError('Не задано название модели. Укажите OPENAI_MODEL в файле .env.')

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL or None,
        timeout=settings.OPENAI_TIMEOUT,
    )

    try:
        completion = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': build_user_prompt(order_text, skills, customer_url)},
            ],
            response_format={'type': 'json_object'},
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )
    except Exception as exc:  # noqa: BLE001 — сеть/API могут вернуть любую ошибку
        raise LLMError(f'Не удалось получить ответ от LLM: {exc}') from exc

    content = (completion.choices[0].message.content or '').strip()
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise LLMError('LLM вернула ответ в неожиданном формате (не JSON).') from exc

    if not isinstance(data, dict):
        raise LLMError('LLM вернула ответ в неожиданном формате.')

    score = data.get('prospects_score')
    try:
        score = int(score) if score is not None and score != '' else None
    except (TypeError, ValueError):
        score = None
    if score is not None:
        score = max(0, min(100, score))

    response_text = str(data.get('response_text') or '').strip()
    if not response_text:
        raise LLMError('LLM не вернула текст отклика. Попробуйте ещё раз.')

    usage = getattr(completion, 'usage', None)
    prompt_tokens = getattr(usage, 'prompt_tokens', 0) or 0
    completion_tokens = getattr(usage, 'completion_tokens', 0) or 0
    total_tokens = getattr(usage, 'total_tokens', None)
    if total_tokens is None:
        total_tokens = prompt_tokens + completion_tokens

    return {
        'prospects_score': score,
        'estimated_time': str(data.get('estimated_time') or '').strip()[:255],
        'estimated_cost': str(data.get('estimated_cost') or '').strip()[:255],
        'response_text': response_text,
        'model_name': getattr(completion, 'model', '') or settings.OPENAI_MODEL,
        'prompt_tokens': prompt_tokens,
        'completion_tokens': completion_tokens,
        'total_tokens': total_tokens,
    }
