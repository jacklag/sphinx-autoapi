{# Identention in this file is important #}

{% if is_method %}
{# Slice self off #}
.. js:method:: {{ obj.name }}({{ obj.args|join(',') }})
{% else %}
.. js:function:: {{ obj.name }}({{ obj.args|join(',') }})
{% endif %}

   {% if obj.docstring %}
   {{ obj.docstring|indent(3) }}
   {% endif %}
