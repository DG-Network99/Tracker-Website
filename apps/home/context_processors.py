from .mongo_db import get_all_notifications

def header_notifications(request):
    if request.user.is_authenticated:
        data = get_all_notifications(request.user.email)
        # print(data)
        last_five_notifications = data[-5:]
        new_notification_count = sum(1 for item in last_five_notifications if item.get('is_read') == False) 
        return {'notifications': last_five_notifications[::-1], 'new_notification_count': new_notification_count}
    else:
        return {'notifications': None}