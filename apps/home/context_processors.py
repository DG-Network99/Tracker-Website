from .mongo_db import get_all_notifications

def header_notifications(request):
    if request.user.is_authenticated:
        data = get_all_notifications(request.user.email)
        # print(data)
        last_five_notifications = data[-5:]
        return {'notifications': last_five_notifications[::-1]}
    else:
        return {'notifications': None}