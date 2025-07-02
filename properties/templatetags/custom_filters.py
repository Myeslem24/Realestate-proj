from django import template

register = template.Library()

@register.filter
def get_year_range(end, start):
    """
    يُستخدم في القالب كـ: {% for y in 2025|get_year_range:1980 %}
    ويُرجع قائمة من السنوات من start إلى end (مثلاً: [1980, ..., 2025])
    """
    try:
        return list(range(int(start), int(end) + 1))[::-1]
    except:
        return []
