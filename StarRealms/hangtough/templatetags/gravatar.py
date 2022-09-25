import hashlib
from django import template
from django.utils.safestring import mark_safe
from urllib.parse import urlencode

register = template.Library()


# return only the URL of the gravatar
# TEMPLATE USE:  {{ email|gravatar_url:150 }}
@register.filter
def gravatar_url(email, size=40):
    default = "robohash"
    return "https://www.gravatar.com/avatar/%s?%s" % \
           (hashlib.md5(email.lower().encode()).hexdigest(), urlencode({'d': default, 's': str(size)}))


# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def gravatar(email, size=40):
    url = gravatar_url(email, size)
    return mark_safe('<img src="%s" height="%d" width="%d" class="rounded-circle me-2"/>' % (url, size, size))
