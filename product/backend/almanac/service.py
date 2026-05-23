from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

from lunar_python import Solar

ASIA_SHANGHAI = timezone(timedelta(hours=8))


@dataclass
class AlmanacDay:
    solar_date: str
    display_date: str
    weekday_label: str
    lunar_date: str
    lunar_full_text: str
    ganzhi_year: str
    ganzhi_month: str
    ganzhi_day: str
    zodiac_year: str
    zodiac_month: str
    zodiac_day: str
    yi: list[str]
    ji: list[str]
    yi_summary: str
    ji_summary: str
    solar_term: str | None
    festivals: list[str]
    pengzu_gan: str
    pengzu_zhi: str
    pengzu_summary: str
    chong: str
    sha: str
    zhi_xing: str
    tian_shen: str
    tian_shen_luck: str
    ji_shen: list[str]
    xiong_sha: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "solar_date": self.solar_date,
            "display_date": self.display_date,
            "weekday_label": self.weekday_label,
            "lunar_date": self.lunar_date,
            "lunar_full_text": self.lunar_full_text,
            "ganzhi_year": self.ganzhi_year,
            "ganzhi_month": self.ganzhi_month,
            "ganzhi_day": self.ganzhi_day,
            "zodiac_year": self.zodiac_year,
            "zodiac_month": self.zodiac_month,
            "zodiac_day": self.zodiac_day,
            "yi": self.yi,
            "ji": self.ji,
            "yi_summary": self.yi_summary,
            "ji_summary": self.ji_summary,
            "solar_term": self.solar_term,
            "festivals": self.festivals,
            "pengzu_gan": self.pengzu_gan,
            "pengzu_zhi": self.pengzu_zhi,
            "pengzu_summary": self.pengzu_summary,
            "chong": self.chong,
            "sha": self.sha,
            "zhi_xing": self.zhi_xing,
            "tian_shen": self.tian_shen,
            "tian_shen_luck": self.tian_shen_luck,
            "ji_shen": self.ji_shen,
            "xiong_sha": self.xiong_sha,
        }


def build_today_almanac(now: datetime | None = None) -> AlmanacDay:
    current = now.astimezone(ASIA_SHANGHAI) if now is not None else datetime.now(ASIA_SHANGHAI)
    return build_almanac_for_date(current.date())


def build_almanac_for_date(target_date: date) -> AlmanacDay:
    midday = datetime.combine(target_date, time(hour=12), tzinfo=ASIA_SHANGHAI)
    solar = Solar.fromDate(midday)
    lunar = solar.getLunar()
    yi = list(lunar.getDayYi())
    ji = list(lunar.getDayJi())
    festivals = list(solar.getFestivals()) + list(solar.getOtherFestivals())
    return AlmanacDay(
        solar_date=solar.toYmd(),
        display_date=f"{target_date.year}年{target_date.month:02d}月{target_date.day:02d}日 星期{solar.getWeekInChinese()}",
        weekday_label=f"星期{solar.getWeekInChinese()}",
        lunar_date=lunar.toString(),
        lunar_full_text=lunar.toFullString(),
        ganzhi_year=lunar.getYearInGanZhi(),
        ganzhi_month=lunar.getMonthInGanZhi(),
        ganzhi_day=lunar.getDayInGanZhi(),
        zodiac_year=lunar.getYearShengXiao(),
        zodiac_month=lunar.getMonthShengXiao(),
        zodiac_day=lunar.getDayShengXiao(),
        yi=yi,
        ji=ji,
        yi_summary=_summarize_actions(yi),
        ji_summary=_summarize_actions(ji),
        solar_term=lunar.getJieQi() or None,
        festivals=festivals,
        pengzu_gan=lunar.getPengZuGan(),
        pengzu_zhi=lunar.getPengZuZhi(),
        pengzu_summary=f"{lunar.getPengZuGan()}；{lunar.getPengZuZhi()}",
        chong=lunar.getDayChongDesc(),
        sha=lunar.getDaySha(),
        zhi_xing=lunar.getZhiXing(),
        tian_shen=lunar.getDayTianShen(),
        tian_shen_luck=lunar.getDayTianShenLuck(),
        ji_shen=list(lunar.getDayJiShen()),
        xiong_sha=list(lunar.getDayXiongSha()),
    )


def _summarize_actions(items: list[str], *, limit: int = 6) -> str:
    if not items:
        return ""
    return "、".join(items[:limit])
