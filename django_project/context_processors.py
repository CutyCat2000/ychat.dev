from config import NAME, WEBSITE, ICON, EMOJIS


def config(request):
    return {
        'NAME': NAME,
        'ICON': ICON,
        'WEBSITE': WEBSITE,
        'EMOJIS': EMOJIS
    }
