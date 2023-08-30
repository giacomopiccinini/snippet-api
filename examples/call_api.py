import requests
import typer
import os
import io
import PIL.Image as Image

from decouple import config


def main(
    code: str = "print('Hello World!')",
    style: str = "monokai",
    save_path: str = "snippet.png",
) -> None:
    """Call the API and save the image locally"""

    # Retrieve the URL from the environment variable
    URL = config("URL")

    # Construct the endpoint url
    endpoint_url = os.path.join(URL, "image")

    # Make the request
    image_bytes = requests.get(
        endpoint_url, params={"code": code, "style": style}
    ).content

    # Save image locally
    Image.open(io.BytesIO(image_bytes)).save(save_path)


if __name__ == "__main__":
    typer.run(main)
