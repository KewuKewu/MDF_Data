import csv
import json
# import sqlite3
# from sqlite3 import Error
from mdf_data_control import create_connection, insert_card

def main():
    conn = create_connection()
    if not conn:
        return

    # 假设你的 csv 文件名为 cards.csv，第一行为表头
    with open('cards.csv', encoding='gbk') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 如果某些字段需要特殊处理（如 JSON 字段），可在此处理
            if 'related_terms' in row:
                try:
                    row['related_terms'] = json.loads(row['related_terms'])
                except json.JSONDecodeError:
                    row['related_terms'] = [term.strip() for term in row['related_terms'].split(',')]
            # if 'skill_descriptions' in row:
            #     try:
            #         row['skill_descriptions'] = json.loads(row['skill_descriptions'])
            #     except json.JSONDecodeError:
            #         row['skill_descriptions'] = [desc.strip() for desc in row['skill_descriptions'].split(',')]
            if 'acquisition' in row:
                try:
                    row['acquisition'] = json.loads(row['acquisition'])
                except json.JSONDecodeError:
                    row['acquisition'] = [acq.strip() for acq in row['acquisition'].split(',')]
            if 'related_tags' in row:
                try:
                    row['related_tags'] = json.loads(row['related_tags'])
                except json.JSONDecodeError:
                    row['related_tags'] = [tag.strip() for tag in row['related_tags'].split(',')]
            if 'card_features' in row:
                try:
                    row['card_features'] = json.loads(row['card_features'])
                except json.JSONDecodeError:
                    row['card_features'] = [feature.strip() for feature in row['card_features'].split(',')]
    # 插入数据库
            insert_card(conn, row)
            # print(f"已插入卡牌: {row.get('card_name', '未知名称')}")

    conn.close()

if __name__ == '__main__':
    main()