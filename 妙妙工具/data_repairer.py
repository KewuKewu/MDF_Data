import json
import re

with open("allCards_merged.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

role_prefix_list = []
role_card_index = {}
spell_card_index = {}

def get_role_prefix(card_id):
    m = re.match(r"([A-Z]+)[\-_]", card_id)
    return m.group(1) if m else None

for card in cards:
    card_id = card.get("card_id", "")
    card_type = card.get("card_type", "")
    prefix = get_role_prefix(card_id)
    if not prefix:
        card["unique_card_id"] = ""
        continue

    # 记录角色出现顺序
    if prefix not in role_prefix_list:
        role_prefix_list.append(prefix)

# 角色卡编号
for card in cards:
    card_id = card.get("card_id", "")
    card_type = card.get("card_type", "")
    prefix = get_role_prefix(card_id)
    if not prefix:
        card["unique_card_id"] = ""
        continue

    role_base = 1000 + role_prefix_list.index(prefix) * 10
    spell_base = 101000 + role_prefix_list.index(prefix) * 1000

    if card_type == "角色卡":
        idx = role_card_index.setdefault(prefix, 0)
        card["unique_card_id"] = str(role_base + idx + 1)
        role_card_index[prefix] += 1
    else:
        idx = spell_card_index.setdefault(prefix, 0)
        card["unique_card_id"] = str(spell_base + idx + 1)
        spell_card_index[prefix] += 1

with open("allCards_merged_with_uid.json", "w", encoding="utf-8") as f:
    json.dump(cards, f, ensure_ascii=False, indent=2)

print("已为所有卡牌分配 unique_card_id，并保存到 allCards_merged_with_uid.json")