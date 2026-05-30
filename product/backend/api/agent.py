from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from features.almanac.engine import build_today_almanac
from product.backend.llm.deepseek import DeepSeekClient, load_env_file

from .database import list_reviews

TOPIC_SUGGESTIONS = {
    'phone': ['帮我解读最近一条手机号评测', '现在换号更看重什么', '我想先看盘面重点'],
    'almanac': ['今天更适合推进什么', '今天哪些动作最好先别做', '帮我把黄历建议变成行动清单'],
    'product': ['下一步先做哪个页面', '手机号结果页还能怎么优化', '首页入口怎么排更清楚'],
    'account': ['我的积分现在怎么用', '评测记录后面怎么做成列表页', '登录后还需要补什么状态'],
    'general': ['帮我继续梳理当前产品', '给我一个今天适合问的问题', '我下一步先做什么'],
}


def build_agent_reply(*, message: str, history: list[dict[str, str]] | None = None, user_id: str | None = None) -> dict[str, Any]:
    normalized_message = (message or '').strip()
    normalized_history = history or []
    today_almanac = build_today_almanac().to_dict()
    recent_reviews = list_reviews(limit=3, user_id=user_id) if user_id else list_reviews(limit=3)
    topic = _detect_topic(normalized_message)
    previous_user_message = _find_previous_user_message(normalized_history)
    review_summary = _build_review_summary(recent_reviews)

    reply, meta = _build_reply(
        topic=topic,
        message=normalized_message,
        history=normalized_history,
        previous_user_message=previous_user_message,
        almanac=today_almanac,
        review_summary=review_summary,
    )

    context_tags = [
        f"今日宜：{today_almanac['yi_summary']}",
        f"今日忌：{today_almanac['ji_summary']}",
        f"最近评测：{review_summary}",
    ]
    source_tag = f"模型：{meta['model_name']}" if meta['used_llm'] else '规则兜底'

    return {
        'reply': reply,
        'suggestions': TOPIC_SUGGESTIONS[topic],
        'context_tags': [source_tag, *context_tags][:4],
        'generated_at': _utc_now(),
        'meta': meta,
    }


def _build_reply(*, topic: str, message: str, history: list[dict[str, str]], previous_user_message: str, almanac: dict[str, Any], review_summary: str) -> tuple[str, dict[str, Any]]:
    client = _resolve_agent_client()
    if client is not None:
        try:
            response = client.chat_text(
                system_prompt=_build_agent_system_prompt(),
                messages=_build_history_messages(history),
                user_prompt=_build_agent_user_prompt(
                    topic=topic,
                    message=message,
                    previous_user_message=previous_user_message,
                    almanac=almanac,
                    review_summary=review_summary,
                ),
                thinking_enabled=False,
                temperature=0.6,
                max_tokens=520,
            )
            reply = (response.content or '').strip()
            if reply:
                return reply, {
                    'reply_mode': 'llm',
                    'used_llm': True,
                    'model_name': response.model or client.config.model,
                }
        except Exception:
            pass

    return _build_topic_reply(
        topic=topic,
        message=message,
        previous_user_message=previous_user_message,
        almanac=almanac,
        review_summary=review_summary,
    ), {
        'reply_mode': 'fallback',
        'used_llm': False,
        'model_name': 'fallback-only',
    }


def _resolve_agent_client() -> DeepSeekClient | None:
    load_env_file()
    try:
        return DeepSeekClient.from_env()
    except Exception:
        return None


def _build_history_messages(history: list[dict[str, str]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for item in history[-6:]:
        role = 'assistant' if item.get('role') == 'assistant' else 'user'
        text = str(item.get('text') or '').strip()
        if not text:
            continue
        items.append({'role': role, 'content': text[:800]})
    return items


def _build_agent_system_prompt() -> str:
    return (
        '你是易如反掌 H5 产品中的智能体助手。'
        '你的职责是帮助用户解读手机号评测、今日黄历和当前产品流程。'
        '回答要适合手机阅读：直接、克制、中文自然，不要使用 markdown 表格，不要堆砌术语。'
        '优先先给结论，再给 2 到 4 条可执行建议。'
        '如果用户问到当前尚未正式开放的功能，要明确说明目前 H5 先完成手机号评测主链路。'
    )


def _build_agent_user_prompt(*, topic: str, message: str, previous_user_message: str, almanac: dict[str, Any], review_summary: str) -> str:
    previous = previous_user_message or '无'
    return (
        f'当前主题：{topic}\n'
        f'用户当前问题：{message}\n'
        f'上一句用户问题：{previous}\n'
        f'今日宜：{almanac["yi_summary"]}\n'
        f'今日忌：{almanac["ji_summary"]}\n'
        f'最近评测摘要：{review_summary}\n\n'
        '请基于这些信息直接回复用户。要求：\n'
        '1. 先给一个清楚判断；\n'
        '2. 再给 2 到 4 条短建议；\n'
        '3. 内容控制在 4 段以内；\n'
        '4. 不要说自己看不到系统，直接像产品内智能体一样回答。'
    )


def _detect_topic(message: str) -> str:
    if any(keyword in message for keyword in ['手机号', '号码', '评测', '测评', '盘面']):
        return 'phone'
    if any(keyword in message for keyword in ['黄历', '今天', '今日', '宜', '忌']):
        return 'almanac'
    if any(keyword in message for keyword in ['首页', '页面', '产品', '流程', 'H5', '原型']):
        return 'product'
    if any(keyword in message for keyword in ['积分', '登录', '我的', '充值', '记录']):
        return 'account'
    return 'general'


def _find_previous_user_message(history: list[dict[str, str]]) -> str:
    for item in reversed(history):
        if item.get('role') == 'user' and item.get('text'):
            return item['text'].strip()
    return ''


def _build_review_summary(reviews: list[dict[str, Any]]) -> str:
    if not reviews:
        return '暂无评测记录'

    summaries = []
    for item in reviews[:3]:
        phone = _mask_phone(str(item['phone']))
        gender_label = '男' if str(item['gender']) == 'male' else '女'
        summaries.append(f"{phone}（{gender_label}，{item['status']}）")
    return '、'.join(summaries)


def _build_topic_reply(*, topic: str, message: str, previous_user_message: str, almanac: dict[str, Any], review_summary: str) -> str:
    prefix = f"你刚刚问的是“{message}”。"
    if previous_user_message and previous_user_message != message:
        prefix = f"结合你上一句“{previous_user_message}”和这句“{message}”，"

    if topic == 'phone':
        return (
            f"{prefix} 当前更适合先看手机号评测里的主轴、主要矛盾和十方面结论，不要一上来就堆很多解释。"
            f" 今天黄历提示“宜：{almanac['yi_summary']}；忌：{almanac['ji_summary']}”，所以这类问题更适合先收敛焦点、先看主结论再做追问。"
            f" 目前系统里最近的评测记录是：{review_summary}。如果你愿意，下一步可以直接围绕最近一条评测继续展开。"
        )

    if topic == 'almanac':
        return (
            f"{prefix} 今天更适合把动作压缩到一条主线。黄历里“宜”是“{almanac['yi_summary']}”，“忌”是“{almanac['ji_summary']}”。"
            f" 放到产品推进上，就是优先做一个清楚、可验证的小闭环，先别同时开太多入口。"
        )

    if topic == 'product':
        return (
            f"{prefix} 当前 H5 阶段更适合优先收敛在手机号评测主链路，首页黄历和“我的”页作为配套能力承接。"
            f" 下一步更值得优先做的是把手机号评测接口、积分规则和历史记录彻底打通，再决定智能体页的增强节奏。"
        )

    if topic == 'account':
        return (
            f"{prefix} “我的”页更适合先把登录态、历史记录和积分消费规则做清楚。"
            f" 先把“什么时候扣积分、哪些记录归当前用户、哪些接口需要登录”定清楚，产品体验会稳定很多。"
        )

    return (
        f"{prefix} 如果你现在没有特别明确的追问，建议先围绕一个主题继续展开，比如手机号评测、今日黄历，或者 H5 产品下一步。"
        f" 今天黄历的节奏偏向“宜：{almanac['yi_summary']}；忌：{almanac['ji_summary']}”，因此更适合先收敛，再继续深入。"
    )


def _mask_phone(phone: str) -> str:
    if len(phone) < 7:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
