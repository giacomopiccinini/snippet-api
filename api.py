import modal
from modal import stub, wsgi_app

# Initialise Modal stub (necessary for using Modal)
stub = modal.Stub("snippet-api")

# Create image (Docker-like) to be used by Modal backend
image = modal.Image.debian_slim(python_version="3.10")

# Pip install packages
image = image.pip_install(
    "Flask",
    "playwright",
    "Pygments",
)

# Install playwright and its dependencies
image = image.run_commands(
    ["python -m playwright install", "python -m playwright install-deps"]
)

# Copy the static directory with CSS
image = image.copy_local_dir(
    local_path="static",
    remote_path=f"/root/static",
)

# Copy the templates directory with HTML (Jinja2)
image = image.copy_local_dir(
    local_path="templates",
    remote_path=f"/root/templates",
)

# Assign image to stub
stub.image = image


@stub.function(image=image, secret=modal.Secret.from_name("snippet-secret"))
@wsgi_app()
def snippet_app():
    from flask import Flask, render_template, request, url_for
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import Python3Lexer
    from playwright.sync_api import sync_playwright

    # Instantiate the Flask app
    app = Flask("website")

    @app.route("/snippet", methods=["GET"])
    def snippet():
        """
        Render an image of the provided snippet
        """

        # Get the code from the request
        code = request.args.get("code")
        code = code or "print('Hello, World!')"

        # Get the style from the request
        style = request.args.get("style")
        style = style or "monokai"

        # Init the formatter. This is used to wrap up the Python code in HTML and use a particular style
        # In the context we shall make use of this formatter to infer the details of the style
        # such as background colour, font, etc.
        formatter = HtmlFormatter(style=style)

        # Context for rendering the page
        context = {
            "style_definitions": formatter.get_style_defs(),  # Get the definition of the style
            "style_bg_color": formatter.style.background_color,  # Get the background colour of the style
            "highlighted_code": highlight(
                code, Python3Lexer(), formatter
            ),  # Get the actual code
        }

        return render_template("snippet.html", **context)

    @app.route("/image", methods=["GET"])
    def screenshot():
        # Get the code from the request
        code = request.args.get("code")
        code = code or "print('Hello, World!')"

        # Get the style from the request
        style = request.args.get("style")
        style = style or "monokai"

        # Set up context manager, which will automatically close the browser
        with sync_playwright() as playwright:
            # Create the url
            url = request.host_url + url_for("snippet", code=code, style=style)

            # Launch the headless browser
            webkit = playwright.webkit
            browser = webkit.launch()

            # Create a new context.
            # The scale factor ensures that the picture is not pixelated
            browser_context = browser.new_context(device_scale_factor=2)

            # Open a new browser page
            page = browser_context.new_page()

            # Visits the given URL
            page.goto(url)

            # Takes a screenshot of the element with a code class
            screenshot_bytes = page.locator(".code").screenshot()

            # Close the browser
            browser.close()

            # Return the image buffer
            return screenshot_bytes

    return app
