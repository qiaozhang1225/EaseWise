import express from "express";
import path from "path";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const app = express();
const PORT = 3000;

app.use(express.json({ limit: '10mb' }));

// Initialise Gemini client if API key is provided
let ai: GoogleGenAI | null = null;
if (process.env.GEMINI_API_KEY) {
  ai = new GoogleGenAI({
    apiKey: process.env.GEMINI_API_KEY,
    httpOptions: {
      headers: {
        'User-Agent': 'aistudio-build',
      }
    }
  });
  console.log("Gemini API Client loaded successfully server-side.");
} else {
  console.warn("GEMINI_API_KEY is not defined in environment variables. Metaphysics Chatbot will use fallback mock answers.");
}

// Global In-Memory Database State
const usersMock: Record<string, any> = {};
const pointsMock: Record<string, any> = {};
const pointsLedgerMock: Record<string, any[]> = {};
const phoneReviewsMock: Record<string, any[]> = {};
const baziReviewsMock: Record<string, any[]> = {};
const claimsLinksMock: Record<string, any> = {};
const rechargeOrdersMock: Record<string, any> = {};

// --- MOCK CONSTANTS & STUDS GENERATORS ---
const seedNow = new Date().toISOString();

function getGanzhiForYear(year: number): string {
  const tianGan = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"];
  const diZhi = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
  const offset = year - 4;
  const tgIdx = ((offset % 10) + 10) % 10;
  const dzIdx = ((offset % 12) + 12) % 12;
  return tianGan[tgIdx] + diZhi[dzIdx];
}

function mockCycleRenderResult(cycleKey: string, titleStr: string): any {
  return {
    title: `${titleStr}中和得势局`,
    core_theme: `此十年大运正值五行气场流转，命局调候得当。主事业稳步攀升，多有贵人指引、合作共创。`,
    opportunities: `机遇：利于技术突破、产品开拓或组建新团队。逢水木流年尤佳。`,
    risks: `风险：提防五行交会或燥土克水之期的精力透支或职场口角纷扰。`,
    action_guidance: `建议：静心打磨核心能力，避免跟风投机，稳健理财。`
  };
}

function mockYearRenderResult(year: number, cycleKey: string): any {
  return {
    title: `流年 ${year}：岁运相交运转乾坤`,
    year_focus: `此流年运生旺相，木火通明。宜专注于业务核心及团队架构扩张，切莫盲动。`,
    opportunities: `机遇：有新的合伙人邀请，或开拓出第二增长极财务渠道。`,
    risks: `风险：秋季金水流月时，需合理规划资金链开销，防范入不敷出。`,
    action_guidance: `建议：做好中长期现金流保障，凡事契约先行，谨慎扩张。`
  };
}

function generateMockLuckCycles(userId: string, birthYear: number = 1995): any[] {
  const currentYear = new Date().getFullYear();
  
  // Cycle 1: 2024 - 2033
  const cycle1Years: any[] = [];
  for (let y = 2024; y <= 2033; y++) {
    const isCurrentY = (y === currentYear);
    cycle1Years.push({
      year: y,
      age: y - birthYear,
      ganzhi: getGanzhiForYear(y),
      is_current: isCurrentY,
      render_status: isCurrentY ? "completed" : "not_generated",
      render: isCurrentY ? {
        id: `rnd_y_${y}`,
        render_id: `rnd_y_${y}`,
        review_id: "seed_bz_review",
        user_id: userId,
        render_type: "liunian",
        cycle_key: "cycle_1",
        year: y,
        status: "completed",
        progress_message: null,
        facts: null,
        result: mockYearRenderResult(y, "cycle_1"),
        points_cost: 30,
        error_message: null,
        retry_count: 0,
        last_attempt_at: new Date().toISOString(),
        next_retry_available_at: null,
        is_retryable: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      } : null
    });
  }

  // Cycle 2: 2034 - 2043
  const cycle2Years: any[] = [];
  for (let y = 2034; y <= 2043; y++) {
    cycle2Years.push({
      year: y,
      age: y - birthYear,
      ganzhi: getGanzhiForYear(y),
      is_current: false,
      render_status: "not_generated",
      render: null
    });
  }

  // Cycle 3: 2044 - 2053
  const cycle3Years: any[] = [];
  for (let y = 2044; y <= 2053; y++) {
    cycle3Years.push({
      year: y,
      age: y - birthYear,
      ganzhi: getGanzhiForYear(y),
      is_current: false,
      render_status: "not_generated",
      render: null
    });
  }

  return [
    {
      cycle_key: "cycle_1",
      start_year: 2024,
      end_year: 2033,
      start_age: 29,
      end_age: 38,
      ganzhi: "己亥",
      display_ganzhi: "己亥大运",
      is_current: true,
      render_status: "completed",
      render: {
        id: "rnd_c_1",
        render_id: "rnd_c_1",
        review_id: "seed_bz_review",
        user_id: userId,
        render_type: "dayun",
        cycle_key: "cycle_1",
        year: null,
        status: "completed",
        progress_message: null,
        facts: null,
        result: mockCycleRenderResult("cycle_1", "己亥大运"),
        points_cost: 80,
        error_message: null,
        retry_count: 0,
        last_attempt_at: new Date().toISOString(),
        next_retry_available_at: null,
        is_retryable: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      },
      year_items: cycle1Years
    },
    {
      cycle_key: "cycle_2",
      start_year: 2034,
      end_year: 2043,
      start_age: 39,
      end_age: 48,
      ganzhi: "庚子",
      display_ganzhi: "庚子大运",
      is_current: false,
      render_status: "not_generated",
      render: null,
      year_items: cycle2Years
    },
    {
      cycle_key: "cycle_3",
      start_year: 2044,
      end_year: 2053,
      start_age: 49,
      end_age: 58,
      ganzhi: "辛丑",
      display_ganzhi: "辛丑大运",
      is_current: false,
      render_status: "not_generated",
      render: null,
      year_items: cycle3Years
    }
  ];
}

function generate12Aspects(): any[] {
  return [
    {
      aspect_key: "career",
      title: "事业发展评测",
      short_title: "事业与机遇",
      score: 88,
      is_unlocked: true,
      unlock_points: 50,
      content: "九天在上，天冲加持，开拓创新势如破竹。适合做初创企业领导人或产品开拓经理。",
      risk: "阻力虽有，但多为贵人敲打，终成大气。",
      elements_check: { "起爆期": "逢庚辛年", "行业契合": "雷木相合" }
    },
    {
      aspect_key: "wealth",
      title: "财富积累剖析",
      short_title: "财富与求财",
      score: 82,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "love",
      title: "感情桃花大势",
      short_title: "感情与婚恋",
      score: 79,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "health",
      title: "身心健康气场",
      short_title: "健康与精力",
      score: 85,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "acad",
      title: "学术科名修证",
      short_title: "文昌与晋升",
      score: 88,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "fortune",
      title: "本命流年运势",
      short_title: "流年起落",
      score: 81,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "investment",
      title: "投资理财格局",
      short_title: "投资决策",
      score: 75,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "travel",
      title: "出行与迁徙向",
      short_title: "出行安全",
      score: 80,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "social",
      title: "社交与人际福德",
      short_title: "人际贵人",
      score: 83,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "family",
      title: "家庭环境熏陶",
      short_title: "家庭成员",
      score: 86,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "personality",
      title: "本性与真我神气",
      short_title: "性格格调",
      score: 90,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "fengshui",
      title: "居住风水气场",
      short_title: "环境风水",
      score: 78,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    }
  ];
}

function generateBaziAspects(): any[] {
  return [
    {
      aspect_key: "personality",
      title: "日主强弱与性格格局",
      short_title: "日主性格",
      score: 85,
      is_unlocked: true,
      unlock_points: 50,
      content: "日干辛金，虽生在巳月死地，但自坐未土冠带偏印，且年、月己土高透生身。辛金虽柔，得势则清。局中火旺，急需癸水润局，时干癸水食神制杀得体，格局清粹。",
      risk: "身偏弱燥火，凡事易急躁、精力透支，注意心血管及眼部保养。",
      elements_check: { "基本得势": "偏弱得生", "用神首选": "癸水食神" }
    },
    {
      aspect_key: "career",
      title: "事业发展气运大势",
      short_title: "事业大势",
      score: 89,
      is_unlocked: true,
      unlock_points: 50,
      content: "官星当令，癸水制煞，事业方向宜选择技术开发、规划咨询、高知型合作，在体系内多有权威重托。",
      risk: "食神制官杀，不妥协容易得罪上司或多承担额外责任。",
      elements_check: { "成就梯阶": "金水相得", "职业方向": "谋略、高管" }
    },
    {
      aspect_key: "wealth",
      title: "财富积累深度剖析",
      short_title: "财运大势",
      score: 82,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "love",
      title: "婚姻与桃花缘分剖析",
      short_title: "婚恋桃花",
      score: 79,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "health",
      title: "身心五行健康分析",
      short_title: "健康调理",
      score: 84,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    },
    {
      aspect_key: "family_environment",
      title: "家庭环境与祖家荫佑",
      short_title: "家庭环境",
      score: 83,
      is_unlocked: false,
      unlock_points: 50,
      content: null,
      risk: null,
      elements_check: {}
    }
  ];
}

// ------ SEEDING PROCESS WITH 4 SPECIFIC ACCOUNTS ------

// User 1: 13800138000 (High Points, Full Regression Account)
usersMock["13800138000"] = {
  user_id: "u_13800138000",
  uid: "EW-DEMO-001",
  status: 'active',
  identity_level: 'promoter',
  nickname: "同修小易",
  avatar_url: null,
  profile_completed: true,
  created_at: seedNow,
  updated_at: seedNow,
  last_active_at: seedNow,
  password: "Easewise123!"
};
pointsMock["u_13800138000"] = { balance: 20000, frozen_balance: 0, created_at: seedNow, updated_at: seedNow };
pointsLedgerMock["u_13800138000"] = [
  { ledger_id: "led_init_138_1", change_type: "add", delta: 10000, balance_after: 10000, biz_type: "register_bonus", biz_id: "signup", idempotency_key: null, remark: "欢迎同修小易加入灵台本命注册礼包", created_at: seedNow },
  { ledger_id: "led_init_138_2", change_type: "add", delta: 10150, balance_after: 20150, biz_type: "recharge", biz_id: "ord_init_1", idempotency_key: null, remark: "充值5000积分同修福慧包", created_at: new Date(Date.now() - 600000).toISOString() },
  { ledger_id: "led_init_138_3", change_type: "deduct", delta: -100, balance_after: 20050, biz_type: "phone_review", biz_id: "seed_ph_review", idempotency_key: null, remark: "快捷号码能量评测：138****8000", created_at: new Date(Date.now() - 3600000).toISOString() },
  { ledger_id: "led_init_138_4", change_type: "deduct", delta: -50, balance_after: 20000, biz_type: "aspect_unlock", biz_id: "seed_ph_review", idempotency_key: null, remark: "解锁手机评测细项「财富积累剖析」", created_at: new Date(Date.now() - 3500000).toISOString() }
];

// User 2: 13900139000 (High Points, Empty History Account)
usersMock["13900139000"] = {
  user_id: "u_13900139000",
  uid: "EW-DEMO-002",
  status: 'active',
  identity_level: 'standard',
  nickname: "同修无漏",
  avatar_url: null,
  profile_completed: false,
  created_at: seedNow,
  updated_at: seedNow,
  last_active_at: seedNow,
  password: "Easewise123!"
};
pointsMock["u_13900139000"] = { balance: 3000, frozen_balance: 0, created_at: seedNow, updated_at: seedNow };
pointsLedgerMock["u_13900139000"] = [
  { ledger_id: "led_init_139_1", change_type: "add", delta: 3000, balance_after: 3000, biz_type: "register_bonus", biz_id: "signup", idempotency_key: null, remark: "快捷高阶福运礼包发配", created_at: seedNow }
];

// User 3: 13600136000 (120 points, can do base evaluation but details trigger insufficient)
usersMock["13600136000"] = {
  user_id: "u_13600136000",
  uid: "EW-DEMO-003",
  status: 'active',
  identity_level: 'standard',
  nickname: "同修局促",
  avatar_url: null,
  profile_completed: true,
  created_at: seedNow,
  updated_at: seedNow,
  last_active_at: seedNow,
  password: "Easewise123!"
};
pointsMock["u_13600136000"] = { balance: 120, frozen_balance: 0, created_at: seedNow, updated_at: seedNow };
pointsLedgerMock["u_13600136000"] = [
  { ledger_id: "led_init_136_1", change_type: "add", delta: 120, balance_after: 120, biz_type: "register_bonus", biz_id: "signup", idempotency_key: null, remark: "修行体验大礼包赠分", created_at: seedNow }
];

// User 4: 13500135000 (30 points, immediate insufficient-points trigger)
usersMock["13500135000"] = {
  user_id: "u_13500135000",
  uid: "EW-DEMO-004",
  status: 'active',
  identity_level: 'standard',
  nickname: "同修微尘",
  avatar_url: null,
  profile_completed: true,
  created_at: seedNow,
  updated_at: seedNow,
  last_active_at: seedNow,
  password: "Easewise123!"
};
pointsMock["u_13500135000"] = { balance: 30, frozen_balance: 0, created_at: seedNow, updated_at: seedNow };
pointsLedgerMock["u_13500135000"] = [
  { ledger_id: "led_init_135_1", change_type: "add", delta: 30, balance_after: 30, biz_type: "register_bonus", biz_id: "signup", idempotency_key: null, remark: "初学入门基本功德包", created_at: seedNow }
];

// User 5: 13700137000 (Empty history fallback)
usersMock["13700137000"] = {
  user_id: "u_13700137000",
  uid: "EW-DEMO-005",
  status: 'active',
  identity_level: 'standard',
  nickname: "同修初悟",
  avatar_url: null,
  profile_completed: true,
  created_at: seedNow,
  updated_at: seedNow,
  last_active_at: seedNow,
  password: "Easewise123!"
};
pointsMock["u_13700137000"] = { balance: 20000, frozen_balance: 0, created_at: seedNow, updated_at: seedNow };
pointsLedgerMock["u_13700137000"] = [
  { ledger_id: "led_init_137_1", change_type: "add", delta: 20000, balance_after: 20000, biz_type: "register_bonus", biz_id: "signup", idempotency_key: null, remark: "本命无执念注册福星点券赠送", created_at: seedNow }
];


// --- HISTORIC REPORTS PRE-SEEDING ---

// Phone reports list
const seedPh138 = {
  id: "seed_ph_review",
  report_id: "seed_rep_ph_1",
  phone: "13800138000",
  phone_number: "13800138000",
  masked_phone: "138****8000",
  gender: "male",
  status: "completed",
  progress_stage: "completed",
  progress_message: "智能排盘推论完成",
  score: 83,
  score_markdown: `*此手机号码之中蕴含吉神【值符加临震宫】，性格直率果决，大利开疆拓土与经商发财。*`,
  error_message: null,
  created_at: new Date(Date.now() - 3600000).toISOString(),
  updated_at: new Date(Date.now() - 3600000).toISOString(),
  phone_summary: {
    title: "震木长生吉局",
    risk: "极低",
    usage_guidance: "宜作事业拓展核心连通或商务总机，五行震木透发，生机勃勃。",
    elements_check: {
      "卦德": "高瞻远瞩",
      "生克": "五行清粹，无克无伤"
    }
  },
  board: {
    center_basis: { trigger: "九天震宫" },
    active_basis: { palace: "震三宫", direction: "正东方", god: "九天", star: "天冲", door: "伤门", heaven_stem: "甲", earth_stem: "己" },
    grid_cells: [
      { slot_id: "1", palace_key: "巽四宫", palace_name: "巽宫", direction: "东南", wuxing: "木", is_active: false },
      { slot_id: "2", palace_key: "离九宫", palace_name: "离宫", direction: "正南", wuxing: "火", is_active: false },
      { slot_id: "3", palace_key: "坤二宫", palace_name: "坤宫", direction: "西南", wuxing: "土", is_active: false },
      { slot_id: "4", palace_key: "震三宫", palace_name: "震宫", direction: "正东", wuxing: "木", is_active: true },
      { slot_id: "5", palace_key: "中五宫", palace_name: "中宫", direction: "中央", wuxing: "土", is_active: false },
      { slot_id: "6", palace_key: "兑七宫", palace_name: "兑宫", direction: "正西", wuxing: "金", is_active: false },
      { slot_id: "7", palace_key: "艮八宫", palace_name: "艮宫", direction: "东北", wuxing: "土", is_active: false },
      { slot_id: "8", palace_key: "坎一宫", palace_name: "坎宫", direction: "正北", wuxing: "水", is_active: false },
      { slot_id: "9", palace_key: "乾六宫", palace_name: "乾宫", direction: "西北", wuxing: "金", is_active: false }
    ],
    relations: { palace_door_relation: "门宫相生，元神安泰", stem_pair_relation: "甲己合化，暗通财库" },
    risks: { four_harms: { emptiness: "无", door_pressure: "伤门未克巽木", tomb: "无", punishment_hit: "无" }, pattern_flags: ["双星守护", "贵人福临"], risk_pairs: [], structural_cap_reasons: [] }
  },
  stability_detail: {
    verdict: "极优稳健",
    content: "本号码奇门格局稳健厚重，用神在生旺之方，求财顺达，能安家定业，万无一失。",
    elements_check: { "命宫相生": "上吉", "星扉融和": "平和利市" }
  },
  aspects: generate12Aspects(),
  aspect_unlock_points: 50,
  free_aspect_keys: ["career"],
  unlock_enforcement_enabled: true
};

// Seed wealth as unlocked for 13800138000
seedPh138.aspects[1].is_unlocked = true;
seedPh138.aspects[1].content = "生门临值符贵人。五行得正财之力，理财能力极其强悍。适合做长线的固产保值配置。";
seedPh138.aspects[1].risk = "忌盲目动用重杠杆进行高息套利，否则易见水火相克、损及本金之险。";
seedPh138.aspects[1].elements_check = { "理产业曜": "稳如泰山", "开财方位": "正南与正下方" };

phoneReviewsMock["u_13800138000"] = [ seedPh138 ];

// Seed pre-seeded phone report for 13600136000 (unlock insufficient)
const seedPh136 = {
  ...seedPh138,
  id: "seed_ph_review_136",
  report_id: "seed_rep_ph_136",
  phone: "13600136000",
  phone_number: "13600136000",
  masked_phone: "136****0000",
  aspects: generate12Aspects(), // All locked except career
};
phoneReviewsMock["u_13600136000"] = [ seedPh136 ];


function generateCompleteBaziReview(userId: string, gender: string, birth_date: string, birth_time: string, reviewId: string, reportId: string, bY: number): any {
  const now = new Date().toISOString();
  return {
    id: reviewId,
    report_id: reportId,
    name: "本命评测",
    gender: gender || "male",
    birth_date,
    birth_time,
    timezone: "Asia/Shanghai",
    birth_place: "北京",
    status: "completed",
    progress_stage: "completed",
    progress_message: "智能算运完成",
    score: 87,
    score_markdown: `八字日主【甲木】坐于申地，属于绝处逢生格局。金水清韵润燥得力，为人仁慈宽博。`,
    created_at: now,
    updated_at: now,
    chart: {
      solar_datetime: `${birth_date} ${birth_time}`,
      lunar_date: "九月初一",
      day_master: "甲申",
      day_master_element: "木"
    },
    deterministic_facts: {
      year_ganzhi: "乙亥",
      month_ganzhi: "丙戌",
      day_ganzhi: "甲申",
      hour_ganzhi: "己巳"
    },
    summary: {
      title: "四柱甲木逢食神生财格",
      risk: "木弱火旺，极易思虑过度或肝火上炎。静坐与修养是维持健康的极佳方法。",
      usage_guidance: "此局以水木为用。宜居家正北方置白水晶，岁运喜水润泽。",
      elements_check: { "身强弱": "偏弱偏燥", "格局": "食神生财格", "喜用神": "金水清韵" }
    },
    chart_display: {
      profile: {
        gender_label: gender === "female" ? "坤造" : "乾造",
        zodiac: "猪",
        solar_datetime_text: `${birth_date} ${birth_time}`,
        lunar_date: "九月初一",
        lunar_full_text: "乙亥年九月初一日 巳时",
        birth_place: "北京",
        timezone: "Asia/Shanghai",
        solar_term_context: "寒露后16天，霜降前3天"
      },
      pillars: {
        year: {
          key: "year",
          label: "年柱",
          ganzhi: "乙亥",
          stem: "乙",
          branch: "亥",
          stem_element: "木",
          branch_element: "水",
          stem_ten_god: "劫财",
          branch_ten_gods: ["偏印"],
          hidden_stems: [{ stem: "甲", element: "木", ten_god: "比肩" }],
          na_yin: "山头火",
          xun_kong: "申酉",
          di_shi: "长生",
          self_sitting: "建禄",
          shen_sha: ["太极贵人", "文昌贵人"],
          shen_sha_details: [
            { name: "太极贵人", category: "talent", basis: "日干甲见支亥", basis_value: "亥", target: "年柱", target_value: "亥", rule: "甲乙见子午", meaning: "太极星临，聪颖好学，一生易得仙缘道气及长辈荫庇。" },
            { name: "文昌贵人", category: "talent", basis: "日干甲见支巳", basis_value: "巳", target: "年柱", target_value: "巳", rule: "甲见巳", meaning: "文采斐然，逢考必过，常带清健文雅之气。" }
          ]
        },
        month: {
          key: "month",
          label: "月柱",
          ganzhi: "丙戌",
          stem: "丙",
          branch: "戌",
          stem_element: "火",
          branch_element: "土",
          stem_ten_god: "食神",
          branch_ten_gods: ["偏财"],
          hidden_stems: [{ stem: "辛", element: "金", ten_god: "正官" }],
          na_yin: "屋上土",
          xun_kong: "午未",
          di_shi: "养",
          self_sitting: "冠带",
          shen_sha: ["红艳煞", "华盖"],
          shen_sha_details: [
            { name: "红艳煞", category: "relationship", basis: "日干甲见支戌", basis_value: "戌", target: "月柱", target_value: "戌", rule: "甲乙见戌", meaning: "情愫多生，风流温雅，一生易得异性青睐。" },
            { name: "华盖", category: "spiritual", basis: "支见戌", basis_value: "戌", target: "月柱", target_value: "戌", rule: "寅午戌见戌", meaning: "艺术直觉敏锐，清高孤傲，喜玄学遁甲修行。" }
          ]
        },
        day: {
          key: "day",
          label: "日柱",
          ganzhi: "甲申",
          stem: "甲",
          branch: "申",
          stem_element: "木",
          branch_element: "金",
          stem_ten_god: "日主",
          branch_ten_gods: ["七杀"],
          hidden_stems: [{ stem: "庚", element: "金", ten_god: "七杀" }],
          na_yin: "泉中水",
          xun_kong: "午未",
          di_shi: "绝",
          self_sitting: "绝地自坐",
          shen_sha: ["天乙贵人", "驿马", "太极贵人", "华盖", "将星", "孤辰", "劫煞"],
          shen_sha_details: [
            { name: "天乙贵人", category: "support", basis: "日干甲见支申", basis_value: "申", target: "日柱", target_value: "申", rule: "甲戊庚见丑未", meaning: "至高吉星，逢凶化吉，一生常得天恩贵人扶助。" },
            { name: "驿马", category: "movement", basis: "支见申", basis_value: "申", target: "日柱", target_value: "申", rule: "申子辰见申", meaning: "奔波迁徙，多出外创业或频繁差旅，不耐久静。" },
            { name: "太极贵人", category: "talent", basis: "日干甲见支申", basis_value: "申", target: "日柱", target_value: "申", rule: "甲见申", meaning: "太极星临，聪颖好学，一生易得仙缘道气及长辈荫庇。" },
            { name: "华盖", category: "spiritual", basis: "支见申", basis_value: "申", target: "日柱", target_value: "申", rule: "华盖入命", meaning: "艺术直觉敏锐，清高孤傲，喜玄学遁甲修行。" },
            { name: "将星", category: "support", basis: "支见申", basis_value: "申", target: "日柱", target_value: "申", rule: "将星临绝", meaning: "有组织领导之才，在官场或职场中易得人望。" },
            { name: "孤辰", category: "relationship", basis: "支见申", basis_value: "申", target: "日柱", target_value: "申", rule: "孤辰临日", meaning: "性格略显孤介，内心世界丰富，喜欢独立思考。" },
            { name: "劫煞", category: "risk", basis: "支见申", basis_value: "申", target: "日柱", target_value: "申", rule: "劫煞主事", meaning: "行事宜多加严谨，防患未然，增强抗压韧性。" }
          ]
        },
        hour: {
          key: "hour",
          label: "时柱",
          ganzhi: "己巳",
          stem: "己",
          branch: "巳",
          stem_element: "土",
          branch_element: "火",
          stem_ten_god: "正财",
          branch_ten_gods: ["食神"],
          hidden_stems: [{ stem: "丙", element: "火", ten_god: "食神" }],
          na_yin: "大林木",
          xun_kong: "戌亥",
          di_shi: "病",
          self_sitting: "临官",
          shen_sha: ["天医", "禄神", "文昌", "福星贵人", "亡神", "五鬼"],
          shen_sha_details: [
            { name: "天医", category: "health", basis: "生月戌见支巳", basis_value: "巳", target: "时柱", target_value: "巳", rule: "月后一辰", meaning: "天医高照，健体强身，在医药、玄学或康养上极具天赋智觉。" },
            { name: "禄神", category: "wealth", basis: "日干甲见支寅", basis_value: "寅", target: "时柱", target_value: "巳", rule: "甲禄在寅", meaning: "财禄丰厚，岁运逢之必得衣食富足，自立门户之气。" },
            { name: "文昌", category: "talent", basis: "日干甲见支巳", basis_value: "巳", target: "时柱", target_value: "巳", rule: "文昌临官", meaning: "文采斐然，逢考必过，常带清健文雅之气。" },
            { name: "福星贵人", category: "support", basis: "日干甲见支巳", basis_value: "巳", target: "时柱", target_value: "巳", rule: "福星临门", meaning: "一生福禄无缺，安康少忧，常有贵人暗中庇护。" },
            { name: "亡神", category: "risk", basis: "支见巳", basis_value: "巳", target: "时柱", target_value: "巳", rule: "亡神临柱", meaning: "做事需深思熟虑，避免急躁，保持从容淡定之姿。" },
            { name: "五鬼", category: "risk", basis: "支见巳", basis_value: "巳", target: "时柱", target_value: "巳", rule: "五鬼惊扰", meaning: "言行宜谨慎，凡事退一步海阔天空，少惹口舌之争。" }
          ]
        }
      },
      element_status: [
        { element: "木", status: "相" },
        { element: "火", status: "旺" },
        { element: "土", status: "休" },
        { element: "金", status: "死" },
        { element: "水", status: "囚" }
      ]
    },
    natal_table: {
      pillars: [
        { key: "year", name: "年柱", stem: "乙", stem_element: "木", branch: "亥", branch_element: "水", diyin_yin_yang: "阴", stem_ten_god: "劫财", branch_main_ten_god: "偏印", sub_hidden_stems: [{ stem: "甲", element: "木", ten_god: "比肩" }], di_shi: "长生", elements_summary: "水木涵养" },
        { key: "month", name: "月柱", stem: "丙", stem_element: "火", branch: "戌", branch_element: "土", diyin_yin_yang: "阳", stem_ten_god: "食神", branch_main_ten_god: "偏财", sub_hidden_stems: [{ stem: "辛", element: "金", ten_god: "正官" }], di_shi: "养", elements_summary: "火土生发" },
        { key: "day", name: "日柱", stem: "甲", stem_element: "木", branch: "申", branch_element: "金", diyin_yin_yang: "阳", stem_ten_god: "日主", branch_main_ten_god: "七杀", sub_hidden_stems: [{ stem: "庚", element: "金", ten_god: "七杀" }], di_shi: "绝", elements_summary: "绝处逢生" },
        { key: "hour", name: "时柱", stem: "己", stem_element: "土", branch: "巳", branch_element: "火", diyin_yin_yang: "阴", stem_ten_god: "正财", branch_main_ten_god: "食神", sub_hidden_stems: [{ stem: "丙", element: "火", ten_god: "食神" }], di_shi: "病", elements_summary: "火土相融" }
      ],
      shen_sha_list: [
        { name: "天乙贵人", category: "贵人", basis: "日干甲逢支巳", basis_value: "巳", target: "时柱" },
        { name: "太极贵人", category: "学业", basis: "日干甲见支亥", basis_value: "亥", target: "年柱" }
      ],
      element_ratios: { "金": 15, "木": 25, "水": 20, "火": 20, "土": 20 }
    },
    luck_analysis: {
      enabled: true,
      cycle_points_cost: 80,
      year_points_cost: 30,
      current_cycle_key: "cycle_1",
      cycles: generateMockLuckCycles(userId, bY)
    },
    aspects: generateBaziAspects(),
    aspect_unlock_points: 50,
    free_aspect_keys: ["personality"],
    unlock_enforcement_enabled: true
  };
}

// Bazi (Four Pillars) reports list
const seedBazi138 = generateCompleteBaziReview("u_13800138000", "male", "1995-10-24", "10:30", "seed_bz_review", "seed_rep_bz_1", 1995);

baziReviewsMock["u_13800138000"] = [ seedBazi138 ];

// Seed FourPillars for 13600136000 (unlock insufficient)
const seedBazi136 = generateCompleteBaziReview("u_13600136000", "male", "1995-10-24", "10:30", "seed_bz_review_136", "seed_rep_bz_136", 1995);
seedBazi136.luck_analysis.cycles = [
  {
    cycle_key: "cycle_1",
    start_year: 2024,
    end_year: 2033,
    start_age: 29,
    end_age: 38,
    ganzhi: "己亥",
    display_ganzhi: "己亥大运",
    is_current: true,
    render_status: "not_generated", // Locked
    render: null,
    year_items: []
  }
];
// Lock career_trend / career for 136001365000:
seedBazi136.aspects[1].is_unlocked = false;
seedBazi136.aspects[1].content = null;
seedBazi136.aspects[1].risk = null;
seedBazi136.aspects[1].elements_check = {};

baziReviewsMock["u_13600136000"] = [ seedBazi136 ];


// Empty history for 13700137000 & 13900139000 & 13500135000
phoneReviewsMock["u_13700137000"] = [];
baziReviewsMock["u_13700137000"] = [];
phoneReviewsMock["u_13900139000"] = [];
baziReviewsMock["u_13900139000"] = [];
phoneReviewsMock["u_13500135000"] = [];
baziReviewsMock["u_13500135000"] = [];


// Helper to extract Bearer Token mock
function getUserIdFromToken(authHeader?: string): string | null {
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return null;
  }
  const token = authHeader.substring(7);
  // Simple check: we just map token back to user_id (the token itself can be the userId for mock purposes)
  return token;
}

// Populate default claim link
claimsLinksMock["claim_999"] = {
  claim_link_id: "claim_999",
  claim_code: "claim_999",
  title: "新客专享回归礼包",
  points_amount: 100,
  display_value_cents: 1000,
  expires_at: "2030-12-31T23:59:59Z",
  enabled: true,
  claims_count: 0,
};

// Global public almanac config
const almanacFallback = {
  solar_date: new Date().toISOString().split('T')[0],
  display_date: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }),
  weekday_label: new Date().toLocaleDateString('zh-CN', { weekday: 'long' }),
  lunar_date: "五月廿四",
  lunar_full_text: "阴历 丙午年 五月廿四日",
  ganzhi_year: "丙午",
  ganzhi_month: "甲午",
  ganzhi_day: "庚辰",
  zodiac_year: "马",
  zodiac_month: "马",
  zodiac_day: "龙",
  yi: ["求嗣", "嫁娶", "纳采", "出行", "开市", "合帐", "安床"],
  ji: ["作灶", "修坟", "掘井", "动土", "破土"],
  yi_summary: "宜求嗣、嫁娶等吉事",
  ji_summary: "忌破土、作灶等事务",
  solar_term: "夏至",
  festivals: [],
  pengzu_gan: "庚不经络织机虚",
  pengzu_zhi: "辰不哭泣必主重丧",
  pengzu_summary: "庚不经络，辰不哭泣",
  chong: "狗",
  sha: "南",
  zhi_xing: "建",
  tian_shen: "金匮",
  tian_shen_luck: "黄道吉日",
  ji_shen: ["官日", "六合", "五合", "鸣吠"],
  xiong_sha: ["大时", "大败", "咸池", "小耗"]
};

// Global pricing packages
const rechargePackages = [
  { package_key: 'pkg_10', title: '10积分优惠包', points_amount: 10, price_cents: 600, display_price: "¥6.00" },
  { package_key: 'pkg_50', title: '50积分超值包', points_amount: 50, price_cents: 2500, display_price: "¥25.00" },
  { package_key: 'pkg_100', title: '100积分尊享包', points_amount: 100, price_cents: 4500, display_price: "¥45.00" },
  { package_key: 'pkg_500', title: '500积分财富商海包', points_amount: 500, price_cents: 19800, display_price: "¥198.00" },
];

// --- API ROTUES FIRST ---

// Public configurations
app.get("/api/v1/runtime-config/public", (req, res) => {
  res.json({
    modules: {
      phone_review: {
        base_points_cost: 100,
        aspect_unlock_points_cost: 50,
        unlock_enforcement_enabled: true,
      },
      four_pillars: {
        base_points_cost: 100,
        aspect_unlock_points_cost: 50,
        luck_cycle_points_cost: 80,
        luck_year_points_cost: 30,
        unlock_enforcement_enabled: true,
      }
    },
    customer_service: {
      wechat_id: "easewise_support",
      contact_url: "",
      qr_code_url: "https://images.unsplash.com/photo-1543269865-cbf427effbad?auto=format&fit=crop&w=350&q=80",
      guidance_text: "长按扫码或复制微信号添加客服专属微信群，我们将竭诚为您服务。",
      qr_guidance_text: "截图或长按保存二维码，微信扫一扫添加客服。",
      copy_button_text: "复制微信号",
      unconfigured_text: "客服尚未配置，请联系管理员。",
      copy: {
        default: "添加官方客服微信号 easewise_support 获取人工专属服务。",
        recharge_help: "购买充值遇到阻碍？请添加客服微信号加速通道人工开项。",
        payment_issue: "如遇付款未到账或账单有误，请即刻联系客服处理。",
        points_insufficient: "积分不够？联系客服咨询本周免费积分赠送优惠券！"
      }
    }
  });
});

app.get("/api/v1/almanac/today", (req, res) => {
  res.json(almanacFallback);
});

// Auth phone status
app.post("/api/v1/auth/phone/status", (req, res) => {
  const { phone } = req.body;
  if (!phone) {
    return res.status(400).json({ detail: "invalid_phone_number" });
  }
  const isRegistered = Boolean(usersMock[phone]);
  res.json({ status: isRegistered ? "registered" : "not_registered" });
});

// Auth phone register
app.post("/api/v1/auth/phone/register", (req, res) => {
  const { phone, password, confirm_password } = req.body;
  if (!phone || String(phone).length !== 11) {
    return res.status(400).json({ detail: "invalid_phone_number" });
  }
  if (!password || password.length < 6) {
    return res.status(400).json({ detail: "password_too_weak" });
  }
  if (password !== confirm_password) {
    return res.status(400).json({ detail: "password_confirm_mismatch" });
  }
  if (usersMock[phone]) {
    return res.status(400).json({ detail: "phone_already_registered" });
  }

  const userId = `u_${phone}`;
  const now = new Date().toISOString();
  
  usersMock[phone] = {
    user_id: userId,
    uid: userId,
    status: 'active',
    identity_level: 'standard',
    nickname: `易友_${phone.slice(-4)}`,
    avatar_url: null,
    profile_completed: false,
    created_at: now,
    updated_at: now,
    last_active_at: now,
    password: password // In mock we keep it simple
  };

  pointsMock[userId] = {
    balance: 50, // Register gives 50 free credits!
    frozen_balance: 0,
    created_at: now,
    updated_at: now
  };

  pointsLedgerMock[userId] = [
    {
      ledger_id: `led_init_${userId}`,
      change_type: "add",
      delta: 50,
      balance_after: 50,
      biz_type: "register_bonus",
      biz_id: "signup",
      idempotency_key: null,
      remark: "注册赠送体验积分",
      created_at: now
    }
  ];

  res.json({
    access_token: userId,
    token_type: "Bearer",
    user: usersMock[phone],
    points: pointsMock[userId]
  });
});

// Auth phone login
app.post("/api/v1/auth/phone/login", (req, res) => {
  const { phone, password } = req.body;
  if (!phone || !password) {
    return res.status(400).json({ detail: "invalid_phone_or_password" });
  }
  const user = usersMock[phone];
  if (!user || user.password !== password) {
    return res.status(401).json({ detail: "invalid_phone_or_password" });
  }

  res.json({
    access_token: user.user_id,
    token_type: "Bearer",
    user,
    points: pointsMock[user.user_id]
  });
});

// Logout
app.post("/api/v1/auth/logout", (req, res) => {
  res.json({ status: "success" });
});

// My Account details
app.get("/api/v1/account/me", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  // Find user by looking into values
  const user = Object.values(usersMock).find((u: any) => u.user_id === userId);
  if (!user) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  res.json({
    user,
    points: pointsMock[userId] || { balance: 0, frozen_balance: 0 }
  });
});

// Points Account
app.get("/api/v1/account/points", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  res.json(pointsMock[userId] || { balance: 0, frozen_balance: 0, created_at: null, updated_at: null });
});

// Points Ledger List
app.get("/api/v1/account/points/ledger", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  res.json({
    items: pointsLedgerMock[userId] || [],
    total: (pointsLedgerMock[userId] || []).length
  });
});

// Update Profile
app.patch("/api/v1/account/profile", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  const user = Object.values(usersMock).find((u: any) => u.user_id === userId);
  if (!user) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  const { nickname, avatar_url } = req.body;
  if (nickname !== undefined) user.nickname = nickname;
  if (avatar_url !== undefined) user.avatar_url = avatar_url;
  user.updated_at = new Date().toISOString();

  res.json(user);
});

// Avatar Upload
app.post("/api/v1/account/avatar", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  const user = Object.values(usersMock).find((u: any) => u.user_id === userId);
  if (!user) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  const { image_data_url } = req.body;
  if (image_data_url) {
    user.avatar_url = image_data_url;
  }
  user.updated_at = new Date().toISOString();
  res.json(user);
});

// Change Password
app.post("/api/v1/account/password/change", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  const user = Object.values(usersMock).find((u: any) => u.user_id === userId);
  if (!user) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  const { current_password, new_password, confirm_password } = req.body;
  if (user.password !== current_password) {
    return res.status(400).json({ detail: "invalid_current_password" });
  }
  if (new_password !== confirm_password) {
    return res.status(400).json({ detail: "password_confirm_mismatch" });
  }
  user.password = new_password;
  user.updated_at = new Date().toISOString();
  res.json({ status: "success", detail: "密码更新成功" });
});

// Points claims codes (Claim public codes)
app.get("/api/v1/points-claims/:claimCode", (req, res) => {
  const { claimCode } = req.params;
  const claim = claimsLinksMock[claimCode];
  if (!claim) {
    return res.status(404).json({ detail: "claim_link_not_found" });
  }
  res.json(claim);
});

app.post("/api/v1/points-claims/:claimCode/claim", (req, res) => {
  const { claimCode } = req.params;
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const claim = claimsLinksMock[claimCode];
  if (!claim) {
    return res.status(404).json({ detail: "claim_link_not_found" });
  }
  if (!claim.enabled) {
    return res.status(400).json({ detail: "claim_link_disabled" });
  }

  // Double check if already claimed (simple ledger check)
  const ledger = pointsLedgerMock[userId] || [];
  const claimedBefore = ledger.some(item => item.biz_id === claimCode);
  if (claimedBefore) {
    return res.status(400).json({ detail: "already_claimed_this_week" });
  }

  // Adjust points
  if (!pointsMock[userId]) {
    pointsMock[userId] = { balance: 0, frozen_balance: 0 };
  }
  pointsMock[userId].balance += claim.points_amount;
  pointsMock[userId].updated_at = new Date().toISOString();

  // Logging addition
  const ledId = `led_${claimCode}_${Date.now()}`;
  pointsLedgerMock[userId].unshift({
    ledger_id: ledId,
    change_type: "add",
    delta: claim.points_amount,
    balance_after: pointsMock[userId].balance,
    biz_type: "public_claim",
    biz_id: claimCode,
    idempotency_key: null,
    remark: `免费码领取：${claim.title}`,
    created_at: new Date().toISOString()
  });

  claim.claims_count += 1;

  res.json({
    status: "success",
    points_amount: claim.points_amount,
    points: pointsMock[userId]
  });
});

// Billing Recharge Packages
app.get("/api/v1/billing/recharge-packages", (req, res) => {
  res.json({ items: rechargePackages });
});

// Billing Recharge Create Order
app.post("/api/v1/billing/recharge-orders", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "session_not_found" });
  }
  const { package_key, proof_url, remark } = req.body;
  const pkg = rechargePackages.find(p => p.package_key === package_key);
  if (!pkg) {
    return res.status(400).json({ detail: "package_not_found" });
  }

  const orderId = `ord_rec_${package_key}_${Date.now()}`;
  const now = new Date().toISOString();

  const newOrder = {
    id: orderId,
    order_id: orderId,
    package_key: pkg.package_key,
    package_title: pkg.title,
    points_amount: pkg.points_amount,
    amount_cents: pkg.price_cents,
    price_cents: pkg.price_cents,
    status: proof_url ? "reviewing" : "pending", // If proof given, starts as reviewing!
    proof_url: proof_url || null,
    remark: remark || null,
    created_at: now,
    updated_at: now,
    payment_method: "offline_upload",
    transaction_id: null
  };

  rechargeOrdersMock[orderId] = newOrder;

  res.json(newOrder);
});

// Billing get order
app.get("/api/v1/billing/recharge-orders/:orderId", (req, res) => {
  const { orderId } = req.params;
  const order = rechargeOrdersMock[orderId];
  if (!order) {
    return res.status(404).json({ detail: "order_not_found" });
  }
  res.json(order);
});

// Billing order pay triggers (offline mock success fallback)
app.post("/api/v1/billing/recharge-orders/:orderId/payments", (req, res) => {
  const { orderId } = req.params;
  const order = rechargeOrdersMock[orderId];
  if (!order) {
    return res.status(404).json({ detail: "order_not_found" });
  }
  const { proof_url } = req.body;
  if (proof_url) {
    order.proof_url = proof_url;
    order.status = "reviewing";
    order.updated_at = new Date().toISOString();
  } else {
    // If we trigger WeChat H5 directly we mock complete it right away!
    order.status = "completed";
    order.updated_at = new Date().toISOString();

    const userId = getUserIdFromToken(req.headers.authorization);
    if (userId) {
      if (!pointsMock[userId]) pointsMock[userId] = { balance: 0, frozen_balance: 0 };
      pointsMock[userId].balance += order.points_amount;
      
      pointsLedgerMock[userId].unshift({
        ledger_id: `led_pay_${orderId}`,
        change_type: "add",
        delta: order.points_amount,
        balance_after: pointsMock[userId].balance,
        biz_type: "recharge",
        biz_id: orderId,
        idempotency_key: null,
        remark: `积分包充值: ${order.package_title}`,
        created_at: new Date().toISOString()
      });
    }
  }

  res.json({
    status: order.status,
    redirect_url: null,
    qr_code_url: "https://images.unsplash.com/photo-1543269865-cbf427effbad?auto=format&fit=crop&w=300&q=80",
    order
  });
});

// Billing order status
app.get("/api/v1/billing/recharge-orders/:orderId/payment-status", (req, res) => {
  const { orderId } = req.params;
  const order = rechargeOrdersMock[orderId];
  if (!order) {
    return res.status(404).json({ detail: "order_not_found" });
  }
  res.json({ status: order.status, is_paid: order.status === "completed" });
});

// --- Phone Qimen Reviews ---
app.post("/api/v1/phone-qimen/reviews", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const { phone, gender } = req.body;
  if (!phone || String(phone).length !== 11) {
    return res.status(400).json({ detail: "invalid_phone_number" });
  }

  // Deduct Points
  const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
  const cost = 100; // Phone review cost 100 points
  if (userPoints.balance < cost) {
    return res.status(402).json({ detail: "insufficient_points" });
  }

  userPoints.balance -= cost;
  userPoints.updated_at = new Date().toISOString();

  const reviewId = `rev_ph_${phone}_${Date.now()}`;
  const reportId = `rep_ph_${Date.now()}`;
  const now = new Date().toISOString();

  // Deduct points logger addition
  pointsLedgerMock[userId].unshift({
    ledger_id: `led_ph_rev_${reviewId}`,
    change_type: "deduct",
    delta: -cost,
    balance_after: userPoints.balance,
    biz_type: "phone_review",
    biz_id: reviewId,
    idempotency_key: null,
    remark: `手机评测扣：${phone}`,
    created_at: now
  });

  // Structural Qimen board template
  const review: any = {
    id: reviewId,
    report_id: reportId,
    phone: phone,
    phone_number: phone,
    masked_phone: `${phone.substring(0, 3)}****${phone.substring(7)}`,
    gender: gender || "male",
    status: "completed",
    progress_stage: "completed",
    progress_message: "智能推论完成",
    score: 83,
    score_markdown: `*该号码的奇门局蕴藏【值符落震宫】，代表做事干脆爽快，适合科技与金融。*`,
    error_message: null,
    created_at: now,
    updated_at: now,
    phone_summary: {
      title: "震木长生格局",
      risk: "极低",
      usage_guidance: "适合多作为个人事务电话或高管联系，利于开展开拓性工作。",
      elements_check: {
        "卦德": "雷厉风行",
        "生克": "五行相生，互不侵扰"
      }
    },
    board: {
      center_basis: { trigger: "九天震宫" },
      active_basis: {
        palace: "震三宫",
        direction: "正东方",
        god: "九天",
        star: "天冲",
        door: "伤门",
        heaven_stem: "甲",
        earth_stem: "己"
      },
      grid_cells: [
        { slot_id: "1", palace_key: "巽四宫", palace_name: "巽宫", direction: "东南", wuxing: "木", is_active: false },
        { slot_id: "2", palace_key: "离九宫", palace_name: "离宫", direction: "正南", wuxing: "火", is_active: false },
        { slot_id: "3", palace_key: "坤二宫", palace_name: "坤宫", direction: "西南", wuxing: "土", is_active: false },
        { slot_id: "4", palace_key: "震三宫", palace_name: "震宫", direction: "正东", wuxing: "木", is_active: true },
        { slot_id: "5", palace_key: "中五宫", palace_name: "中宫", direction: "中央", wuxing: "土", is_active: false },
        { slot_id: "6", palace_key: "兑七宫", palace_name: "兑宫", direction: "正西", wuxing: "金", is_active: false },
        { slot_id: "7", palace_key: "艮八宫", palace_name: "艮宫", direction: "东北", wuxing: "土", is_active: false },
        { slot_id: "8", palace_key: "坎一宫", palace_name: "坎宫", direction: "正北", wuxing: "水", is_active: false },
        { slot_id: "9", palace_key: "乾六宫", palace_name: "乾宫", direction: "西北", wuxing: "金", is_active: false }
      ],
      relations: {
        palace_door_relation: "门宫相生，元气通融",
        stem_pair_relation: "甲己合化，贵人辅佐"
      },
      risks: {
        four_harms: {
          emptiness: "无",
          door_pressure: "伤门未克巽宫",
          tomb: "无",
          punishment_hit: "无"
        },
        pattern_flags: ["甲己合化", "九天飞腾"],
        risk_pairs: [],
        structural_cap_reasons: []
      }
    },
    stability_detail: {
      verdict: "极高",
      content: "大局主气运不衰，用神坚韧而无克，求财交易及事业合作稳如泰山。",
      elements_check: {
        "主次气运": "中正平稳",
        "岁运相交": "平和顺达"
      }
    },
    aspects: generate12Aspects(),
    aspect_unlock_points: 50,
    free_aspect_keys: ["career"],
    unlock_enforcement_enabled: true
  };

  if (!phoneReviewsMock[userId]) {
    phoneReviewsMock[userId] = [];
  }
  phoneReviewsMock[userId].unshift(review);

  res.json(review);
});

app.get("/api/v1/phone-qimen/reviews", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const items = phoneReviewsMock[userId] || [];
  res.json({
    items: items.map(r => ({
      id: r.id,
      report_id: r.report_id,
      phone: r.phone,
      phone_number: r.phone_number,
      masked_phone: r.masked_phone,
      gender: r.gender,
      status: r.status,
      progress_stage: r.progress_stage,
      progress_message: r.progress_message,
      score: r.score,
      error_message: r.error_message,
      created_at: r.created_at,
      updated_at: r.updated_at
    })),
    total: items.length,
    limit: 20,
    offset: 0
  });
});

app.get("/api/v1/phone-qimen/reviews/:reviewId", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const reviews = phoneReviewsMock[userId] || [];
  const review = reviews.find(r => r.id === req.params.reviewId);
  if (!review) {
    return res.status(404).json({ detail: "review_not_found" });
  }
  res.json(review);
});

app.post("/api/v1/phone-qimen/reviews/:reviewId/aspect-unlocks", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const reviews = phoneReviewsMock[userId] || [];
  const review = reviews.find(r => r.id === req.params.reviewId);
  if (!review) {
    return res.status(404).json({ detail: "review_not_found" });
  }

  const { aspect_key } = req.body;
  const aspect = review.aspects.find((a: any) => a.aspect_key === aspect_key);
  if (!aspect) {
    return res.status(404).json({ detail: "aspect_not_found" });
  }
  if (aspect.is_unlocked) {
    return res.json({ points: pointsMock[userId], detail: "aspect_already_unlocked" });
  }

  // Deduct Points
  const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
  const cost = 50; // Aspect costs 50 points
  if (userPoints.balance < cost) {
    return res.status(402).json({ detail: "insufficient_points" });
  }

  userPoints.balance -= cost;
  userPoints.updated_at = new Date().toISOString();

  // Update Aspect
  aspect.is_unlocked = true;
  if (aspect_key === "wealth" || aspect_key === "finance") {
    aspect.content = "金匮财气加临。命中正财、偏财双曜交相，主财富厚重平缓，理财得法可得长久之财。";
    aspect.risk = "防范秋季岁运偏激而冲克财库，切莫动用重资盲目进行高风险金融投机。";
    aspect.elements_check = { "吉利方位": "正西方", "贵人色彩": "浅黄、褐土色" };
  } else if (aspect_key === "love") {
    aspect.content = "桃花星长生在震，人缘奇佳。情感世界多姿多彩，婚后能互敬互助，白头偕老。";
    aspect.risk = "注意外部口舌与风言风语，遇事多沟通，给彼此足够的私密信任空间。";
    aspect.elements_check = { "宜合属相": "属马、属狗", "和合色泽": "正绿、粉红" };
  } else {
    aspect.content = `【吉星高照】${aspect.title}正在呈现吉利格局。运势在未来的岁运流转中呈高开高走之势。`;
    aspect.risk = "注意保持心境淡然平和，凡事三思而行、稳中求进。";
    aspect.elements_check = { "守护吉星": "天乙贵人", "助运配饰": "青金石、檀香手串" };
  }

  pointsLedgerMock[userId].unshift({
    ledger_id: `led_unl_${review.id}_${aspect_key}`,
    change_type: "deduct",
    delta: -cost,
    balance_after: userPoints.balance,
    biz_type: "aspect_unlock",
    biz_id: review.id,
    idempotency_key: null,
    remark: `解锁评测细项「${aspect.title}」`,
    created_at: new Date().toISOString()
  });

  res.json({
    points: userPoints,
    detail: "aspect_unlocked_successfully"
  });
});

// --- Four Pillars (Bazi) Reviews ---
app.post("/api/v1/four-pillars/reviews", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const { birth_date, birth_time, gender } = req.body;
  if (!birth_date || !birth_time) {
    return res.status(400).json({ detail: "invalid_birth_datetime" });
  }

  // Deduct credits
  const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
  const cost = 100; // Bazi costs 100 points
  if (userPoints.balance < cost) {
    return res.status(402).json({ detail: "insufficient_points" });
  }

  userPoints.balance -= cost;
  userPoints.updated_at = new Date().toISOString();

  const reviewId = `rev_bz_${Date.now()}`;
  const reportId = `rep_bz_${Date.now()}`;
  const now = new Date().toISOString();

  // Deduct points logger addition
  pointsLedgerMock[userId].unshift({
    ledger_id: `led_bz_rev_${reviewId}`,
    change_type: "deduct",
    delta: -cost,
    balance_after: userPoints.balance,
    biz_type: "four_pillars_review",
    biz_id: reviewId,
    idempotency_key: null,
    remark: `四柱八字评测：${birth_date} ${birth_time}`,
    created_at: now
  });

  const bY = birth_date ? Number(birth_date.split("-")[0]) : 1995;
  const baziReview = generateCompleteBaziReview(userId, gender, birth_date, birth_time, reviewId, reportId, bY);

  if (!baziReviewsMock[userId]) {
    baziReviewsMock[userId] = [];
  }
  baziReviewsMock[userId].unshift(baziReview);

  res.json(baziReview);
});

app.get("/api/v1/four-pillars/reviews", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const items = baziReviewsMock[userId] || [];
  res.json({
    items: items.map(r => ({
      id: r.id,
      report_id: r.report_id,
      gender: r.gender,
      birth_date: r.birth_date,
      birth_time: r.birth_time,
      timezone: r.timezone,
      status: r.status,
      score: r.score,
      created_at: r.created_at,
      updated_at: r.updated_at
    })),
    total: items.length,
    limit: 20,
    offset: 0
  });
});

app.get("/api/v1/four-pillars/reviews/:reviewId", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const reviews = baziReviewsMock[userId] || [];
  const review = reviews.find(r => r.id === req.params.reviewId);
  if (!review) {
    return res.status(404).json({ detail: "review_not_found" });
  }
  res.json(review);
});

app.post("/api/v1/four-pillars/reviews/:reviewId/aspect-unlocks", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const reviews = baziReviewsMock[userId] || [];
  const review = reviews.find(r => r.id === req.params.reviewId);
  if (!review) {
    return res.status(404).json({ detail: "review_not_found" });
  }

  const { aspect_key } = req.body;
  const aspect = review.aspects.find((a: any) => a.aspect_key === aspect_key);
  if (!aspect) {
    return res.status(404).json({ detail: "aspect_not_found" });
  }
  if (aspect.is_unlocked) {
    return res.json({ points: pointsMock[userId], detail: "aspect_already_unlocked" });
  }

  // Deduct Points
  const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
  const cost = 50; // Bazi aspect costs 50 points
  if (userPoints.balance < cost) {
    return res.status(402).json({ detail: "insufficient_points" });
  }

  userPoints.balance -= cost;
  userPoints.updated_at = new Date().toISOString();

  // Unlock Bazi aspect
  aspect.is_unlocked = true;
  if (aspect_key === "career_trend" || aspect_key === "career") {
    aspect.score = 88;
    aspect.content = "甲己合化，财官齐来。天干透比劫助运，最适合从事金融、互联网或自由职业咨询商。";
    aspect.risk = "唯独忌讳合化过度，反而容易陷入人合心不合的被动合作局面。";
    aspect.elements_check = { "事业贵人": "属猪与属龙者", "最佳财方": "正南与东南方" };
  } else if (aspect_key === "wealth_capacity" || aspect_key === "wealth") {
    aspect.score = 84;
    aspect.content = "食神生正财格局。命中带财库，偏财运弱但正财福德极其高，中年后积蓄颇丰。";
    aspect.risk = "中年前开销偏大，宜尽早做稳固保值的房产或重资产配置。";
    aspect.elements_check = { "财气积蓄": "佳", "调养偏方": "常佩戴黑白冷玉色系" };
  } else {
    aspect.score = 80 + Math.floor(Math.random() * 15);
    aspect.content = `【吉相加临】该八字于${aspect.title}一象气流顺畅。逢生扶之流年岁运，势必能得遇良机。`;
    aspect.risk = "应静心内省，注意平稳心态，凡事莫作极端激进行止。";
    aspect.elements_check = { "岁运喜神": "金水清韵", "运势提振": "居家正北方置白水晶球" };
  }

  pointsLedgerMock[userId].unshift({
    ledger_id: `led_unl_bz_${review.id}_${aspect_key}`,
    change_type: "deduct",
    delta: -cost,
    balance_after: userPoints.balance,
    biz_type: "aspect_unlock",
    biz_id: review.id,
    idempotency_key: null,
    remark: `解锁八字评测细项「${aspect.title}」`,
    created_at: new Date().toISOString()
  });

  res.json({
    points: userPoints,
    detail: "aspect_unlocked_successfully"
  });
});

app.get("/api/v1/four-pillars/reviews/:reviewId/luck-cycles", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const reviews = baziReviewsMock[userId] || [];
  const review = reviews.find(r => r.id === req.params.reviewId);
  if (!review) {
    return res.status(404).json({ detail: "review_not_found" });
  }
  res.json({ luck_analysis: review.luck_analysis });
});

// Create/Get Cycle Luck summary (Unlock cycle description)
app.all("/api/v1/four-pillars/reviews/:reviewId/luck-cycles/:cycleKey/summary", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const reviews = baziReviewsMock[userId] || [];
  const review = reviews.find(r => r.id === req.params.reviewId);
  if (!review) {
    return res.status(404).json({ detail: "review_not_found" });
  }

  const { cycleKey } = req.params;
  const cycle = review.luck_analysis.cycles.find((c: any) => c.cycle_key === cycleKey || c.key === cycleKey);
  if (!cycle) {
    return res.status(404).json({ detail: "luck_cycle_not_found" });
  }

  // If already rendered, just return it
  if (cycle.render_status === "completed" && cycle.render) {
    return res.json(cycle.render);
  }

  const isPost = req.method === "POST";
  const cost = 80; // Decennial costs 80 points

  // Point check if we are performing a deduction (POST)
  if (isPost) {
    const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
    if (userPoints.balance < cost) {
      return res.status(402).json({ detail: "insufficient_points" });
    }
    userPoints.balance -= cost;
    userPoints.updated_at = new Date().toISOString();

    pointsLedgerMock[userId].unshift({
      ledger_id: `led_bz_Luck_${review.id}_${cycleKey}`,
      change_type: "deduct",
      delta: -cost,
      balance_after: userPoints.balance,
      biz_type: "aspect_unlock",
      biz_id: review.id,
      idempotency_key: null,
      remark: `解锁大运气运大势分析：${cycle.title || cycleKey}`,
      created_at: new Date().toISOString()
    });
  } else {
    // For GET, check if they can afford it if not unlocked
    const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
    if (userPoints.balance < cost) {
      return res.status(402).json({ detail: "insufficient_points" });
    }
  }

  cycle.render_status = "completed";
  const renderRecord: any = {
    id: `render_${cycleKey}_${Date.now()}`,
    render_id: `render_${cycleKey}`,
    review_id: review.id,
    user_id: userId,
    render_type: "dayun",
    cycle_key: cycleKey,
    year: null,
    status: "completed",
    progress_stage: "completed",
    progress_message: "智能算运完成",
    facts: null,
    result: mockCycleRenderResult(cycleKey, cycle.ganzhi || "己亥"),
    points_cost: cost,
    error_message: null,
    retry_count: 0,
    last_attempt_at: new Date().toISOString(),
    next_retry_available_at: null,
    is_retryable: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  cycle.render = renderRecord;

  res.json(renderRecord);
});

// Create/Get Annual Luck summary (Unlock annual description)
app.all("/api/v1/four-pillars/reviews/:reviewId/luck-cycles/:cycleKey/years/:year", (req, res) => {
  const userId = getUserIdFromToken(req.headers.authorization);
  if (!userId) {
    return res.status(401).json({ detail: "registered_user_required" });
  }
  const reviews = baziReviewsMock[userId] || [];
  const review = reviews.find(r => r.id === req.params.reviewId);
  if (!review) {
    return res.status(404).json({ detail: "review_not_found" });
  }

  const { cycleKey, year } = req.params;
  const cycle = review.luck_analysis.cycles.find((c: any) => c.cycle_key === cycleKey || c.key === cycleKey);
  if (!cycle) {
    return res.status(404).json({ detail: "luck_cycle_not_found" });
  }

  const yearNum = Number(year);
  const yearItem = cycle.year_items ? cycle.year_items.find((y: any) => y.year === yearNum) : null;

  // If already rendered, just return it
  if (yearItem && yearItem.render_status === "completed" && yearItem.render) {
    return res.json(yearItem.render);
  }

  const isPost = req.method === "POST";
  const cost = 30; // Annual costs 30 points

  if (isPost) {
    const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
    if (userPoints.balance < cost) {
      return res.status(402).json({ detail: "insufficient_points" });
    }
    userPoints.balance -= cost;
    userPoints.updated_at = new Date().toISOString();

    pointsLedgerMock[userId].unshift({
      ledger_id: `led_bz_year_${review.id}_${year}`,
      change_type: "deduct",
      delta: -cost,
      balance_after: userPoints.balance,
      biz_type: "aspect_unlock",
      biz_id: review.id,
      idempotency_key: null,
      remark: `锁定流年流岁：${year}流位析`,
      created_at: new Date().toISOString()
    });
  } else {
    const userPoints = pointsMock[userId] || { balance: 0, frozen_balance: 0 };
    if (userPoints.balance < cost) {
      return res.status(402).json({ detail: "insufficient_points" });
    }
  }

  const renderRecord: any = {
    id: `render_${cycleKey}_${year}_${Date.now()}`,
    render_id: `render_${cycleKey}_${year}`,
    review_id: review.id,
    user_id: userId,
    render_type: "liunian",
    cycle_key: cycleKey,
    year: yearNum,
    status: "completed",
    progress_stage: "completed",
    progress_message: "流年推算完成",
    facts: null,
    result: mockYearRenderResult(yearNum, cycleKey),
    points_cost: cost,
    error_message: null,
    retry_count: 0,
    last_attempt_at: new Date().toISOString(),
    next_retry_available_at: null,
    is_retryable: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  if (yearItem) {
    yearItem.render_status = "completed";
    yearItem.render = renderRecord;
  }

  res.json(renderRecord);
});

// --- Simple mock voice narrations ---
app.post("/api/v1/voice/narrations", (req, res) => {
  res.json({
    voice_url: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    status: "completed"
  });
});

// --- REAL SERVER-SIDE GEMINI API FOR CHAT ---
app.post("/api/v1/agent/chat", async (req, res) => {
  const { message, history } = req.body;
  if (!message) {
    return res.status(400).json({ detail: "No message provided" });
  }

  try {
    if (ai) {
      // Structure instructions for metaphysics Q&A assistant
      const systemInstruction = `你是一位精通中国传统术数、奇门遁甲、周易黄历与四柱八字的专业玄学学术导师，名为「易如反掌人工智能助手」。
你的回答风格要古雅温和、条理清晰，既体现术数学的严谨逻辑，又带着关怀人生的温度。
请遵照以下守则解答易友问题：
1. 始终使用客观、理性、古韵的语气，不可夸大恐吓，也不要给人宿命论的感觉；
2. 如果易友询问每日运势，可用黄历常识解释；如果是手机号码测试，你可以说明在奇门中如何用宫位五行推论其生克；如果是八字，可讲述十神、长生克泄之理；
3. 输出内容请适当使用 Markdown 排版，方便移动端浏览，字数控制在300字以内最佳。`;

      // Build chat conversation sequence matching new SDK parameters
      // Group history into correct parts format
      const contentsList: any[] = [];
      
      if (history && Array.isArray(history)) {
        history.forEach((h: any) => {
          contentsList.push({
            role: h.role === 'user' ? 'user' : 'model',
            parts: [{ text: h.content }]
          });
        });
      }
      
      // Append latest message
      contentsList.push({
        role: 'user',
        parts: [{ text: message }]
      });

      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: contentsList,
        config: {
          systemInstruction,
          temperature: 0.85,
        }
      });

      const text = response.text || "吾刚才掐指一算，神机暂闭，请稍后再咨询。";
      res.json({ reply: text });
    } else {
      // Fallback response if GEMINI_API_KEY is not configured
      const fallbackMsgs = [
        "易友安好。此问题若从奇门飞盘推之，用神逢生旺，正财、事业皆蓄势待发。但切忌急功近利，防守重于进攻。",
        "玄机妙算，天干甲己相合。当前大局清澈，最适合静下心来专注于内心追求。稍安勿躁，心诚则灵。",
        "此命盘偏燥，喜水调候。凡事多思则神伤，建议多接触大自然。立秋之后，必定否极泰来。",
        "奇门震宫主雷，阳气萌动，虽有些微竞争和烦乱之音，但终究九天照拂，拨云见日，并无大碍。"
      ];
      const randomMsg = fallbackMsgs[Math.floor(Math.random() * fallbackMsgs.length)];
      res.json({ reply: `【体验模式答复】\n\n${randomMsg}\n\n*提示：若在“Settings - Secrets”中配置您的 GEMINI_API_KEY，即可开启流畅无限的 AI 实时命理诊断服务。*` });
    }
  } catch (err: any) {
    console.error("Gemini API Error details:", err);
    res.status(500).json({ detail: err.message || "Gemini execution failed" });
  }
});


// --- VITE MIDDLEWARE SETUP ---
async function startServer() {
  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Express custom server running on http://localhost:${PORT}`);
  });
}

startServer();
