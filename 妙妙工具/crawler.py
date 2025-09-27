import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

role_codes = ["RM", "MS", "SK", "YM", "REM", "FLD", "MQ", "UU", "YK", "RC", "SYS"]
BASE_URL = "https://mdf.best"

def parse_card_div(card_div):
    card = {}
    rarity = card_div.select_one('.header .rarity')
    card['rarity'] = rarity.text.strip() if rarity else ""
    sku = card_div.select_one('.footer .sku')
    card['card_id'] = sku.text.strip() if sku else ""
    img = card_div.select_one('.card-image img.pokemon-css-card__front')
    card['image'] = img['src'] if img else ""
    title = card_div.select_one('.right .title text')
    card['card_name'] = title.text.strip() if title else ""
    artist = ""
    for p in card_div.select('.meta p'):
        if p.text.strip().startswith("画师："):
            artist = p.text.strip().replace("画师：", "")
            break
    card['artist'] = artist
    obtain = ""
    for p in card_div.select('.meta p'):
        if p.text.strip().startswith("从"):
            obtain = p.text.strip()
            break
    card['obtain'] = obtain
    effect = card_div.select_one('.right .effect')
    card['effect'] = effect.text.strip() if effect else ""
    center_tag = card_div.select_one('.right .tag.center')
    hyper_tag = card_div.select_one('.right .tag.hyper')
    support_tag = card_div.select_one('.right .tag.support')
    exclusive_tag = card_div.select_one('.right .tag.exclusive')
    card_type = ""
    for span in card_div.select('.header .col-auto .tag'):
        if "角色卡" in span.text:
            card_type = "角色卡"
        elif "符卡" in span.text:
            card_type = span.text.strip()
    card['card_type'] = card_type

    def get_text_with_desc(tag):
        if not tag:
            return ""
        desc = ""
        next_p = tag.find_next_sibling('p')
        if next_p:
            desc = next_p.text.strip()
        return tag.text.strip() + (" " + desc if desc else "")

    def get_tag_text(tag):
        return tag.text.strip() if tag else ""

    # 新增：发动条件
    activation_conditions = []

    if card_type == "角色卡":
        card['center'] = get_text_with_desc(center_tag)
        card['hyper'] = get_text_with_desc(hyper_tag)
        card['support'] = get_text_with_desc(support_tag)
        card['exclusive'] = get_text_with_desc(exclusive_tag)
        card['activation_condition'] = ""
    else:
        # 非角色卡，标签内容保留到原字段，描述内容放到 activation_condition
        def get_condition(tag):
            if not tag:
                return ""
            next_p = tag.find_next_sibling('p')
            return next_p.text.strip() if next_p else ""
        card['center'] = get_tag_text(center_tag)
        card['hyper'] = get_tag_text(hyper_tag)
        card['support'] = get_tag_text(support_tag)
        card['exclusive'] = get_tag_text(exclusive_tag)
        # 收集所有有描述的发动条件
        for tag in [center_tag, hyper_tag, support_tag, exclusive_tag]:
            cond = get_condition(tag)
            if cond:
                activation_conditions.append(cond)
        card['activation_condition'] = "；".join(activation_conditions)

    cards_detail = card_div.select_one('.right .content .detail')
    if cards_detail:
        tds = cards_detail.find_all('td')
        for i in range(0, len(tds), 2):
            key = tds[i].text.strip()
            value = tds[i+1].text.strip() if i+1 < len(tds) else ""
            if key == "华丽度":
                card['splendor'] = value
            elif key == "灵力消耗":
                card['mana_cost'] = value
            elif key == "原始战力":
                card['base_power'] = value
            elif key == "伤害类型":
                card['damage_type'] = value
    return card

async def main():
    cards = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for code in role_codes:
            url = f"{BASE_URL}/{code}"
            print(f"正在爬取：{url}")
            await page.goto(url)
            await page.wait_for_timeout(2500)  # 等待页面渲染
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            for card_div in soup.select('.col-lg-6.twin-center .game-card'):
                card = parse_card_div(card_div)
                cards.append(card)
        await browser.close()
    with open("allCards.json", "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(f"共提取 {len(cards)} 张卡牌，已保存到 allCards.json")

if __name__ == "__main__":
    asyncio.run(main())