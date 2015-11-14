import os
import sys

import requests

PER_PAGE = 25  # number of images returned per page


def get_image_id(image_name):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(os.environ["DIGITALOCEAN_TOKEN"])
    }
    url = "https://api.digitalocean.com/v2/images?private=true&per_page={}&page=1".format(PER_PAGE)

    while True:
        r = requests.get(url, headers=headers)
        json_data = r.json()
        for image in json_data["images"]:
            if image["name"] == image_name:
                return image["id"]
        if not json_data["links"]["pages"].get("next"):
            return "Couldn't find the image '{}'. I'm so sorry. You might have copied the image name wrong, or the image may not have finished saving.".format(image_name)
        url = json_data["links"]["pages"]["next"]


if __name__ == "__main__":
    print get_image_id(sys.argv[1])
