.. js:method:: {{ obj.name }}(
{%- for param in obj.parameters %}
   {{- param.name }}
   {%- if param.type %}: {{ param.type }}{%- endif %}
   {%- if param.optional %} = {{ param.defaultvalue }}{% endif %}
   {{- ", " if not loop.last }}
{%- endfor %}
)

{% if obj.docstring %}
   {{ obj.docstring|indent(3) }}
{% endif %}

{% for param in obj.parameters %}
   {{ param.name }}
   {%- if param.type %}: {{ param.type }}{%- endif %}
   {%- if param.optional %} = {{ param.defaultvalue }}{% endif %}
   {{- " " }}{{- param.description }}
{% endfor %}
