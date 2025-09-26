from flask import Flask, request, jsonify
from flask_cors import CORS
from mdf_data_control import create_connection, insert_card, search_cards, delete_card, update_card

# 创建 Flask 应用实例
app = Flask(__name__)
CORS(app)  # 允许跨域请求，方便前端本地开发

@app.route('/card/add', methods=['POST'])
def add_card():
    conn = create_connection()  # 每次请求新建连接
    card_data = request.json
    card_id = insert_card(conn, card_data)
    conn.close()  # 用完关闭连接
    if card_id:
        return jsonify({"msg": "添加成功", "id": card_id}), 201
    else:
        return jsonify({"msg": "添加失败"}), 400

@app.route('/card/search', methods=['GET'])
def search():
    conn = create_connection()
    keyword = request.args.get('keyword', '')
    feature = request.args.get('feature', '')
    belong = request.args.get('belong', '')
    rarity = request.args.get('rarity', '')
    manacost = request.args.get('manacost', '')
    power = request.args.get('power', '')
    splendor = request.args.get('splendor', '')
    damageType = request.args.get('damageType', '')
    activationLevel = request.args.get('activationLevel', '')
    tags = request.args.get('tags', '')
    results = search_cards(conn, keyword, feature, belong, rarity, manacost, power, splendor, damageType, activationLevel, tags)
    conn.close()
    return jsonify(results)

@app.route('/card/delete/<card_id>', methods=['DELETE'])
def delete(card_id):
    conn = create_connection()
    delete_card(conn, card_id)
    conn.close()
    return jsonify({"msg": "删除成功", "id": card_id})

@app.route('/card/update/<card_id>', methods=['PUT'])
def update(card_id):
    conn = create_connection()
    update_data = request.json
    update_card(conn, card_id, update_data)
    conn.close()
    return jsonify({"msg": "修改成功"})

@app.route('/card/all', methods=['GET'])
def get_all_cards():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT card_id, unique_card_id, card_name FROM cards")
    results = cursor.fetchall()
    conn.close()
    # 转为字典列表
    cards = [{"card_id": row[0], "unique_card_id": row[1], "card_name": row[2]} for row in results]
    return jsonify(cards)

if __name__ == '__main__':
    # 启动 Flask 服务，debug 模式方便开发调试
    app.run(debug=True)