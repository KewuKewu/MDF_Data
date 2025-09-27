import json
import glob

# 自动读取所有批次的 json 文件
batch_files = sorted(glob.glob("allCards_ai_batch_*.json"), key=lambda x: int(x.split('_')[-1].split('.')[0]))

all_cards = []
for file in batch_files:
    with open(file, "r", encoding="utf-8") as f:
        try:
            batch_cards = json.load(f)
            # 如果是数组，直接扩展
            if isinstance(batch_cards, list):
                all_cards.extend(batch_cards)
            # 如果是字符串（AI返回的JSON字符串），先解析
            elif isinstance(batch_cards, str):
                all_cards.extend(json.loads(batch_cards))
        except Exception as e:
            print(f"{file} 解析失败：{e}")

# 保存合并后的json
with open("allCards_merged.json", "w", encoding="utf-8") as f:
    json.dump(all_cards, f, ensure_ascii=False, indent=4)

# 可选：生成txt文本
lines = []
for card in all_cards:
    lines.append(f"卡牌名称：{card.get('card_name', '')}")
    lines.append(f"稀有度：{card.get('rarity', '')}")
    lines.append(f"卡牌ID：{card.get('card_id', '')}")
    lines.append(f"画师：{card.get('artist', '')}")
    lines.append(f"获得方式：{card.get('obtain', '')}")
    lines.append(f"卡牌类型：{card.get('card_type', '')}")

    card_type = card.get('card_type', '')
    if card_type == "角色卡":
        lines.append(f"CENTER：{card.get('center', '')}")
        lines.append(f"HYPER：{card.get('hyper', '')}")
        lines.append(f"SUPPORT：{card.get('support', '')}")
    else:
        def only_tag(text):
            if not text:
                return ""
            return text.split(" ")[0]
        lines.append(f"CENTER：{only_tag(card.get('center', ''))}")
        lines.append(f"HYPER：{only_tag(card.get('hyper', ''))}")
        lines.append(f"SUPPORT：{only_tag(card.get('support', ''))}")

    lines.append(f"华丽度：{card.get('splendor', '')}")
    lines.append(f"灵力消耗：{card.get('mana_cost', '')}")
    lines.append(f"原始战力：{card.get('base_power', '')}")
    lines.append(f"伤害类型：{card.get('damage_type', '')}")
    lines.append(f"效果：{card.get('effect', '')}")
    lines.append("-" * 20)

with open("allCards_new.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"已合并 {len(batch_files)} 个批次，生成 {len(all_cards)} 张卡牌，已保存到 allCards_merged.json 和 allCards_new.txt")