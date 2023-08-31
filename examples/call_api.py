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

    # Retrieve the token
    AUTH_TOKEN = config("AUTH_TOKEN")

    # Construct the endpoint url
    endpoint_url = os.path.join(URL, "image")

    # Make the request
    response = requests.get(
        endpoint_url,
        params={"code": code, "style": style},
        headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
    )
    
    # If call was successful, retrieve the image
    if response.status_code == 200:
        
        # Retrieve the image bytes
        image_bytes = response.content
        
        # Save image locally
        Image.open(io.BytesIO(image_bytes)).save(save_path)
        
    else:
        # Print the logs of the errors
        print(response.status_code)
        print(response.text)

if __name__ == "__main__":
    typer.run(main)
