export interface MockLocation {
  id: string;
  name: string;
  pinyin?: string;
  timezone?: string;
}

export const MOCK_LOCATIONS: MockLocation[] = [
  { id: "cn-110101", name: "北京市东城区", pinyin: "Beijing Dongcheng", timezone: "Asia/Shanghai" },
  { id: "cn-310101", name: "上海市黄浦区", pinyin: "Shanghai Huangpu", timezone: "Asia/Shanghai" },
  { id: "cn-440106", name: "广东省广州市天河区", pinyin: "Guangzhou Tianhe", timezone: "Asia/Shanghai" },
  { id: "cn-440304", name: "广东省深圳市福田区", pinyin: "Shenzhen Futian", timezone: "Asia/Shanghai" },
  { id: "cn-330102", name: "浙江省杭州市上城区", pinyin: "Hangzhou Shangcheng", timezone: "Asia/Shanghai" },
  { id: "cn-320102", name: "江苏省南京市玄武区", pinyin: "Nanjing Xuanwu", timezone: "Asia/Shanghai" },
  { id: "cn-510104", name: "四川省成都市锦江区", pinyin: "Chengdu Jinjiang", timezone: "Asia/Shanghai" },
  { id: "cn-420102", name: "湖北省武汉市江岸区", pinyin: "Wuhan Jiangan", timezone: "Asia/Shanghai" }
];
