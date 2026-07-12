from flask import render_template, request, redirect, url_for, jsonify
from src.models import db, Todo
from sqlalchemy import text
import json
from datetime import datetime

class JSONLogger:
    @staticmethod
    def log(level, event, **kwargs):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'event': event,
            **kwargs
        }
        print(json.dumps(log_entry))

def init_routes(app):
    
    @app.route('/')
    def index():
        todos = Todo.query.order_by(Todo.created_at.desc()).all()
        return render_template('index.html', todos=todos)
    
    @app.route('/add', methods=['POST'])
    def add_todo():
        title = request.form.get('title', '').strip()
        if title:
            todo = Todo(title=title)
            db.session.add(todo)
            db.session.commit()
            JSONLogger.log('info', 'task_created', task_id=todo.id, title=title)
        return redirect(url_for('index'))
    
    @app.route('/toggle/<int:task_id>', methods=['POST'])
    def toggle_todo(task_id):
        todo = Todo.query.get_or_404(task_id)
        todo.is_done = not todo.is_done
        db.session.commit()
        JSONLogger.log('info', 'task_toggled', task_id=task_id, new_status=todo.is_done)
        return redirect(url_for('index'))
    
    @app.route('/delete/<int:task_id>', methods=['POST'])
    def delete_todo(task_id):
        todo = Todo.query.get_or_404(task_id)
        db.session.delete(todo)
        db.session.commit()
        JSONLogger.log('info', 'task_deleted', task_id=task_id)
        return redirect(url_for('index'))
    
    @app.route('/health')
    def health():
        try:
            # Исправлено: используем text() для SQL-выражения
            db.session.execute(text('SELECT 1'))
            return jsonify({'status': 'ok'}), 200
        except Exception as e:
            JSONLogger.log('error', 'health_check_failed', error=str(e))
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 503
