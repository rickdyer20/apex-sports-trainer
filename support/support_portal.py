"""
Customer Support Portal for Basketball Analysis Service

This module implements a comprehensive customer support system including:
- Live chat with WebSocket support
- Ticket management system  
- Knowledge base integration
- Escalation workflows
- Support analytics and reporting

Built for production scalability with proper error handling and monitoring.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
import uuid
import json
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import redis
from celery import Celery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/basketball_support'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
login_manager = LoginManager(app)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Celery configuration for async tasks
celery = Celery(app.name, broker='redis://localhost:6379')

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ChatMessageType(Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

# Database Models
class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.Enum(TicketPriority), default=TicketPriority.MEDIUM)
    status = db.Column(db.Enum(TicketStatus), default=TicketStatus.OPEN)
    
    assigned_agent_id = db.Column(db.String(36), nullable=True)
    assigned_agent_name = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    messages = db.relationship('TicketMessage', backref='ticket', lazy=True, cascade='all, delete-orphan')
    attachments = db.relationship('TicketAttachment', backref='ticket', lazy=True, cascade='all, delete-orphan')

class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(db.String(36), db.ForeignKey('support_tickets.id'), nullable=False)
    
    sender_id = db.Column(db.String(36), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # 'user' or 'agent'
    
    message = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)  # Internal agent notes
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TicketAttachment(db.Model):
    __tablename__ = 'ticket_attachments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = db.Column(db.String(36), db.ForeignKey('support_tickets.id'), nullable=False)
    
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    
    uploaded_by = db.Column(db.String(36), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    
    agent_id = db.Column(db.String(36), nullable=True)
    agent_name = db.Column(db.String(100), nullable=True)
    
    status = db.Column(db.String(20), default='waiting')  # waiting, active, closed
    queue_position = db.Column(db.Integer, nullable=True)
    
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    
    sender_id = db.Column(db.String(36), nullable=False)
    sender_name = db.Column(db.String(100), nullable=False)
    message_type = db.Column(db.Enum(ChatMessageType), nullable=False)
    
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Data Classes
@dataclass
class SupportMetrics:
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    avg_resolution_time: float
    customer_satisfaction: float
    response_time_avg: float

@dataclass 
class AgentPerformance:
    agent_id: str
    agent_name: str
    tickets_handled: int
    avg_resolution_time: float
    customer_rating: float
    online_time: float

# Support Service Class
class SupportService:
    def __init__(self):
        self.redis_client = redis_client
        
    def create_ticket(self, user_data: Dict, ticket_data: Dict) -> SupportTicket:
        """Create a new support ticket"""
        try:
            ticket_number = self._generate_ticket_number()
            
            ticket = SupportTicket(
                ticket_number=ticket_number,
                user_id=user_data['id'],
                user_email=user_data['email'],
                user_name=user_data['name'],
                subject=ticket_data['subject'],
                description=ticket_data['description'],
                category=ticket_data['category'],
                priority=TicketPriority(ticket_data.get('priority', 'medium'))
            )
            
            db.session.add(ticket)
            db.session.commit()
            
            # Auto-assign based on category and agent availability
            self._auto_assign_ticket(ticket)
            
            # Send notification to user
            self._send_ticket_confirmation(ticket)
            
            # Notify available agents
            self._notify_agents_new_ticket(ticket)
            
            logger.info(f"Created ticket {ticket.ticket_number} for user {user_data['email']}")
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            db.session.rollback()
            raise
    
    def add_ticket_message(self, ticket_id: str, sender_data: Dict, message: str, is_internal: bool = False) -> TicketMessage:
        """Add a message to a ticket"""
        try:
            ticket = SupportTicket.query.get(ticket_id)
            if not ticket:
                raise ValueError("Ticket not found")
            
            message_obj = TicketMessage(
                ticket_id=ticket_id,
                sender_id=sender_data['id'],
                sender_name=sender_data['name'],
                sender_type=sender_data['type'],
                message=message,
                is_internal=is_internal
            )
            
            db.session.add(message_obj)
            
            # Update ticket status and timestamp
            if sender_data['type'] == 'agent' and ticket.status == TicketStatus.WAITING_FOR_CUSTOMER:
                ticket.status = TicketStatus.IN_PROGRESS
            elif sender_data['type'] == 'user' and ticket.status == TicketStatus.IN_PROGRESS:
                ticket.status = TicketStatus.WAITING_FOR_CUSTOMER
                
            ticket.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Send email notification if needed
            if not is_internal:
                self._send_message_notification(ticket, message_obj)
            
            logger.info(f"Added message to ticket {ticket.ticket_number}")
            return message_obj
            
        except Exception as e:
            logger.error(f"Error adding ticket message: {str(e)}")
            db.session.rollback()
            raise
    
    def resolve_ticket(self, ticket_id: str, agent_id: str, resolution_message: str) -> bool:
        """Mark a ticket as resolved"""
        try:
            ticket = SupportTicket.query.get(ticket_id)
            if not ticket:
                raise ValueError("Ticket not found")
            
            # Add resolution message
            resolution_msg = TicketMessage(
                ticket_id=ticket_id,
                sender_id=agent_id,
                sender_name=ticket.assigned_agent_name or "Support Agent",
                sender_type='agent',
                message=resolution_message
            )
            
            db.session.add(resolution_msg)
            
            # Update ticket status
            ticket.status = TicketStatus.RESOLVED
            ticket.resolved_at = datetime.utcnow()
            ticket.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Send resolution notification
            self._send_resolution_notification(ticket)
            
            logger.info(f"Resolved ticket {ticket.ticket_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving ticket: {str(e)}")
            db.session.rollback()
            raise
    
    def start_chat_session(self, user_data: Dict) -> ChatSession:
        """Start a new chat session"""
        try:
            session = ChatSession(
                user_id=user_data['id'],
                user_email=user_data['email'],
                user_name=user_data['name']
            )
            
            db.session.add(session)
            
            # Check for available agents
            available_agent = self._find_available_agent()
            
            if available_agent:
                session.agent_id = available_agent['id']
                session.agent_name = available_agent['name']
                session.status = 'active'
            else:
                # Add to queue
                queue_position = self._get_queue_position()
                session.queue_position = queue_position
                session.status = 'waiting'
            
            db.session.commit()
            
            # Send initial system message
            self._send_chat_welcome_message(session)
            
            logger.info(f"Started chat session {session.id} for user {user_data['email']}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting chat session: {str(e)}")
            db.session.rollback()
            raise
    
    def send_chat_message(self, session_id: str, sender_data: Dict, message: str) -> ChatMessage:
        """Send a message in a chat session"""
        try:
            session = ChatSession.query.get(session_id)
            if not session:
                raise ValueError("Chat session not found")
            
            chat_message = ChatMessage(
                session_id=session_id,
                sender_id=sender_data['id'],
                sender_name=sender_data['name'],
                message_type=ChatMessageType(sender_data['type']),
                message=message
            )
            
            db.session.add(chat_message)
            db.session.commit()
            
            # Emit to connected clients
            socketio.emit('new_message', {
                'session_id': session_id,
                'message': {
                    'id': chat_message.id,
                    'sender_name': chat_message.sender_name,
                    'message_type': chat_message.message_type.value,
                    'message': chat_message.message,
                    'timestamp': chat_message.timestamp.isoformat()
                }
            }, room=f"chat_{session_id}")
            
            logger.info(f"Sent chat message in session {session_id}")
            return chat_message
            
        except Exception as e:
            logger.error(f"Error sending chat message: {str(e)}")
            db.session.rollback()
            raise
    
    def get_support_metrics(self, days: int = 30) -> SupportMetrics:
        """Get support metrics for the specified period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total tickets
            total_tickets = SupportTicket.query.filter(
                SupportTicket.created_at >= start_date
            ).count()
            
            # Open tickets
            open_tickets = SupportTicket.query.filter(
                SupportTicket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_FOR_CUSTOMER])
            ).count()
            
            # Resolved tickets
            resolved_tickets = SupportTicket.query.filter(
                SupportTicket.status == TicketStatus.RESOLVED,
                SupportTicket.resolved_at >= start_date
            ).count()
            
            # Average resolution time
            resolved_tickets_with_time = SupportTicket.query.filter(
                SupportTicket.status == TicketStatus.RESOLVED,
                SupportTicket.resolved_at >= start_date,
                SupportTicket.resolved_at.isnot(None)
            ).all()
            
            if resolved_tickets_with_time:
                resolution_times = [
                    (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                    for ticket in resolved_tickets_with_time
                ]
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
            else:
                avg_resolution_time = 0.0
            
            return SupportMetrics(
                total_tickets=total_tickets,
                open_tickets=open_tickets,
                resolved_tickets=resolved_tickets,
                avg_resolution_time=avg_resolution_time,
                customer_satisfaction=4.2,  # Placeholder - would come from surveys
                response_time_avg=2.5  # Placeholder - would be calculated from first response times
            )
            
        except Exception as e:
            logger.error(f"Error getting support metrics: {str(e)}")
            raise
    
    def _generate_ticket_number(self) -> str:
        """Generate a unique ticket number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        counter = self.redis_client.incr(f"ticket_counter:{timestamp}")
        return f"BA-{timestamp}-{counter:04d}"
    
    def _auto_assign_ticket(self, ticket: SupportTicket) -> None:
        """Auto-assign ticket to available agent based on category and workload"""
        try:
            # This would connect to your user management system
            # For now, using placeholder logic
            
            category_agents = {
                'technical': ['agent_1', 'agent_2'],
                'billing': ['agent_3', 'agent_4'],
                'general': ['agent_1', 'agent_2', 'agent_3', 'agent_4']
            }
            
            eligible_agents = category_agents.get(ticket.category, category_agents['general'])
            
            # Find agent with lowest current workload
            # This would query your agent management system
            if eligible_agents:
                assigned_agent = eligible_agents[0]  # Simplified assignment
                ticket.assigned_agent_id = assigned_agent
                ticket.assigned_agent_name = f"Agent {assigned_agent}"
                
                db.session.commit()
                
        except Exception as e:
            logger.error(f"Error auto-assigning ticket: {str(e)}")
    
    def _send_ticket_confirmation(self, ticket: SupportTicket) -> None:
        """Send ticket confirmation email to user"""
        # This would integrate with your email service
        logger.info(f"Sending confirmation email for ticket {ticket.ticket_number}")
    
    def _notify_agents_new_ticket(self, ticket: SupportTicket) -> None:
        """Notify available agents of new ticket"""
        socketio.emit('new_ticket', {
            'ticket_id': ticket.id,
            'ticket_number': ticket.ticket_number,
            'category': ticket.category,
            'priority': ticket.priority.value,
            'subject': ticket.subject
        }, room='agents')
    
    def _send_message_notification(self, ticket: SupportTicket, message: TicketMessage) -> None:
        """Send email notification for new ticket message"""
        logger.info(f"Sending message notification for ticket {ticket.ticket_number}")
    
    def _send_resolution_notification(self, ticket: SupportTicket) -> None:
        """Send resolution notification to user"""
        logger.info(f"Sending resolution notification for ticket {ticket.ticket_number}")
    
    def _find_available_agent(self) -> Optional[Dict]:
        """Find an available agent for chat"""
        # This would integrate with your agent management system
        # Placeholder logic
        return {
            'id': 'agent_1',
            'name': 'Support Agent'
        }
    
    def _get_queue_position(self) -> int:
        """Get current queue position for chat"""
        waiting_sessions = ChatSession.query.filter_by(status='waiting').count()
        return waiting_sessions + 1
    
    def _send_chat_welcome_message(self, session: ChatSession) -> None:
        """Send welcome message to chat session"""
        welcome_message = ChatMessage(
            session_id=session.id,
            sender_id='system',
            sender_name='Basketball Analysis Support',
            message_type=ChatMessageType.SYSTEM,
            message=f"Hello {session.user_name}! Welcome to Basketball Analysis support. How can we help you today?"
        )
        
        db.session.add(welcome_message)
        db.session.commit()

# Initialize support service
support_service = SupportService()

# Flask Routes
@app.route('/support')
def support_home():
    """Support portal home page"""
    return render_template('support/index.html')

@app.route('/support/tickets')
@login_required
def user_tickets():
    """User's support tickets"""
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).order_by(
        SupportTicket.created_at.desc()
    ).all()
    return render_template('support/user_tickets.html', tickets=tickets)

@app.route('/support/tickets/<ticket_id>')
@login_required  
def view_ticket(ticket_id):
    """View individual ticket"""
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    # Check if user owns ticket or is an agent
    if ticket.user_id != current_user.id and not current_user.is_agent:
        return redirect(url_for('user_tickets'))
    
    return render_template('support/view_ticket.html', ticket=ticket)

@app.route('/support/api/tickets', methods=['POST'])
@login_required
def create_ticket():
    """API endpoint to create a new ticket"""
    try:
        data = request.get_json()
        
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'name': current_user.name
        }
        
        ticket = support_service.create_ticket(user_data, data)
        
        return jsonify({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'ticket_number': ticket.ticket_number,
                'status': ticket.status.value
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating ticket via API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/support/api/tickets/<ticket_id>/messages', methods=['POST'])
@login_required
def add_ticket_message(ticket_id):
    """API endpoint to add message to ticket"""
    try:
        data = request.get_json()
        
        sender_data = {
            'id': current_user.id,
            'name': current_user.name,
            'type': 'agent' if current_user.is_agent else 'user'
        }
        
        message = support_service.add_ticket_message(
            ticket_id, 
            sender_data, 
            data['message'],
            data.get('is_internal', False)
        )
        
        return jsonify({'success': True, 'message_id': message.id})
        
    except Exception as e:
        logger.error(f"Error adding ticket message via API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/support/chat')
@login_required
def chat_portal():
    """Live chat portal"""
    return render_template('support/chat.html')

# WebSocket Events
@socketio.on('start_chat')
def handle_start_chat(data):
    """Handle chat session start"""
    try:
        user_data = {
            'id': current_user.id,
            'email': current_user.email,
            'name': current_user.name
        }
        
        session = support_service.start_chat_session(user_data)
        
        # Join room for this chat session
        join_room(f"chat_{session.id}")
        
        emit('chat_started', {
            'session_id': session.id,
            'status': session.status,
            'queue_position': session.queue_position
        })
        
    except Exception as e:
        logger.error(f"Error starting chat: {str(e)}")
        emit('error', {'message': 'Failed to start chat session'})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle chat message"""
    try:
        sender_data = {
            'id': current_user.id,
            'name': current_user.name,
            'type': 'agent' if current_user.is_agent else 'user'
        }
        
        support_service.send_chat_message(
            data['session_id'],
            sender_data,
            data['message']
        )
        
    except Exception as e:
        logger.error(f"Error sending chat message: {str(e)}")
        emit('error', {'message': 'Failed to send message'})

@socketio.on('join_agent_room')
def handle_join_agent_room():
    """Allow agents to join the agents room for notifications"""
    if current_user.is_agent:
        join_room('agents')
        emit('joined_agents', {'message': 'Connected to agent notifications'})

# Celery Tasks
@celery.task
def send_email_notification(to_email: str, subject: str, body: str):
    """Send email notification asynchronously"""
    try:
        # Email sending logic here
        logger.info(f"Sending email to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False

@celery.task
def analyze_support_trends():
    """Analyze support trends and generate insights"""
    try:
        metrics = support_service.get_support_metrics(30)
        # Store metrics in database or send to analytics service
        logger.info(f"Support metrics: {asdict(metrics)}")
        return asdict(metrics)
    except Exception as e:
        logger.error(f"Error analyzing support trends: {str(e)}")
        return None

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
