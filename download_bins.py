import requests
import re
import os
import shutil
from constants import HEADERS
from utils import panic, download

def download_release_asset(repo: str, regex: str, prerelease: bool, out_dir: str, filename=None):
    url = f"https://api.github.com/repos/{repo}/releases"

    if prerelease is False:
        url += "/latest"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch github")

    if prerelease is True:
        release = response.json()[0]
    else:
        release = response.json()

    link = None
    for i in release["assets"]:
        if re.search(regex, i["name"]):
            link = i["browser_download_url"]
            if filename is None:
                filename = i["name"]
            break

    download(link, f"{out_dir.lstrip("/")}/{filename}")


def download_artifact_asset(repo: str, regex: str, count: int, out_dir: str, dirname: str, filename: str, zipname=None):
    url = f"https://api.github.com/repos/{repo}/actions/artifacts?per_page={count}"
    full_dirname = f"{out_dir.lstrip("/")}/{dirname}"
    full_filename = f"{out_dir.lstrip("/")}/{filename}"
    full_zipname = f"{out_dir.lstrip("/")}/{zipname}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch github")

    link = None
    for i in response.json()["artifacts"]:
        if re.search(regex, i["name"]) and i["expired"] is False:
            link = i["archive_download_url"]

            HEADERS.update({f"authorization: Bearer {os.environ["GH_TOKEN"]}"})
            artifact_response = request.get(link, HEADERS)
            if artifact_response.status_code != 302:
                raise Exception("Failed to fetch artifacts")

            if zipname is None:
                zipname = i["name"] + ".zip"
            break

    download(link, full_zipname)

    shutil.unpack_archive(full_zipname, full_dirname)

    os.remove(full.zipname)

    for file in os.listdir(full_dirname):
        if re.search(r"^jar-.*.jar", file):
            if os.path.exists(full_filename):
                os.unlink(full_filename)
            os.rename(f"{out_dir.lstrip("/")}/{file}", full_filename)

    shutil.rmtree(full_dirname)

def download_apkeditor():
    print("Downloading apkeditor")
    download_release_asset("REAndroid/APKEditor", "APKEditor", False, "bins", "apkeditor.jar")


def download_lspatch():
    print("Downloading lspatch")
    download_artifact_asset("JingMatrix/LSPatch", "lspatch-release", 4, "bins", "lspatch", "lspatch.jar", "lspatch.zip")


def download_xposed_bins(repo_url: str, regex: str, prerelease: bool = False):
    print("Downloading xposed")
    download_release_asset(repo_url, regex, prerelease, "bins", "xposed.apk")


def download_revanced_bins(repo_url: str, type: str, prerelease: bool = False):
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
