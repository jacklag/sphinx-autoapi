.. js:class:: {{ obj.name }}(
{%- for param in obj.parameters %}
   {{- param.name }}
   {%- if param.type %}: {{ param.type }}{%- endif %}
   {%- if param.optional %} = {{ param.defaultvalue }}{% endif %}
   {{- ", " if not loop.last }}
{%- endfor %}
)

   {% if obj.docstring %}

   .. rubric:: Summary

   {{ obj.docstring|indent(3) }}

   {% endif %}

   {% if obj.methods %}

   {% for method in obj.methods %}

   {% macro render() %}{{ method.render() }}{% endmacro %}
   {{ render()|indent(3) }}

   {%- endfor %}

   {% endif %}
