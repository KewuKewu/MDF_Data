import sqlite3
from sqlite3 import Error
import json

def create_connection(db_file="cards.db"):
    """创建数据库连接"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"成功连接到数据库 {db_file}")
        return conn
    except Error as e:
        print(f"连接数据库时出错: {e}")
    return conn

def create_table(conn):
    """创建卡牌数据表"""
    try:
        # acquisition 相关变动暂未完成
        sql = """
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT NOT NULL,  -- 卡牌名称
            card_type TEXT,  -- 卡牌类型
            card_description TEXT, -- 卡牌描述
            rarity TEXT CHECK(rarity IN ('N', 'R', 'SR', 'SSR', 'UR')), -- 稀有度
            card_id TEXT UNIQUE NOT NULL,  -- 卡牌发行ID -- 同时标记卡牌图片路径
            belongs_to TEXT, -- 卡牌所属角色
            card_phrase TEXT, -- 卡牌短语
            acquisition TEXT, -- 存储JSON数组 -- 卡牌获取方式
            illustrator TEXT, -- 插画师
            related_tags TEXT,  -- 存储JSON数组 -- 关联词条
            splendor INTEGER, -- 华丽度
            mana_cost INTEGER, -- 灵力消耗
            base_power INTEGER, -- 原始战力
            damage_type TEXT, -- 伤害类型
            activation_level TEXT, -- 激活等级(S-C-H)
            character_nickname TEXT, -- 角色昵称
            unique_card_id INTEGER UNIQUE,  -- 卡牌存储ID，用于生成卡组
            card_features TEXT  -- 存储JSON数组 -- 卡牌特性
        );
        """
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        print("卡牌表创建成功")
    except Error as e:
        print(f"创建表时出错: {e}")

def insert_card(conn, card_data):
    """插入一张新卡牌"""
    sql = """
    INSERT INTO cards(
        card_name, card_type, card_description, rarity, card_id, belongs_to, 
        card_phrase, acquisition, illustrator, related_tags, 
        splendor, mana_cost, base_power, damage_type, activation_level, 
        character_nickname, unique_card_id, card_features
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        cursor = conn.cursor()
        
        # 将列表字段转换为JSON字符串
        if 'related_tags' in card_data:
            card_data['related_tags'] = json.dumps(card_data['related_tags'])
        
        # if 'skill_descriptions' in card_data:
        #     card_data['skill_descriptions'] = json.dumps(card_data['skill_descriptions'])

        if 'acquisition' in card_data:
            card_data['acquisition'] = json.dumps(card_data['acquisition'])

        if 'card_features' in card_data:
            card_data['card_features'] = json.dumps(card_data['card_features'])

        cursor.execute(sql, (
            card_data.get('card_name', ''),
            card_data.get('card_type', ''),
            card_data.get('card_description', ''),
            card_data.get('rarity', 'N'),
            card_data.get('card_id', ''),
            card_data.get('belongs_to', ''),
            card_data.get('card_phrase', ''),
            card_data.get('acquisition', ''),
            card_data.get('illustrator', ''),
            card_data.get('related_tags', '[]'),
            card_data.get('splendor', 0),
            card_data.get('mana_cost', 0),
            card_data.get('base_power', 0),
            card_data.get('damage_type', ''),
            card_data.get('activation_level', ''),
            card_data.get('character_nickname', ''),
            card_data.get('unique_card_id', 0),
            card_data.get('card_features', '[]')
        ))
        conn.commit()
        print(f"卡牌 '{card_data['card_name']}' 添加成功, ID: {cursor.lastrowid}")
        return cursor.lastrowid
    except Error as e:
        print(f"插入卡牌时出错: {e}")
        return None

def search_cards(conn, keyword, feature, belong, rarity, manacost, power, splendor, damageType, activationLevel, tags):
    """搜索卡牌"""
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM cards WHERE 1=1"
        params = []
        
        # 构建动态查询
        # 即按照不同要求进行查询，也可以同时对多个条件进行查询
        if keyword:
            for k in keyword.split():   # 分割关键词
                if k.strip():
                    query += " AND (card_name LIKE ? OR card_description LIKE ?)"
                    params.extend([f"%{k.strip()}%", f"%{k.strip()}%"])

        if feature:
            for f in feature.split(','):
                if f.strip():
                    query += " AND EXISTS (SELECT 1 FROM json_each(card_features) WHERE value LIKE ?)"
                    params.append(f"%{f.strip()}%")
            print("查询特性:", feature)

        if belong:
            query += " AND belongs_to LIKE ?"
            params.append(f"%{belong}%")

        if rarity:
            query += " AND rarity = ?"
            params.append(rarity)

        if manacost:
            query += " AND mana_cost = ?"
            params.append(manacost)
        
        if power:
            query += " AND base_power = ?"
            params.append(power)
        
        if splendor:
            query += " AND splendor = ?"
            params.append(splendor)
        
        if damageType:
            query += " AND damage_type LIKE ?"
            params.append(f"%{damageType}%")
        
        if activationLevel:
            query += " AND activation_level LIKE ?"
            params.append(f"%{activationLevel}%")

        if tags:
            for tag in tags.split(','):
                if tag.strip():
                    query += " AND EXISTS (SELECT 1 FROM json_each(related_tags) WHERE value LIKE ?)"
                    params.append(f"%{tag.strip()}%")

        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # 获取列名
        col_names = [description[0] for description in cursor.description]
        
        # 转换JSON字段
        formatted_results = []
        for row in results:
            card = dict(zip(col_names, row))
            # 解析JSON字段
            if card['related_tags']:
                card['related_tags'] = json.loads(card['related_tags'])
            # if card['skill_descriptions']:
            #     card['skill_descriptions'] = json.loads(card['skill_descriptions'])
            formatted_results.append(card)
        
        return formatted_results
    except Error as e:
        print(f"搜索卡牌时出错: {e}")
        return []

def create_indexes(conn):
    """创建索引以优化搜索性能"""
    try:
        cursor = conn.cursor()
        # 为常用搜索字段创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_card_name ON cards(card_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rarity ON cards(rarity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_illustrator ON cards(illustrator)")
        
        # 为JSON数组创建虚拟列和索引 (SQLite 3.9+)
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS terms_index USING fts5(term, content='cards', content_rowid='id');
        """)
        conn.commit()
        print("索引创建成功")
    except Error as e:
        print(f"创建索引时出错: {e}")

def delete_card(conn, card_id):
    """根据 card_id 删除卡牌"""
    sql = "DELETE FROM cards WHERE card_id = ?"
    try:
        cursor = conn.cursor()
        cursor.execute(sql, (card_id,))
        conn.commit()
        print(f"卡牌 {card_id} 已删除")
    except Error as e:
        print(f"删除卡牌时出错: {e}")
        
def update_card(conn, card_id, update_data):
    """根据 card_id 修改卡牌信息，update_data 为要更新的字段字典"""
    fields = []
    values = []
    for key, value in update_data.items():
        fields.append(f"{key} = ?")
        # 如果是 JSON 字段，需序列化
        if key in ['related_tags', 'acquisition', 'card_features']:
            value = json.dumps(value)
        values.append(value)
    sql = f"UPDATE cards SET {', '.join(fields)} WHERE card_id = ?"
    values.append(card_id)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, values)
        conn.commit()
        print(f"卡牌 {card_id} 已更新")
    except Error as e:
        print(f"修改卡牌时出错: {e}")

def main():
    # 1. 创建数据库连接
    conn = create_connection()
    if not conn:
        return
    
    # 2. 创建表
    create_table(conn)
    
    # 3. 创建索引
    create_indexes(conn)
    
    # 4. 添加示例卡牌
    # example_card = {
    #     "card_name": "「完美而潇洒的从者」",
    #     "card_type": "Character",
    #     "card_description": "CENTER：快刀乱麻【战斗阶段限1次】对对手造成特殊伤害时：弃置对手符力区或华丽区中的1张卡牌。HYPER：无尽之刃你可无视次数限制发动「快刀乱麻」。 你弃置或破坏对手的卡牌时：回复1点灵力或抽取1张卡牌。",
    #     "rarity": "R",
    #     "card_id": "SK-C01",
    #     "belongs_to": "十六夜咲夜",
    #     "card_phrase": "说她是女仆好呢，还是看孩子的好呢…",
    #     "acquisition": ["RP03-2023.4"],
    #     "illustrator": "Mincho",
    #     "related_tags": ["战斗阶段", "弃置", "破坏", "特殊伤害", "回复", "灵力", "抽取"],
    #     "skill_descriptions": [
    #         "CENTER：快刀乱麻：【战斗阶段限1次】对对手造成特殊伤害时：弃置对手符力区或华丽区中的1张卡牌。",
    #         "HYPER：无尽之刃：你可无视次数限制发动「快刀乱麻」。 你弃置或破坏对手的卡牌时：回复1点灵力或抽取1张卡牌。"
    #     ],
    #     "character_nickname": "完美而潇洒的从者",
    #     "unique_card_id": "003"
    # }
    
    # insert_card(conn, example_card)
    
    # # 5. 搜索示例
    # print("\n搜索 '火焰' 相关卡牌:")
    # results = search_cards(conn, term="火焰")
    # for card in results:
    #     print(f"{card['card_name']} ({card['rarity']}) - {card['character_nickname']}")
    #     print(f"关联词条: {', '.join(card['related_tags'])}")
    #     print("---")
    
    # 6. 关闭连接
    conn.close()

if __name__ == "__main__":
    main()