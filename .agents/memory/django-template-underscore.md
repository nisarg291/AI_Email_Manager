---
name: Django template underscore variable restriction
description: Django template engine raises TemplateSyntaxError for context variables starting with underscore. Affects context processors and any template variables.
---

Django's template engine raises `TemplateSyntaxError: Variables and attributes may not begin with underscores` when you try to use a context variable like `_global_active_job` in `{% if %}` or any other template tag.

**Why:** Django's template layer intentionally blocks underscore-prefixed names to prevent access to private Python attributes.

**How to apply:** Context processor keys must not start with `_`. Use descriptive plain names like `global_active_job` instead of `_global_active_job`. The same rule applies to any variable passed via `render()` context if it will be used in template tags (not just `{{ }}` output).
