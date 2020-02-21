from flask import Blueprint, json, jsonify, request, make_response, Response

from . import db
from .models import Image

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

bp_main = Blueprint('bp_main', __name__)


@bp_main.after_app_request
def disable_CORS(response):
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    origin = request.headers.get('Origin')
    response.headers['Access-Control-Allow-Origin'] = origin
    return response


# images
"""/images/
GET
resp: 200, body:
{
    "data": [
        {
            "id": [Number],
            "img_type": [String]
            "tags": [Array[String]],
            "create_at": [String]
        },
        ...
    ]
}

GET id=[int]
resp: 200, body:
content-type: image/<img_type>
图片二进制数据
"""
@bp_main.route('/images/', methods=['GET'])
def show_images():
    image_id = request.args.get('id')
    if image_id is None:
        images = Image.query.order_by(Image.create_at).all()

        columns = ('id', 'img_type', 'tags', 'create_at')

        response = {
            'data': [record.readyToJSON(columns, DATETIME_FORMAT) for record in images]
        }
        return jsonify(response)
    else:
        image = Image.query.get(image_id)
        response = Response(image.data, mimetype=f'image/{image.img_type}')
        return response


"""/images/add
POST 使用表单提交
Content-Type: multipart/form-data
"image": [bytes-file],
"metadata": [JSON-String] {
    "img_type": [String],
    "tags": [Array[String]]
}
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/images/add', methods=['POST'])
def add_image():
    image_file = request.files['image']
    image_data = image_file.read()
    image_file.close()
    metadata = json.loads(request.form['metadata'])
    record = Image(
        data=image_data,
        img_type=metadata['img_type'],
        tags=','.join(metadata['tags']),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({
        'msg': f'成功添加图片：{record}'
    })


"""/images/delete
GET ?id=[Number]
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/images/delete', methods=['GET'])
def delete_image():
    image_id = int(request.args.get('id'))
    image = Image.query.get(image_id)
    if image is None:
        err = f'图片（id={image_id}）不存在，可能是其已被删除，请刷新页面。'
        return make_response(jsonify({
            'error': err
        }), 404)
    else:
        db.session.delete(image)
        db.session.commit()
        return jsonify({
            'msg': f'成功删除图片（id={image_id}）'
        })


# tags
"""/tags/
GET ?image_id=[int]
resp: 200, body:
{
    "data": [Array[String]]
}
"""
@bp_main.route('/tags/', methods=['GET'])
def show_tags():
    image_id = int(request.args.get('image_id'))
    image = Image.query.get(image_id)
    if image is None:
        err = f'图片（id={image_id}）不存在，可能是其已被删除，请刷新页面。'
        return make_response(jsonify({
            'error': err
        }), 404)

    response = {
        'data': image.tags.split(','),
    }
    return jsonify(response)


"""/tags/add
POST {
    "image_id": [Number],
    "tags": [Array[String]]
}
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/tags/add', methods=['POST'])
def add_tags():
    data = request.get_json()
    image_id = data['image_id']
    image = Image.query.get(image_id)
    if data['tags']:
        image.tags += (',' + ','.join(data['tags']))
        db.session.commit()

    return jsonify({
        'msg': f'成功添加为图片（id={image_id}）添加标签：{data["tags"]}'
    })


"""/tags/delete
POST {
    "image_id": xxx,
    "tag": [String]
}
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/tags/delete', methods=['POST'])
def delete_tag():
    data = request.get_json()
    image_id = data['image_id']
    image = Image.query.get(image_id)
    new_tags = image.tags.split(',')
    new_tags.remove(data['tag'])
    image.tags = ','.join(new_tags)
    db.session.commit()
    return jsonify({
        'msg': f'成功删除标签：{data}'
    })
