from __future__ import annotations
from typing import Any

RELATION_LABELS={"palace_generates_door":"宫生门","same_element":"同气","door_generates_palace":"门生宫","palace_controls_door":"宫克门","door_controls_palace":"门克宫","heaven_generates_earth":"天干生地干","earth_generates_heaven":"地干生天干","heaven_controls_earth":"天干克地干","earth_controls_heaven":"地干克天干","unrelated":"关系平"}
PATTERN_LABELS={"triple_same":"三连号放大","peach_blossom_111_999":"111/999 桃花放大","pair_69_96":"69/96 风险组合","pair_25_95":"25/95 重风险组合","pair_27_99_92":"27/99/92 扰动组合","tail_repeat_bias":"尾位重复偏压"}
CAP_REASON_LABELS={"pair_25_95":"25/95 触发结构封顶","pair_69_96":"69/96 触发结构封顶","stacked_27_99_92":"27/99/92 多重叠加触发封顶","palace_empty_with_door_pressure":"宫空亡叠加门迫触发封顶","multiple_heavy_harms":"多重重害叠加触发封顶"}
PERSONALITY_LEVELS=["性格底色很稳","性格整体顺手","有特点，但更吃表达方式","情绪张力偏明显","长期容易拧巴内耗"]
PERSONALITY_TYPES=["主动外放型","务实结果型","细腻感受型","谨慎防御型","敏感拉扯型","强压硬撑型","慢热压抑型","表达存在型"]
DOOR_PERSONALITY={"休门":"慢热、克制、重观察","生门":"务实、重结果、重落地","开门":"主动、外放、推动力强","景门":"在意表达与反馈","惊门":"反应快、警觉高、易紧绷","杜门":"谨慎、保守、防备心重","伤门":"直接、较真、容易硬碰硬","死门":"收着来、压得住、容易闷着扛"}
GOD_TONE={"值符":"主见和掌控感","值符+九天":"主见、外扩和冲劲","六合":"讲关系、讲配合","太阴":"细腻、顾虑多、心思深","九天":"想做大、想拉开空间","九地":"偏稳、偏慢、偏守","玄武":"防备强、内心不轻易外露","腾蛇":"多想、多绕、容易敏感","白虎":"压力感重、容易较硬"}

def _label(m:dict[str,str],v:str)->str:return m.get(v,v)
def _label_list(m:dict[str,str],vals:list[str])->list[str]:return[_label(m,v) for v in vals]
def _humanize_harm(flag:bool,layers:list[str],labels:dict[str,str])->str:
    if not flag:return"无"
    if not layers:return"有"
    return f"有（{'、'.join(labels.get(x,x) for x in layers)}）"

def _pick_level(result:dict[str,Any],final_score:int)->str:
    h=result["features"]["harms"];p=result["features"]["patterns"];heavy=int(h["door_pressure"])+int(h["tomb"])+int(h["punishment_hit"])
    has_empty=bool(h["emptiness_layers"]);risk=len(set(p["risk_pairs"]));cap=bool(result["scoring"]["structural_cap_reasons"])
    if heavy>=2 or final_score<45 or "pair_25_95" in p["detected"]:return"长期容易拧巴内耗"
    if heavy>=1 or (has_empty and risk>=1) or final_score<65:return"情绪张力偏明显"
    if has_empty or risk>=1 or cap or final_score<80:return"有特点，但更吃表达方式"
    if final_score>=95 and heavy==0 and not has_empty and not p["detected"]:return"性格底色很稳"
    return"性格整体顺手"

def _pick_type(result:dict[str,Any])->str:
    s=result["board"]["symbols"];door,star,god=s["door"],s["star"],s["god"];h=result["features"]["harms"]
    if door=="死门" or star=="天芮" or h["tomb"]:return"慢热压抑型"
    if door=="伤门" or god=="白虎":return"强压硬撑型"
    if door=="惊门" or god=="腾蛇":return"敏感拉扯型"
    if door=="杜门" or god=="玄武":return"谨慎防御型"
    if door=="休门" or god in {"太阴","六合"} or star=="天辅":return"细腻感受型"
    if door=="生门" or star=="天任":return"务实结果型"
    if door=="景门" or star=="天英":return"表达存在型"
    return"主动外放型"

def _manifest(t:str)->str:return{"主动外放型":"更容易给人主动、直接、愿意先动起来的感觉。","务实结果型":"说话做事更偏落地、看实际，先看有没有结果。","细腻感受型":"感受力和细节感更强，容易先接收到气氛和情绪。","谨慎防御型":"先观察、后表态，边界感和防备心会更明显。","敏感拉扯型":"对外界反馈比较敏感，容易想多，也更容易被情绪牵动。","强压硬撑型":"表面像能扛得住，但压力一上来更容易硬顶和较真。","慢热压抑型":"打开得慢，很多感受会先压着，不会第一时间摊开。","表达存在型":"更在意表达感、存在感和别人能不能接收到自己的状态。"}[t]

def _watch_areas(result:dict[str,Any],final_score:int)->list[dict[str,str]]:
    s=result["board"]["symbols"];f=result["features"];h=f["harms"];p=f["patterns"];risk=set(p["risk_pairs"]);det=set(p["detected"]);areas=[]
    def add(a,r,sc):
        if any(i["area"]==a for i in areas):return
        areas.append({"area":a,"reason":r,"scenario":sc})
    if s["door"] in {"景门","开门","伤门","惊门"} or s["god"] in {"值符","九天","白虎"}:add("对外表达","话风、存在感和第一反应更容易被别人直接感知。","开会发言、社交表达和需要快速表态的时候更明显。")
    if h["door_pressure"] or h["punishment_hit"] or s["god"] in {"腾蛇","白虎"}:add("情绪反应","压力一上来时，性格和反应速度更容易把棱角放大。","被催促、被质疑、遇到冲突或高压场景时更明显。")
    if h["emptiness"] or s["door"] in {"杜门","死门"} or s["god"] in {"太阴","玄武"}:add("边界感","不轻易摊开自己，很多真实想法会先留在心里。","刚进入新环境、需要信任建立或关系还不熟的时候更明显。")
    if det.intersection({"pair_27_99_92","peach_blossom_111_999"}) or risk.intersection({"27","99","92"}):add("关系感受","外界反馈、人情往来和关系气氛更容易影响当下状态。","社交互动、关系敏感期和在意别人看法的时候更明显。")
    if h["tomb"] or result["scoring"]["structural_cap_reasons"] or final_score<60:add("内在承接","很多压力不是立刻爆出来，而是后段更容易沉成拧巴和内耗。","长期相处、连续高压或需要长期稳定输出的时候更明显。")
    if not areas and final_score>=80:add("日常相处","整体顺手，但真正拉开差距的还是长期相处里的细节处理。","熟人相处、长期合作和重复沟通时更能看出质感。")
    return areas[:3]

def _deduction_reasons(result:dict[str,Any])->list[str]:
    f=result["features"];h=f["harms"];p=f["patterns"];sc=result["scoring"];reasons=[]
    def add(t):
        if t not in reasons:reasons.append(t)
    if h["emptiness"]:add("空亡会让一些真实想法和情绪不那么直接落地，表达上更容易留白或收着。")
    if h["door_pressure"]:add("宫门相克时，性格里的松弛感会被压缩，做事和说话更容易带着拧劲。")
    if h["tomb"]:add("入墓会让感受和情绪更容易压在后面，短期看不明显，长期更容易发沉。")
    if h["punishment_hit"]:add("击刑会把较真、反复、硬碰硬或情绪内耗这一面放大。")
    if set(p["risk_pairs"]).intersection({"27","99","92"}) or set(p["detected"]).intersection({"pair_27_99_92","peach_blossom_111_999"}):add("外部扰动组合会让性格更容易被关系、人情和外界反馈带节奏。")
    for r in sc["structural_cap_reasons"]:add(f"结构封顶提示：{CAP_REASON_LABELS.get(r,r)}。")
    return reasons[:3]

def _advice(level:str,result:dict[str,Any],final_score:int)->str:
    area_text="、".join(i["area"] for i in _watch_areas(result,final_score)[:2]) or "关键场景"
    if final_score==100:return"这个号的性格呈现非常完整，建议坚持长期使用。"
    if level=="性格底色很稳":return"如果你看重自己的对外气质和表达稳定，这个号可以长期坚持使用。" if final_score>=95 else "可以长期使用，适合把自己的自然节奏和稳定表达慢慢放大出来。"
    if level=="性格整体顺手":return f"可以长期使用，整体顺手；如果你在意{area_text}的细腻度，再多留一点调节空间会更好。"
    if level=="有特点，但更吃表达方式":return f"可以继续使用，但更适合有意识地调整表达和节奏；如果你特别看重{area_text}，不要把它当成完全无代价的配置。"
    if level=="情绪张力偏明显":return f"如果你很在意对外气质、情绪稳定和沟通舒服度，这个号不建议长期硬扛，尤其在{area_text}上更容易放大问题。"
    return f"如果你很在意对外气质、情绪稳定和沟通舒服度，这个号不建议继续长期使用，建议优先调整，尤其要正视{area_text}这几层扣分。"

def build_personality_payload(result:dict[str,Any],final_score:int,labels:dict[str,str])->dict[str,Any]:
    b=result["board"];f=result["features"];h=f["harms"];p=f["patterns"];sc=result["scoring"];s=b["symbols"]
    level=_pick_level(result,final_score);ptype=_pick_type(result);watch=_watch_areas(result,final_score);reasons=_deduction_reasons(result)
    primary="表达层"
    if s["door"] in {"杜门","死门"} or h["emptiness"]:primary="边界层"
    elif s["god"] in {"腾蛇","白虎"} or h["punishment_hit"]:primary="情绪层"
    elif h["tomb"]:primary="承接层"
    secondary="表达层"
    if primary!="情绪层" and (h["door_pressure"] or h["punishment_hit"]):secondary="情绪层"
    elif primary!="边界层" and (h["emptiness"] or s["door"] in {"杜门","死门"}):secondary="边界层"
    elif primary!="承接层" and h["tomb"]:secondary="承接层"
    return {"level":level,"type":ptype,"primary_driver":primary,"secondary_driver":secondary,"manifestation":_manifest(ptype),"advice":_advice(level,result,final_score),"score_gap":max(0,100-final_score),"watch_areas":watch,"deduction_reasons":reasons,"facts":{"score_after_structural_cap":final_score,"confidence":sc["confidence"],"palace_door_relation":_label(RELATION_LABELS,f["palace_door_relation"]),"stem_pair_relation":_label(RELATION_LABELS,f["stem_pair_relation"]),"door":s["door"],"star":s["star"],"god":s["god"],"door_personality":DOOR_PERSONALITY.get(s["door"],"有自己的节奏和边界感"),"god_tone":GOD_TONE.get(s["god"],"明显的内在驱动力"),"four_harms":{"emptiness":_humanize_harm(h["emptiness"],h["emptiness_layers"],labels),"door_pressure":_humanize_harm(h["door_pressure"],[],labels),"tomb":_humanize_harm(h["tomb"],h["tomb_layers"],labels),"punishment_hit":_humanize_harm(h["punishment_hit"],h["punishment_layers"],labels)},"pattern_flags":_label_list(PATTERN_LABELS,p["detected"]),"risk_pairs":p["risk_pairs"],"structural_cap_reasons":_label_list(CAP_REASON_LABELS,sc["structural_cap_reasons"]),"tags":sc["tags"]},"model_pack":{"allowed_levels":PERSONALITY_LEVELS,"allowed_types":PERSONALITY_TYPES,"rendering_goal":"Explain what kind of outward personality tone this number reinforces, where the missing points fall, and whether it still suits long-term use.","client_tone":"Professional but readable. Explain temperament, expression, emotional handling and practical long-term usage clearly."}}