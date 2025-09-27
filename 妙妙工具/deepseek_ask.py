import requests

API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = "sk-60d743ebff914ec68110d1efd3140191"

with open("allCards.txt", "r", encoding="utf-8") as f:
    txt_content = f.read()

card_blocks = txt_content.split('--------------------')
card_blocks = [block.strip() for block in card_blocks if block.strip()]

batch_size = 10
start_batch = 21
start_index = (start_batch - 1) * batch_size
all_results = []

total_batches = (len(card_blocks) + batch_size - 1) // batch_size

for i in range(start_index, len(card_blocks), batch_size):
    batch_num = i // batch_size + 1
    print(f"\n=== 开始处理第 {batch_num}/{total_batches} 批（卡牌 {i+1} ~ {min(i+batch_size, len(card_blocks))}） ===")
    batch = card_blocks[i:i+batch_size]
    batch_txt = '\n--------------------\n'.join(batch)
    prompt = f"""请将以下卡牌信息（每张卡牌用“--------------------”分隔）转换为 JSON 数组，每张卡牌的字段包括：

card_name 卡牌名称
card_type 卡牌类型
card_description 卡牌描述
rarity 稀有度
card_id 卡牌发行ID
belongs_to 卡牌所属角色
card_phrase 卡牌短语
acquisition 卡牌获取方式 额外存储为JSON数组
illustrator 插画师
related_tags 关联词条 额外存储为JSON数组
splendor 华丽度
mana_cost 灵力消耗
base_power 原始战力
damage_type 伤害类型
activation_level 激活等级(S-C-H)
character_nickname 角色昵称
unique_card_id 卡牌存储ID，用于生成卡组
card_features 卡牌特性 额外存储为JSON数组

其中卡牌描述字段应包括这张卡的全部信息。
如果某字段没有内容请填空字符串。
返回标准 JSON 格式，不要有多余解释。

内容如下：
{batch_txt}

请直接输出JSON，不要输出任何解释或推理过程。
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 40960
    }

    response = requests.post(API_URL, headers=headers, json=data)
    print(f"第 {batch_num} 批 status:", response.status_code)
    print(f"第 {batch_num} 批返回内容预览:", response.text[:300])

    result = response.json()
    json_text = result['choices'][0]['message']['content']
    all_results.append(json_text)

    # 单独保存每一批的返回内容
    with open(f"allCards_ai_batch_{batch_num}.json", "w", encoding="utf-8") as f:
        f.write(json_text)

    print(f"=== 第 {batch_num} 批处理完成，已保存到 allCards_ai_batch_{batch_num}.json ===")

print("所有批次已处理完毕。")