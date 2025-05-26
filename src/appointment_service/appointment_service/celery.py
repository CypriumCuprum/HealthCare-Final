import os
from django.conf import settings

# Tạo dummy app để tránh lỗi import
class DummyCeleryApp:
    def __init__(self, *args, **kwargs):
        pass
        
    def config_from_object(self, *args, **kwargs):
        pass
        
    def autodiscover_tasks(self, *args, **kwargs):
        pass
        
    def task(self, *args, **kwargs):
        # Decorator giả để thay thế @app.task, trả về chính hàm đó
        def decorator(func):
            return func
        return decorator
    
    # Thêm shared_task giả
    def shared_task(self, *args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Tạo instance của lớp giả
app = DummyCeleryApp('appointment_service')

# Thêm dummy attributes để tránh lỗi khi code khác tham chiếu
app.conf = type('obj', (object,), {
    'beat_schedule': {},
    'task_routes': {}
})

# Định nghĩa lại hàm task
def shared_task(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

# Dummy debug_task
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Debug task simulated')