from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from product.backend.board_description import render_board_description_from_package
from product.backend.career import render_career_from_package
from product.backend.fortune import render_fortune_from_package
from product.backend.health import render_health_from_package
from product.backend.learning import render_learning_from_package
from product.backend.llm import DeepSeekClient, load_env_file
from product.backend.marriage import render_marriage_from_package
from product.backend.personality import render_personality_from_package
from product.backend.relationship import render_relationship_from_package
from product.backend.stability import render_stability_from_package
from product.backend.suitable_job import render_suitable_job_from_package
from product.backend.wealth import render_wealth_from_package


@dataclass
class _SectionSpec:
    key: str
    title: str
    payload_key: str
    renderer: Callable[..., Any]


class _FallbackRenderClient:
    def chat_json(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError('deepseek_disabled')


SECTION_SPECS = [
    _SectionSpec('personality', '性格', 'personality_payload', render_personality_from_package),
    _SectionSpec('wealth', '财运', 'wealth_payload', render_wealth_from_package),
    _SectionSpec('career', '事业', 'career_payload', render_career_from_package),
    _SectionSpec('marriage', '婚姻', 'marriage_payload', render_marriage_from_package),
    _SectionSpec('fortune', '运势', 'fortune_payload', render_fortune_from_package),
    _SectionSpec('health', '健康', 'health_payload', render_health_from_package),
    _SectionSpec('relationship', '人际感情', 'relationship_payload', render_relationship_from_package),
    _SectionSpec('learning', '学习', 'learning_payload', render_learning_from_package),
    _SectionSpec('suitable_job', '适合职业', 'suitable_job_payload', render_suitable_job_from_package),
    _SectionSpec('stability', '稳定性', 'stability_payload', render_stability_from_package),
]


def build_product_review_render(package: dict[str, Any], *, tone_pack: str = 'customer') -> dict[str, Any]:
    client, render_mode, configured_model = _resolve_render_client()
    score_template = package['score_template']
    score_summary = score_template['score_summary']
    rendered_sections, board_result, render_strategy = _render_sections(
        package,
        client=client,
        configured_model=configured_model,
        tone_pack=tone_pack,
        render_mode=render_mode,
    )

    fallback_sections: list[str] = []
    llm_sections: list[str] = []

    for key, section_result in rendered_sections.items():
        if section_result.get('used_fallback'):
            fallback_sections.append(key)
        else:
            llm_sections.append(key)

    if board_result.get('used_fallback'):
        fallback_sections.insert(0, 'board_description')
    else:
        llm_sections.insert(0, 'board_description')

    outline = _build_rendered_outline(score_template, rendered_sections)
    meta = {
        'render_mode': 'llm' if render_mode == 'llm' else 'fallback',
        'render_strategy': render_strategy,
        'configured_model': configured_model,
        'generated_at': _utc_now(),
        'tone_pack': tone_pack,
        'llm_sections': llm_sections,
        'fallback_sections': fallback_sections,
        'used_llm': render_mode == 'llm' and len(llm_sections) > 0,
    }

    return {
        'meta': meta,
        'summary': {
            'title': f"{score_template['board_description_payload']['score_band']} · {score_template['board_description_payload']['main_axis']}",
            'text': board_result['technical_narrative'],
            'highlight': board_result['core_relation_judgement'],
            'recommendation': rendered_sections['stability']['user_facing_paragraph'],
            'score': score_summary['final_score'],
        },
        'board_description': board_result,
        'sections': rendered_sections,
        'outline': outline,
        'actions': _build_actions(rendered_sections),
    }


def _render_sections(
    package: dict[str, Any],
    *,
    client: Any,
    configured_model: str,
    tone_pack: str,
    render_mode: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], str]:
    score_template = package['score_template']

    if render_mode != 'llm':
        return _build_fallback_sections(score_template, tone_pack=tone_pack), _build_board_fallback(score_template, tone_pack=tone_pack), 'fallback'

    strategy = _get_render_strategy()
    if strategy == 'legacy':
        rendered_sections, board_result = _render_sections_legacy(package, client=client, configured_model=configured_model, tone_pack=tone_pack)
        return rendered_sections, board_result, 'legacy'

    try:
        rendered_sections, board_result = _render_sections_batched(score_template, client=client, configured_model=configured_model, tone_pack=tone_pack)
        return rendered_sections, board_result, 'batched'
    except Exception:
        return _build_fallback_sections(score_template, tone_pack=tone_pack), _build_board_fallback(score_template, tone_pack=tone_pack), 'fallback'


def _render_sections_batched(
    score_template: dict[str, Any],
    *,
    client: DeepSeekClient,
    configured_model: str,
    tone_pack: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    context = _build_batch_context(score_template)
    board_result = _build_board_fallback(score_template, tone_pack=tone_pack)
    rendered_sections = _build_fallback_sections(score_template, tone_pack=tone_pack)
    section_groups = _split_section_groups()

    with ThreadPoolExecutor(max_workers=min(3, len(section_groups) + 1)) as executor:
        future_map = {
            executor.submit(
                _render_board_description_batch,
                score_template,
                context,
                client=client,
                model=configured_model,
                tone_pack=tone_pack,
            ): 'board_description',
        }

        for index, section_group in enumerate(section_groups):
            future_map[executor.submit(
                _render_aspects_batch,
                score_template,
                context,
                section_group,
                client=client,
                model=configured_model,
                tone_pack=tone_pack,
            )] = f'aspects:{index}'

        for future in as_completed(future_map):
            target = future_map[future]
            result = future.result()
            if target == 'board_description':
                board_result = result
            else:
                rendered_sections.update(result)

    return rendered_sections, board_result


def _render_board_description_batch(
    score_template: dict[str, Any],
    context: dict[str, Any],
    *,
    client: DeepSeekClient,
    model: str,
    tone_pack: str,
) -> dict[str, Any]:
    fallback = _build_board_fallback(score_template, tone_pack=tone_pack)
    json_example = {
        'board_basis': '一句话解释盘面起点和落宫结构。',
        'core_relation_judgement': '一句话判断这组号码的核心结构关系。',
        'technical_narrative': '一段适合手机阅读的盘面分析，直接说重点。',
    }

    try:
        response = client.chat_json(
            system_prompt=(
                '你是易如反掌 H5 正式产品的盘面文案模型。'
                '你只负责解释锁定结构，不得改写或发明评分、档位、关系。'
                '回答适合手机阅读，要直接、短句、中文自然。'
            ),
            user_prompt=(
                '请根据以下锁定盘面数据，输出一个 JSON object。'
                '不要重复所有字段，只输出需要展示给用户的解释文案。'
                'technical_narrative 控制在 120 到 180 字之间。\n\n'
                f"{json.dumps(context['board'], ensure_ascii=False, separators=(',', ':'))}"
            ),
            json_example=json_example,
            model=model,
            thinking_enabled=False,
            temperature=0.3,
            max_tokens=_get_board_max_tokens(),
        )
        payload = response.json_object()
        board_basis = _clean_text(payload.get('board_basis')) or fallback['board_basis']
        core_relation_judgement = _clean_text(payload.get('core_relation_judgement')) or fallback['core_relation_judgement']
        technical_narrative = _clean_text(payload.get('technical_narrative')) or fallback['technical_narrative']
        used_fallback = not _is_usable(board_basis, minimum=14) or not _is_usable(core_relation_judgement, minimum=14) or not _is_usable(technical_narrative, minimum=60)

        return {
            'board_basis': board_basis,
            'core_relation_judgement': core_relation_judgement,
            'technical_narrative': technical_narrative,
            'practical_manifestation': fallback['practical_manifestation'],
            'tone_pack': tone_pack,
            'model_name': response.model or model,
            'used_fallback': used_fallback,
            'raw_model_output': payload,
        }
    except Exception:
        return fallback


def _render_aspects_batch(
    score_template: dict[str, Any],
    context: dict[str, Any],
    section_specs: list[_SectionSpec],
    *,
    client: DeepSeekClient,
    model: str,
    tone_pack: str,
) -> dict[str, dict[str, Any]]:
    fallback_sections = _build_fallback_sections(score_template, tone_pack=tone_pack)
    json_example = {
        item.key: {
            'core_judgement': f"{item.title}的核心判断。",
            'real_world_manifestation': f"{item.title}在现实中的具体表现。",
            'user_facing_paragraph': f"面向用户的一段{item.title}说明，适合手机阅读。",
        }
        for item in section_specs
    }

    try:
        response = client.chat_json(
            system_prompt=(
                '你是易如反掌 H5 正式产品的十方面结果文案模型。'
                '你只能解释给定的锁定 level、type、manifestation、advice 和 signals。'
                '不要改写档位，不要发明新的结论，不要输出 markdown。'
                '每个方面都先给判断，再落到现实，再写成适合手机端阅读的一小段。'
            ),
            user_prompt=(
                '请根据以下十方面锁定数据，输出一个 JSON object。'
                '每个方面只返回 core_judgement、real_world_manifestation、user_facing_paragraph 三个字段。'
                'user_facing_paragraph 控制在 80 到 140 字之间。\n\n'
                f"{json.dumps({item.key: context['aspects'][item.key] for item in section_specs}, ensure_ascii=False, separators=(',', ':'))}"
            ),
            json_example=json_example,
            model=model,
            thinking_enabled=False,
            temperature=0.35,
            max_tokens=_get_aspects_max_tokens(),
        )
        payload = response.json_object()
        model_name = response.model or model
    except Exception:
        return {item.key: fallback_sections[item.key] for item in section_specs}

    rendered_sections: dict[str, dict[str, Any]] = {}
    for item in section_specs:
        generated = payload.get(item.key)
        payload_item = score_template[item.payload_key]
        fallback = fallback_sections[item.key]

        if not isinstance(generated, dict):
            rendered_sections[item.key] = fallback
            continue

        core_judgement = _clean_text(generated.get('core_judgement')) or fallback['core_judgement']
        manifestation = _clean_text(generated.get('real_world_manifestation')) or fallback['real_world_manifestation']
        paragraph = _clean_text(generated.get('user_facing_paragraph')) or fallback['user_facing_paragraph']
        used_fallback = not _is_usable(core_judgement, minimum=12) or not _is_usable(manifestation, minimum=12) or not _is_usable(paragraph, minimum=40)

        rendered_sections[item.key] = {
            f'{item.key}_level': payload_item['level'],
            f'{item.key}_type': payload_item['type'],
            'core_judgement': core_judgement,
            'real_world_manifestation': manifestation,
            'advice': payload_item['advice'],
            'user_facing_paragraph': paragraph,
            'tone_pack': tone_pack,
            'model_name': model_name,
            'used_fallback': used_fallback,
            'raw_model_output': generated,
        }

    return rendered_sections


def _split_section_groups() -> list[list[_SectionSpec]]:
    group_size = _get_batch_group_size()
    return [SECTION_SPECS[index:index + group_size] for index in range(0, len(SECTION_SPECS), group_size)]


def _render_sections_legacy(package: dict[str, Any], *, client: Any, configured_model: str, tone_pack: str) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    board_result: dict[str, Any] = {}
    rendered_sections: dict[str, dict[str, Any]] = {}
    max_workers = _get_max_workers()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(
                render_board_description_from_package,
                package,
                tone_pack='customer',
                client=client,
                model=configured_model,
                thinking_enabled=False,
            ): 'board_description'
        }

        for item in SECTION_SPECS:
            future_map[executor.submit(
                item.renderer,
                package,
                tone_pack=tone_pack,
                client=client,
                model=configured_model,
                thinking_enabled=False,
            )] = item.key

        for future in as_completed(future_map):
            key = future_map[future]
            result = future.result().to_dict()
            if key == 'board_description':
                board_result = result
            else:
                rendered_sections[key] = result

    return rendered_sections, board_result


def _build_batch_context(score_template: dict[str, Any]) -> dict[str, Any]:
    board_payload = score_template['board_description_payload']
    score_summary = score_template['score_summary']
    structure = score_template['structure']
    four_harms = score_template['four_harms_check']
    pattern_check = score_template['pattern_check']
    outline_map = {item['key']: item for item in score_template['review_outline']}

    aspects = {
        item.key: {
            'title': item.title,
            'level': score_template[item.payload_key]['level'],
            'type': score_template[item.payload_key]['type'],
            'manifestation': score_template[item.payload_key]['manifestation'],
            'advice': score_template[item.payload_key]['advice'],
            'primary_driver': score_template[item.payload_key].get('primary_driver', ''),
            'secondary_driver': score_template[item.payload_key].get('secondary_driver', ''),
            'watch_areas': list(score_template[item.payload_key].get('watch_areas') or [])[:3],
            'facts': list(score_template[item.payload_key].get('facts') or [])[:3],
            'summary': outline_map.get(item.key, {}).get('summary', ''),
            'signals': list(outline_map.get(item.key, {}).get('signals') or [])[:3],
        }
        for item in SECTION_SPECS
    }

    board = {
        'score_band': board_payload['score_band'],
        'final_score': score_summary['final_score'],
        'confidence': score_summary['confidence'],
        'main_axis': board_payload['main_axis'],
        'main_contradiction': board_payload['main_contradiction'],
        'practical_manifestation': board_payload['practical_manifestation'],
        'board_basis': board_payload['board_basis'],
        'technical_focus': board_payload['technical_focus'][:4],
        'manifestation_keywords': board_payload['manifestation_keywords'][:5],
        'palace_door_relation': structure['palace_door_relation'],
        'stem_pair_relation': structure['stem_pair_relation'],
        'structural_cap': score_summary['structural_cap'],
        'score_tags': score_summary['tags'][:4],
        'pattern_detected': list(pattern_check.get('detected') or [])[:4],
        'pattern_edge_flags': list(pattern_check.get('edge_flags') or [])[:4],
        'emptiness': four_harms['emptiness'],
        'door_pressure': four_harms['door_pressure'],
        'tomb': four_harms['tomb'],
        'punishment_hit': four_harms['punishment_hit'],
        'stability_level': score_template['stability_payload']['level'],
        'stability_type': score_template['stability_payload']['type'],
        'stability_manifestation': score_template['stability_payload']['manifestation'],
        'stability_advice': score_template['stability_payload']['advice'],
    }

    return {
        'board': board,
        'aspects': aspects,
    }


def _build_fallback_sections(score_template: dict[str, Any], *, tone_pack: str) -> dict[str, dict[str, Any]]:
    rendered_sections: dict[str, dict[str, Any]] = {}
    for item in SECTION_SPECS:
        payload = score_template[item.payload_key]
        rendered_sections[item.key] = {
            f'{item.key}_level': payload['level'],
            f'{item.key}_type': payload['type'],
            'core_judgement': _build_section_core_judgement(item.title, payload),
            'real_world_manifestation': payload['manifestation'],
            'advice': payload['advice'],
            'user_facing_paragraph': _build_section_paragraph(item.title, payload),
            'tone_pack': tone_pack,
            'model_name': 'fallback-only',
            'used_fallback': True,
            'raw_model_output': None,
        }
    return rendered_sections


def _build_board_fallback(score_template: dict[str, Any], *, tone_pack: str) -> dict[str, Any]:
    board_payload = score_template['board_description_payload']
    score_summary = score_template['score_summary']
    structure = score_template['structure']
    pattern_check = score_template['pattern_check']
    four_harms = score_template['four_harms_check']
    board_basis = board_payload['board_basis']
    active_patterns = '、'.join((pattern_check.get('detected') or [])[:3]) or '常规结构'
    active_harms = '、'.join([
        four_harms['emptiness'],
        four_harms['door_pressure'],
        four_harms['tomb'],
        four_harms['punishment_hit'],
    ])

    return {
        'board_basis': (
            f"末七位 {board_basis['last7']} 由 {board_basis['trigger']} 触发，落在 {board_basis['palace']} 宫，"
            f"神为 {board_basis['god']}、星为 {board_basis['star']}、门为 {board_basis['door']}，"
            f"天盘 {board_basis['heaven_stem']}、地盘 {board_basis['earth_stem']}。"
        ),
        'core_relation_judgement': (
            f"这组号码的核心关系落在“{structure['palace_door_relation']}”与“{structure['stem_pair_relation']}”上，"
            f"再叠加 {active_patterns} 与 {active_harms}，所以整体不是没有推动力，而是关键承接位更容易发空、受压或反复。"
        ),
        'technical_narrative': (
            f"这组号码当前处在“{board_payload['score_band']}”区间，综合分 {score_summary['final_score']}，主轴是“{board_payload['main_axis']}”。"
            f" 真正的卡点不是表面完全做不动，而是“{board_payload['main_contradiction']}”。"
            f" 也就是说，前段能推、场面不差，但一到承接、持续和落地阶段，更容易出现节奏被拖慢、推进反复、结果放大之后难收的情况。"
        ),
        'practical_manifestation': board_payload['practical_manifestation'],
        'tone_pack': tone_pack,
        'model_name': 'fallback-only',
        'used_fallback': True,
        'raw_model_output': None,
    }


def _build_section_core_judgement(title: str, payload: dict[str, Any]) -> str:
    return f"{title}层面属于“{payload['level']}”，整体更接近“{payload['type']}”，主要表现是{payload['manifestation']}"


def _build_section_paragraph(title: str, payload: dict[str, Any]) -> str:
    primary_driver = str(payload.get('primary_driver') or '').strip()
    secondary_driver = str(payload.get('secondary_driver') or '').strip()
    watch_areas = [str(item).strip() for item in list(payload.get('watch_areas') or [])[:3] if str(item).strip()]
    parts = [
        f"{title}这块更像是“{payload['type']}”的表现，当前状态是“{payload['level']}”。",
        str(payload['manifestation']).strip(),
    ]

    if primary_driver:
        parts.append(f"主导力量更偏向“{primary_driver}”。")
    if secondary_driver:
        parts.append(f"次级牵动点在“{secondary_driver}”。")
    if watch_areas:
        parts.append(f"使用时更要留意 {('、'.join(watch_areas))}。")

    return ' '.join(part for part in parts if part)


def _get_render_strategy() -> str:
    raw_value = os.getenv('EASEWISE_REVIEW_RENDER_STRATEGY', 'batched').strip().lower()
    if raw_value == 'legacy':
        return 'legacy'
    return 'batched'


def _get_max_workers() -> int:
    raw_value = os.getenv('EASEWISE_REVIEW_RENDER_WORKERS', '4').strip()
    try:
        return max(1, min(8, int(raw_value)))
    except ValueError:
        return 4


def _get_board_max_tokens() -> int:
    return _get_int_env('EASEWISE_REVIEW_BOARD_MAX_TOKENS', 650, minimum=200, maximum=1600)


def _get_aspects_max_tokens() -> int:
    return _get_int_env('EASEWISE_REVIEW_ASPECTS_MAX_TOKENS', 1800, minimum=600, maximum=3200)


def _get_batch_group_size() -> int:
    return _get_int_env('EASEWISE_REVIEW_BATCH_GROUP_SIZE', 5, minimum=2, maximum=10)


def _get_int_env(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        return max(minimum, min(maximum, int(raw_value)))
    except ValueError:
        return default


def _resolve_render_client() -> tuple[Any, str, str]:
    load_env_file()
    if not os.getenv('DEEPSEEK_API_KEY', '').strip():
        return _FallbackRenderClient(), 'fallback', 'fallback-only'

    try:
        client = DeepSeekClient.from_env()
        configured_model = os.getenv('EASEWISE_REVIEW_MODEL', '').strip() or client.config.model
        return client, 'llm', configured_model
    except Exception:
        return _FallbackRenderClient(), 'fallback', 'fallback-only'


def _build_rendered_outline(score_template: dict[str, Any], rendered_sections: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for outline_item in score_template['review_outline']:
        section = rendered_sections.get(outline_item['key'], {})
        level_key = next((item for item in section.keys() if item.endswith('_level')), '')
        type_key = next((item for item in section.keys() if item.endswith('_type')), '')

        items.append({
            'key': outline_item['key'],
            'title': outline_item['title'],
            'summary': outline_item['summary'],
            'signals': outline_item['signals'],
            'level': section.get(level_key, ''),
            'type': section.get(type_key, ''),
            'core_judgement': section.get('core_judgement', ''),
            'manifestation': section.get('real_world_manifestation', ''),
            'advice': section.get('advice', ''),
            'paragraph': section.get('user_facing_paragraph', ''),
            'used_fallback': bool(section.get('used_fallback')),
            'model_name': section.get('model_name', ''),
        })

    return items


def _build_actions(rendered_sections: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    action_specs = [
        ('01', '先看整体稳定性', rendered_sections['stability']['advice']),
        ('02', '再看事业与财运', f"{rendered_sections['career']['advice']} {rendered_sections['wealth']['advice']}"),
        ('03', '最后看关系与长期使用', f"{rendered_sections['relationship']['advice']} {rendered_sections['personality']['advice']}"),
    ]

    return [
        {
            'step': step,
            'title': title,
            'text': text.strip(),
        }
        for step, title, text in action_specs
    ]


def _clean_text(value: Any) -> str:
    return str(value or '').strip()


def _is_usable(value: str, *, minimum: int) -> bool:
    return len(value.strip()) >= minimum


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
