from flask_socketio import emit  # type: ignore
from flask import request
from typing import Any
from app import socketio

# Handling errors


@socketio.on_error("/channel")
def error_handler_channel(e: Any):
    print("\n--- [BEGIN | error_handler_channel] ---")
    print("Reason: ", str(e))
    print(request.event["message"])  # "my error event" # type: ignore
    print(request.event["args"])  # (data,) # type: ignore
    print("--- [END | error_handler_channel] ---\n")


@socketio.on_error_default
def default_error_handler(e: Any):
    print("\n--- [BEGIN | default_error_handler] ---")
    print("Reason: ", str(e))
    print(request.event["message"])  # "my error event" # type: ignore
    print(request.event["args"])  # (data,) # type: ignore
    print("--- [END | default_error_handler] ---\n")


from app.events.namespaces.channel import *
