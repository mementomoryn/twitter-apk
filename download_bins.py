import requests
import re
import shutil
from config import LSPATCH_REPOSITORY, APKEDITOR_REPOSITORY
from constants import HEADERS
from utils import panic, exe_permission, extract_archive, download

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


def download_artifact_asset(repo: str, artifact_regex: str, archive_regex: str, release_regex: str, count: int, keep_dir: bool, out_dir: str, dirname: str, filename: str, zipname=None):
    url = f"https://api.github.com/repos/{repo}/actions/artifacts?per_page={count}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch github")

    link = None
    for i in response.json()["artifacts"]:
        if re.search(artifact_regex, i["name"]) and i["expired"] is False:
            link = i["archive_download_url"]

            if zipname is None:
                zipname = i["name"] + ".zip"
            break

    if link is not None:
        zip_path = f"{out_dir.lstrip("/")}/{zipname}"
        dir_path = f"{out_dir.lstrip("/")}/{dirname}"
        file_path = f"{out_dir.lstrip("/")}/{filename}"

        download(link, zip_path, HEADERS)

        extract_archive(zip_path, dir_path, file_path, archive_regex, keep_dir)
    else:
        download_release_asset(repo, release_regex, False, out_dir, filename)


def download_apkeditor():
    print("Downloading apkeditor")
    download_release_asset(APKEDITOR_REPOSITORY, "APKEditor", False, "bins", "apkeditor.jar")


def download_lspatch():
    print("Downloading lspatch")
    download_artifact_asset(LSPATCH_REPOSITORY, "lspatch-release", r"^jar-.*.jar", "lspatch", 4, False, "bins", "lspatch-archive", "lspatch.jar", "lspatch.zip")


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
