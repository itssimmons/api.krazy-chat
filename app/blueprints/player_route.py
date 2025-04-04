from flask_socketio import emit  # type: ignore
from flask.json import jsonify
from flask import Blueprint, request
from uuid import uuid4
from datetime import datetime
from config.database import Builder
from typing import Dict, Any

players_bp = Blueprint("players", __name__, url_prefix="/players")

ASSISTANT_ID = 1


@players_bp.route("/register/<username>", methods=["GET"])
def register_player(username: str):
    """
    Example:
        .. code-block:: bash
        curl -X GET "http://127.0.0.1:8000/{version}/players/register/{username}" \\
        -d room=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX \\
        -d avatar=http://... \\
        -d color=#92F700
    """

    query_params: Dict[str, Any] = {
        "avatar": request.args.get("avatar"),
        "color": request.args.get("color"),
        "room": request.args.get("room"),
    }

    already_registered = (
        Builder.query("users")
        .fields("*")
        .where(f"username LIKE '%{username}%'")
        .limit(1)
        .read()
    )

    if already_registered.exists:
        existing_user = already_registered.fetchone()
        response = jsonify({"user": existing_user, "is": "old"})
        return response, 200

    lastrowid = (
        Builder.query("users")
        .fields(["username", "avatar", "color", "status"])
        .values((username, query_params["avatar"], query_params["color"], "online"))
        .create()
    )

    created_user = (
        Builder.query("users").fields("*").where(f"id = {lastrowid}").read().fetchone()
    )

    welcome_message: Dict[str, Any] = {
        "id": str(uuid4()),
        "sender_id": ASSISTANT_ID,
        "modified_id": None,
        "message": f"Ey! say everybody welcome to @{username} 👋",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modified_at": None,
    }

    (
        Builder.query("chats")
        .fields("*")
        .values(tuple(welcome_message.values()))
        .create()
    )

    emit("main:channel", welcome_message, to=query_params["room"], namespace="/channel")  # type: ignore

    response = jsonify({"user": created_user, "is": "new"})
    return response, 201


@players_bp.route("/", methods=["GET"])
def read_players():
    """
    Example:
        .. code-block:: bash
        curl -X GET "http://127.0.0.1:8000/{version}/players"
    """

    users = Builder.query("users").fields("*").read().fetchall()
    response = jsonify(users)
    response.headers["Cache-Control"] = "no-store"
    return response, 200


@players_bp.route("/<int:user_id>", methods=["PATCH"])
def update_player_status(user_id: int):
    """
    Example:
        .. code-block:: bash
        curl -X PATCH "http://127.0.0.1:8000/{version}/players/{user_id}" \\
        -H "Content-Type: application/json" \\
        -d status={online|offline|writing}
    """

    data: Dict[str, Any] = request.get_json()
    status: str = data["status"]

    if status not in ["online", "offline", "typing", "idle"]:
        return jsonify({"success": False, "message": f"Invalid status: {status}"}), 400

    (
        Builder.query("users", False)
        .fields(["status"])
        .values((status,))
        .where(f"id = {user_id}")
        .update()
    )

    response = jsonify(
        {"success": True, "message": f"User {user_id} status updated to {status}"}
    )
    return response, 200
