import os
from bson import ObjectId
from flask import Flask, request, Response, jsonify
from flask_pymongo import PyMongo
from mail import send_mail, celery_app
from schema import validation_create_notification, validation_list_notification, HttpError, create_mark
from bson import json_util
from celery.result import AsyncResult

PORT = os.getenv('PORT')
DB_URI = os.getenv('DB_URI')
# DB_URI = "mongodb://localhost:27017/dbdata6"

app = Flask(__name__)
app.config["MONGO_URI"] = DB_URI
mongo = PyMongo(app)


@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    http_response = jsonify({'status': 'error', 'description': error.message})
    http_response.status_code = error.status_code
    return http_response


@app.route('/create', methods=['POST'])
def create():
    count_documents = mongo.db.notifications.count_documents({})
    if count_documents < 5:
        user_id = request.json.get("user_id")
        key = request.json.get("key")

        is_new = False
        target_id = request.json.get("target_id")
        data = request.json.get('data')

        json_data = {'user_id': user_id, 'target_id': target_id,
                     'key': key, 'data': data, 'is_new': is_new
                     }
        json_data = validation_create_notification(json_data)
        print(f'{json_data=}')

        if key == 'registration':
            send_mail.delay()
        elif key == 'new_message':
            mongo.db.notifications.insert_one(json_data)
        elif key == 'new_post':
            mongo.db.notifications.insert_one(json_data)
        elif key == 'new_login':
            send_mail.delay()
            mongo.db.notifications.insert_one(json_data)

        response = jsonify({"success": True})
        response.status_code = 201
        return response
    else:
        raise HttpError(status_code=400, message='Количество документов не должно быть больше 5')


@app.route('/list', methods=['GET'])
def listing():
    qs = dict(request.args)
    json_data = validation_list_notification(qs)

    limit = int(json_data.get('limit', 0))
    user_id = {'user_id': ObjectId(json_data.get('user_id'))} if json_data.get('user_id') else {}
    skip = int(json_data.get('skip', 0))

    notifications = mongo.db.notifications.find(user_id).skip(skip).limit(limit)

    response_list = list(notifications)
    for x in response_list:
        x['id'] = str(x.pop('_id'))
        x['target_id'] = str(x.pop('target_id'))
        x['user_id'] = str(x.pop('user_id'))

    elements = len(response_list)
    new = sum(1 for notification in response_list if notification.get('is_new'))
    query = request.args

    response = {"success": True,
                "data": {"elements": elements,
                         "new": new,
                         "request": query,
                         "list": response_list
                         }
                }

    return Response(json_util.dumps(response), mimetype="application/json")


@app.route('/read', methods=['POST'])
def create_read_mark():
    user_id = request.args.get('user_id')
    notification_id = request.args.get('notification_id')
    data = {'user_id': user_id, 'notification_id': notification_id}
    read_data = create_mark(data)
    read_data['_id'] = read_data.pop('notification_id')

    result_update = mongo.db.notifications.update_one(
        read_data, {'$set': {'is_new': True}}
    )

    if not result_update.matched_count == result_update.acknowledged:
        raise HttpError(status_code=404, message='Уведомление не найдено или не обработано ')

    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(port=PORT)
