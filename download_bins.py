import requests
import re
from utils import panic, download

def download_release_asset(repo: str, regex: str, prerelease: bool, out_dir: str, filename=None):
    url = f"https://api.github.com/repos/{repo}/releases"

    if prerelease is False:
        url += "/latest"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch github")

    if prerelease is True:
        assets = response.json()[0]["assets"]
    else:
        assets = response.json()["assets"]

    link = None
    for i in assets:
        if re.search(regex, i["name"]):
            link = i["browser_download_url"]
            if filename is None:
                filename = i["name"]
            break

    download(link, f"{out_dir.lstrip("/")}/{filename}")


def download_apkeditor():
    print("Downloading apkeditor")
    download_release_asset("REAndroid/APKEditor", "APKEditor", "bins", "apkeditor.jar")


def download_revanced_bins(repo_url: str, type: str, prerelease: bool):
    match type:
        case "cli":
            print("Downloading cli")
            regex = r"^.*-cli-.*\.jar$"
            output = "cli.jar"
        case "patch":
            print("Downloading patches")
            regex = r"^.*-patches-.*\.jar$"
            output = "patches.jar"
        case "integration":
            print("Downloading integrations")
            regex = r"^.*-integrations-.*\.apk$"
            output = "integrations.apk"
        case _:
            panic("Assets bin type is not recognized")

    download_release_asset(repo_url, regex, prerelease, "bins", output)


if __name__ == "__main__":
   download_apkeditor()
   download_revanced_bins(cli_url, "cli")
   download_revanced_bins(patch_url, "patches")
   download_revanced_bins(integration_url, "integrations")
