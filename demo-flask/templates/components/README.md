# Reusable Components

This directory contains reusable Jinja2 template components for the SAML SP demo application.

## Tooltip Component

The `tooltip.html` component provides a reusable tooltip that can be used throughout the application.

### Usage

1. Import the component in your template:
```jinja2
{% from "components/tooltip.html" import tooltip %}
```

2. Use the tooltip in your HTML:
```jinja2
<div class="flex items-center">
  <label for="field_name" class="block text-sm font-medium text-gray-700">Field Label</label>
  {{ tooltip("Your tooltip text here") }}
</div>
```

### Parameters

- `text` (required): The tooltip text to display
- `max_width` (optional): CSS class for maximum width. Defaults to "max-w-xs"

### Examples

Basic usage:
```jinja2
{{ tooltip("Simple tooltip text") }}
```

With custom max width:
```jinja2
{{ tooltip("Longer tooltip text that needs more space", "max-w-sm") }}
```

### Features

- Hover to show/hide
- Responsive positioning
- Consistent styling with the application theme
- Accessible with proper ARIA attributes
- Smooth fade in/out animations 