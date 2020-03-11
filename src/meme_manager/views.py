from flask import Blueprint, json, jsonify, request, Response

from . import db
from .models import Image, Group

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
分页后端实现，使用url参数?page=[int]&per_page=[int]
- page: 可选，默认为 1。
- per_page：可选，默认为 20。
搜索：后端实现，使用 url 参数，可搜索项：tag。
- tag: [str]
- group: [str]
resp: 200, body:
{
    "data": [
        {
            "id": [Number],
            "img_type": [String],
            "tags": [Array[String]],
            "group": [String] or [null],
            "create_at": [String]
        },
        ...
    ]
    "pagination": {
        'pages': [Number], # 总页数
        'page': [Number], # 当前页码
        'per_page': [Number], # 每页条数（行数）
        'total': [Number] # 总条数（行数）
    }
}

GET id=[int]
resp: 200, body:
content-type: image/<img_type>
图片二进制数据
"""
@bp_main.route('/api/images/', methods=['GET'])
def show_images():
    image_id = request.args.get('id')
    if image_id:
        image = Image.query.get(image_id)
        response = Response(image.data, mimetype=f'image/{image.img_type}')
        return response
    else:
        # apply search
        group = request.args.get('group')
        tag = request.args.get('tag')
        if group:
            query = Image.query.join(Image.group).filter(Group.name == group)
        else:
            query = Image.query

        if tag:
            query = query.filter(Image.tags.contains(tag))
        # apply pagination
        DEFAULT_PER_PAGE = 20
        page = int(request.args.get('page', default=1))
        per_page = int(request.args.get('per_page', default=DEFAULT_PER_PAGE))
        paginate = query.order_by(Image.create_at)\
                        .paginate(page=page, per_page=per_page)

        columns = ('id', 'img_type', 'tags', 'group', 'create_at')

        response = {
            'data': [record.readyToJSON(columns, DATETIME_FORMAT) for record in paginate.items],
            'pagination': {
                'pages': paginate.pages,
                'page': paginate.page,
                'per_page': paginate.per_page,
                'total': paginate.total,
            }
        }
        return jsonify(response)
        


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
@bp_main.route('/api/images/add', methods=['POST'])
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
@bp_main.route('/api/images/delete', methods=['GET'])
def delete_image():
    image_id = int(request.args.get('id'))
    image = Image.query.get(image_id)
    if image is None:
        err = f'图片（id={image_id}）不存在，可能是其已被删除，请刷新页面。'
        return jsonify({
            'error': err
        }), 404
    else:
        db.session.delete(image)
        db.session.commit()
        return jsonify({
            'msg': f'成功删除图片（id={image_id}）'
        })


"""/images/update
POST {
    "id": [Number],
    "group": [String]
}
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/api/images/update', methods=['POST'])
def update_image():
    data = request.get_json()
    image_id = data['id']
    image = Image.query.get(image_id)
    if image is None:
        err = f'图片（id={image_id}）不存在，可能是其已被删除，请刷新页面。'
        return jsonify({
            'error': err
        }), 404
    
    group_name = data['group']
    if group_name is None:
        image.group_id = None
        db.session.commit()
        return jsonify({
            'msg': f'成功将图片（id={image_id}）移至组（全部））'
        })
    else:
        group = Group.query.filter_by(name=group_name).first()
        if group is None:
            err = f'组（name={group_name}）不存在。'
            return jsonify({
                'error': err
            }), 404

        image.group = group
        db.session.commit()
        return jsonify({
            'msg': f'成功将图片（id={image_id}）移至组（name={group_name}）'
        })


# tags
"""/tags/
GET ?image_id=[int]
resp: 200, body:
{
    "data": [Array[String]]
}
"""
@bp_main.route('/api/tags/', methods=['GET'])
def show_tags():
    image_id = int(request.args.get('image_id'))
    image = Image.query.get(image_id)
    if image is None:
        err = f'图片（id={image_id}）不存在，可能是其已被删除，请刷新页面。'
        return jsonify({
            'error': err
        }), 404

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
@bp_main.route('/api/tags/add', methods=['POST'])
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
@bp_main.route('/api/tags/delete', methods=['POST'])
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


# group
"""/groups/
GET
resp: 200, body:
{
    "data": [Array[String]]
}
"""
@bp_main.route('/api/groups/', methods=['GET'])
def show_groups():
    groups = Group.query.order_by(Group.name).all()
    resp = {
        'data': [r.name for r in groups],
    }
    return jsonify(resp)


"""/groups/add
POST {
    "name": [String],
}
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/api/groups/add', methods=['POST'])
def add_group():
    data = request.get_json()
    name = data['name']
    record = Group(name=name)
    db.session.add(record)
    db.session.commit()
    return jsonify({
        'msg': f'成功添加组：{record}'
    })


"""/groups/delete
POST {
    "name": [String],
}
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/api/groups/delete', methods=['POST'])
def delete_group():
    data = request.get_json()
    name = data['name']
    record = Group.query.filter_by(name=name).first()
    if record is None:
        err = f'组（name={name}）不存在，可能是其已被删除，请刷新页面。'
        return jsonify({
            'error': err
        }), 404
    else:
        db.session.delete(record)
        db.session.commit()
        return jsonify({
            'msg': f'成功删除组（name={name}）'
        })


"""/groups/update
POST {
    "name": [String],
    "new_name": [String]
}
resp: 200, body: {"msg": [String]}
"""
@bp_main.route('/api/groups/update', methods=['POST'])
def update_group():
    data = request.get_json()
    name = data['name']
    record = Group.query.filter_by(name=name).first()
    record.name = data['new_name']
    db.session.commit()
    return jsonify({
        'msg': f'成功更新组：{record}'
    })
