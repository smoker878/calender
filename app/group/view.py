from flask import request, jsonify, render_template
from flask.views import MethodView
from flask_login import login_required, current_user
from app import db
from app.models import Group, User
from app.schemas import GroupSchema
from marshmallow import ValidationError
from sqlalchemy.orm import  selectinload
from . import group_bp


# 列出當前使用者加入的群組
@group_bp.route("/", methods=["GET"])
@login_required
def groups_page():
    return render_template("groups/index.html")  # 群組列表頁

# 單個群組詳細頁
@group_bp.route("/<int:group_id>/view", methods=["GET"])
@login_required
def group_detail_page(group_id):
    return render_template("groups/detail.html", group_id=group_id)


# -------------------------------
# 群組 CRUD + 成員管理 CBV
# -------------------------------
class GroupAPI(MethodView):
    decorators = [login_required]

    # GET /api/groups 或 /api/groups/<id>
    def get(self, group_id=None):
        if group_id is None:
            # 取得當前使用者加入的所有群組
            groups = Group.query.join(Group.users)\
                .filter(User.id == current_user.id)\
                .options(
                    selectinload(Group.users),
                    selectinload(Group.events)
                ).all()
            schema = GroupSchema(many=True)
            return jsonify(schema.dump(groups))
        else:
            # 單筆群組詳細資訊
            group = Group.query.options(
                selectinload(Group.users),
                selectinload(Group.events)
            ).get_or_404(group_id)
            schema = GroupSchema()
            return jsonify(schema.dump(group))

    # POST /api/groups
    def post(self):
        data = request.json
        name = data.get("name")
        if not name:
            return jsonify({"error": "Group name is required"}), 400

        if Group.query.filter_by(name=name).first():
            return jsonify({"error": "Group name already exists"}), 400

        group = Group(name=name)
        # 建立時把自己加入群組
        group.users.append(current_user)

        db.session.add(group)
        db.session.commit()

        schema = GroupSchema()
        return jsonify(schema.dump(group)), 201

    # PUT /api/groups/<id>
    def put(self, group_id):
        group = Group.query.get_or_404(group_id)
        data = request.json
        name = data.get("name")
        if not name:
            return jsonify({"error": "Group name is required"}), 400

        # 權限檢查：只有創建者可修改
        if group.users[0].id != current_user.id:
            return jsonify({"error": "Not allowed"}), 403

        group.name = name
        db.session.commit()

        schema = GroupSchema()
        return jsonify(schema.dump(group))

    # DELETE /api/groups/<id>
    def delete(self, group_id):
        group = Group.query.get_or_404(group_id)

        if group.users[0].id != current_user.id:
            return jsonify({"error": "Not allowed"}), 403

        db.session.delete(group)
        db.session.commit()
        return jsonify({"message": "Group deleted"}), 200


# -------------------------------
# 群組成員管理 CBV
# -------------------------------
class GroupMemberAPI(MethodView):
    decorators = [login_required]

    # POST /api/groups/<id>/members
    def post(self, group_id):
        group = Group.query.get_or_404(group_id)
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "user_id required"}), 400

        user = User.query.get_or_404(user_id)
        if user in group.users:
            return jsonify({"error": "User already in group"}), 400

        group.users.append(user)
        db.session.commit()

        schema = GroupSchema()
        return jsonify(schema.dump(group))

    # DELETE /api/groups/<id>/members/<user_id>
    def delete(self, group_id, user_id):
        group = Group.query.get_or_404(group_id)
        user = User.query.get_or_404(user_id)
        if user not in group.users:
            return jsonify({"error": "User not in group"}), 400

        group.users.remove(user)
        db.session.commit()

        schema = GroupSchema()
        return jsonify(schema.dump(group))


# -------------------------------
# 註冊 CBV route
# -------------------------------
group_view = GroupAPI.as_view("group_api")
group_member_view = GroupMemberAPI.as_view("group_member_api")

# CRUD
group_bp.add_url_rule("/api/groups", defaults={"group_id": None},
                      view_func=group_view, methods=["GET",])
group_bp.add_url_rule("/api/groups", view_func=group_view, methods=["POST",])
group_bp.add_url_rule("/api/groups/<int:group_id>", view_func=group_view,
                      methods=["GET", "PUT", "DELETE"])

# 成員管理
group_bp.add_url_rule("/api/groups/<int:group_id>/members",
                      view_func=group_member_view, methods=["POST"])
group_bp.add_url_rule("/api/groups/<int:group_id>/members/<int:user_id>",
                      view_func=group_member_view, methods=["DELETE"])