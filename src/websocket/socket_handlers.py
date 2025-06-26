"""
WebSocket event handlers for real-time communication
Handles Socket.IO events following Single Responsibility Principle
"""

from flask_socketio import SocketIO, emit


def register_socket_handlers(socketio: SocketIO) -> None:
    """
    Register WebSocket event handlers with SocketIO instance
    
    Args:
        socketio: SocketIO instance
    """
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        emit('status', {'message': 'Connected to NimbusRelay'})
        print('Client connected to WebSocket')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print('Client disconnected from WebSocket')
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping from client"""
        emit('pong', {'timestamp': 'pong'})
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Handle client joining a room"""
        room = data.get('room', 'general')
        # Note: join_room would be imported from flask_socketio if needed
        emit('status', {'message': f'Joined room: {room}'})
    
    @socketio.on('email_update')
    def handle_email_update(data):
        """Handle email update notifications"""
        # Broadcast email updates to all connected clients
        socketio.emit('email_notification', data, broadcast=True)
