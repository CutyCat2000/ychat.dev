from config import NAME, WEBSITE, ICON

def config(request):
    return {
        'NAME': NAME,
        'ICON': ICON,
        'WEBSITE': WEBSITE,
    }