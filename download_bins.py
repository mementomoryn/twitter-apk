import requests
import re
from config import LSPATCH_REPOSITORY, APKEDITOR_REPOSITORY, MANIFESTEDITOR_REPOSITORY
from config import REVANCED_PATCH_VERSION, REVANCED_INTEGRATION_VERSION, REVANCED_CLI_VERSION, XPOSED_MODULE_VERSION
from constants import HEADERS
from utils import panic, exe_permission, extract_archive, download

def download_release_asset(repo: str, regex: str, prerelease: bool, out_dir: str, filename=None, version=None):
    url = f"https://api.github.com/repos/{repo}/releases"

    if prerelease is False and not version:
        url += "/latest"
    
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch github")

    if version:
        response = [i for i in response.json() if prerelease is False]
        release = [i for i in response if i["tag_name"] == version][0]
        
        if len(release) == 0:
            raise Exception(f"No release found for version {version} on {repo}")
    elif prerelease is True:
        release = response.json()[0]
    else:
        release = response.json()
        
    if not release:
        raise Exception(f"No release found for {repo}")



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


def download_manifesteditor():
    print("Downloading manifesteditor")
    download_release_asset(MANIFESTEDITOR_REPOSITORY, "ManifestEditor", False, "bins", "manifesteditor.jar")
    
    
def download_apkeditor():
    print("Downloading apkeditor")
    download_release_asset(APKEDITOR_REPOSITORY, "APKEditor", False, "bins", "apkeditor.jar")


def download_lspatch():
    print("Downloading lspatch")
    download_artifact_asset(LSPATCH_REPOSITORY, "lspatch-release", r"^jar-.*.jar", "lspatch", 4, False, "bins", "lspatch-archive", "lspatch.jar", "lspatch.zip")


def download_xposed_bins(repo_url: str, regex: str, prerelease: bool = False):
    print("Downloading xposed")
    download_release_asset(repo_url, regex, prerelease, "bins", "xposed.apk", XPOSED_MODULE_VERSION)


def download_revanced_bins(repo_url: str, type: str, prerelease: bool = False):
    match type:
        case "cli":
            print("Downloading cli")
            regex = r"^.*-cli-.*\.jar$"
            output = "cli.jar"
            version = REVANCED_CLI_VERSION
        case "patch":
            print("Downloading patches")
            regex = r"^.*-patches-.*\.jar$"
            output = "patches.jar"
            version = REVANCED_PATCH_VERSION
        case "integration":
            print("Downloading integrations")
            regex = r"^.*-integrations-.*\.apk$"
            output = "integrations.apk"
            version = REVANCED_INTEGRATION_VERSION
        case _:
            panic("Assets bin type is not recognized")

    download_release_asset(repo_url, regex, prerelease, "bins", output, version)


if __name__ == "__main__":
   download_apkeditor()
