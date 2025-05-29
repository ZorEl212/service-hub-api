import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi_users import BaseUserManager

from models import auth
from models.user import User
from services.socket import SocketManager
from utils.exceptions import AppException

router = APIRouter()
socket_manager = SocketManager()


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, user_manager: BaseUserManager = Depends(auth.get_user_manager)):
    try:
        # Authenticate user
        user: User = await auth.get_user_from_cookie(websocket, user_manager)
        if not user:
            print("user not logged in")
            await websocket.close(code=4001)
            return

        # Accept the connection
        await websocket.accept()
        sid = websocket.headers.get("sec-websocket-key", "")

        # Connect user and store websocket
        await socket_manager.connect(sid, str(user.id), websocket)

        try:
            while True:
                # Wait for messages
                data = await websocket.receive_json()

                if data["type"] == "message":
                    # Handle new message
                    result = await socket_manager.send_message(
                        sender_id=user,
                        receiver_id=data["receiver_id"],
                        content=data["content"],
                        attachments=data.get("attachments"),
                    )
                    if not result.success:
                        await websocket.send_json(
                            {"type": "error", "message": str(result.exception_case)}
                        )

                elif data["type"] == "mark_read":
                    # Handle marking messages as read
                    result = await socket_manager.mark_messages_read(
                        user_id=user, sender_id=data["sender_id"]
                    )
                    if not result.success:
                        await websocket.send_json(
                            {"type": "error", "message": str(result.exception_case)}
                        )

                elif data["type"] == "get_chat_rooms":
                    # Handle getting chat rooms
                    result = await socket_manager.get_chat_rooms(user)
                    await websocket.send_json({
                        "type": "chat_rooms",
                        "data": result.value if result.success else [],
                    })
                    if not result.success:
                        await websocket.send_json(
                            {"type": "error", "message": str(result.exception_case)}
                        )

                elif data["type"] == "get_chat_history":
                    # Handle getting chat history
                    result = await socket_manager.get_chat_history(
                        user_id=user,
                        other_user_id=data["other_user_id"],
                        page=data.get("page", 1),
                        limit=data.get("limit", 50),
                    )
                    if result.success:
                        await websocket.send_json(
                            {"type": "chat_history", "data": result.value}
                        )
                    else:
                        await websocket.send_json(
                            {"type": "error", "message": str(result.exception_case)}
                        )

        except WebSocketDisconnect:
            await socket_manager.disconnect(sid)

    except Exception as e:
        await websocket.close(code=4000)
