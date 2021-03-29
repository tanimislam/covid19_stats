"""
rstjinja    
~~~~~~~~~~~~~~~~~

I follow instructions without deep insight or contextual understanding, from https://www.ericholscher.com/blog/2016/jul/25/integrating-jinja-rst-sphinx. Objective is to create an extension that does Jinja replacement in my RST documentation files when I sphinx-build HTML documentation.
"""

def rstjinja(app, docname, source):
    """
    Render our pages as a jinja template for fancy templating goodness.
    """
    # Make sure we're outputting HTML
    if app.builder.format != 'html': return
    src = source[0]
    rendered = app.builder.templates.render_string(
        src, app.config.html_context
    )
    source[0] = rendered

def setup( app ):
    app.connect( "source-read", rstjinja )
