import os
import re
import shutil
import requests
import subprocess
import sys
from github import get_last_build_version


def panic(message: str):
    print(message, file=sys.stderr)
    exit(1)


def send_message(message: str, token: str, chat_id: str, thread_id: str):
    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"

    data = {
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
        "text": message,
        "message_thread_id": thread_id,
        "chat_id": chat_id,
    }

    requests.post(endpoint, data=data)


def previous_version(index: int, changelog: str) -> str:
    body: str = changelog.body
    splitline = body.splitlines()
    remove = list(filter(None, splitline))
    find: str = remove[index]
    version: str = find.split(": ")[1]

    return version


def format_changelog(changelog: str, sections: bool) -> str:
    if sections is False:
        replace: str = changelog.replace("# ", "### ")
        loglist: str = "\r\n\r\n".join(replace.split("\r\n\r\n")[:-3]).split("### ")[1:]
    else:
        loglist: str = changelog.split("### ")[1:]
    append: str = ["### " + log for log in loglist]
    join: str = ''.join(append)

    return join


def report_to_telegram(patch_url: str, integration_url: str, xposed_url: str, prerelease: bool):
    tg_token = os.environ["TG_TOKEN"]
    tg_chat_id = os.environ["TG_CHAT_ID"]
    tg_thread_id = os.environ["TG_THREAD_ID"]
    repo_url: str = os.environ["CURRENT_REPOSITORY"]
    release = get_last_build_version(repo_url, prerelease)

    if release is None:
        raise Exception("Could not fetch release")

    downloads = [
        f"[{asset.name}]({asset.browser_download_url})" for asset in release.assets
    ]

    if prerelease is False:
        message_title: str = "New Release Update !"
    else:
        message_title: str = "New Pre-release Update !"

    message = f"""
[{message_title}]({release.html_url})

Patches -> {patch_url}@{previous_version(0, release)}
Integrations -> {integration_url}@{previous_version(1, release)}
Xposed -> {xposed_url}@{previous_version(2, release)}

▼ Downloads ▼

{"\n\n".join(downloads)}
"""

    print(message)

    send_message(message, tg_token, tg_chat_id, tg_thread_id)


def extract_archive(zip_path: str, dir_path: str, file_path: str, regex: str, keep_dir: bool, out_dir: str = None, folders: str = None):
    if out_dir is None and folders is None:
        shutil.unpack_archive(zip_path, dir_path)
    else:
        shutil.unpack_archive(zip_path, out_dir)
        os.rename(f"{out_dir}.lstrip('/')/{folders}", dir_path)

    os.remove(zip_path)

    for i in os.listdir(dir_path):
        if re.search(regex, i):
            if os.path.exists(file_path):
                os.unlink(file_path)
            os.rename(f"{dir_path}/{i}", file_path)

    if keep_dir is False:
        shutil.rmtree(dir_path)


def download(link, out, headers=None):
    if os.path.exists(out):
        print(f"{out} already exists skipping download")
        return

    # https://www.slingacademy.com/article/python-requests-module-how-to-download-files-from-urls/#Streaming_Large_Files
    with requests.get(link, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def run_command(command: list[str]):
    cmd = subprocess.run(command, capture_output=True, shell=True)

    try:
        cmd.check_returncode()
    except subprocess.CalledProcessError:
        print(cmd.stdout)
        print(cmd.stderr)
        exit(1)


def merge_apk(path: str):
    subprocess.run(
        ["java", "-jar", "./bins/apkeditor.jar", "m", "-i", path]
    ).check_returncode()


def move_merged_apk(
    apk: str,
    out: str,
    files: list | None = None
):
    if os.path.exists(out):
        os.unlink(out)
    shutil.move(apk, out)

    if files is not None:
        files.append(out)


def patch_revanced_apk(
    cli: str,
    integrations: str,
    patches: str,
    apk: str,
    includes: list[str] | None = None,
    excludes: list[str] | None = None,
    riparch: list[str] | None = None,
    exclusive: bool | None = None,
    out: str | None = None,
    files: list | None = None
):
    keystore_password = os.environ["KEYSTORE_PASSWORD"]
    keystore_alias = os.environ["KEYSTORE_ALIAS"]
    
    command = [
        "java",
        "-jar",
        cli,
        "patch",
        "-b",
        patches,
        "-m",
        integrations,
        "--keystore",
        "bks.keystore",
        "--keystore-entry-password",
        keystore_password,
        "--keystore-password",
        keystore_password,
        "--signer",
        "mementomoryn",
        "--keystore-entry-alias",
        keystore_alias
    ]

    if riparch is not None:
        for r in riparch:
            command.append("--rip-lib")
            command.append(r)

    if includes is not None:
        for i in includes:
            command.append("-i")
            command.append(i)

    if exclusive is True:
        command.append("--exclusive")
    elif excludes is not None:
        for e in excludes:
            command.append("-e")
            command.append(e)

    command.append(apk)

    subprocess.run(command).check_returncode()

    # remove -patched from the apk to match out
    if out is not None:
        cli_output = f"{str(apk).removesuffix(".apk")}-patched.apk"
        if os.path.exists(out):
            os.unlink(out)
        shutil.move(cli_output, out)

    if files is not None:
        files.append(out)


def patch_xposed_apk(
    lspatch: str,
    xposed: str,
    apk: str,
    out_dir: str,
    out: str | None = None,
    files: list | None = None
):
    keystore_password = os.environ["KEYSTORE_PASSWORD"]
    keystore_alias = os.environ["KEYSTORE_ALIAS"]
    
    command = [
        "java",
        "-jar",
        lspatch,
        "--embed",
        xposed,
        "--keystore",
        "jks.keystore",
        keystore_password,
        keystore_alias,
        keystore_password,
        "--output",
        out_dir
    ]

    command.append(apk)

    subprocess.run(command).check_returncode()

    if out is not None:
        patch_output = os.listdir(out_dir)[0]
        if os.path.exists(out):
            os.unlink(out)
        shutil.move(os.path.join(out_dir, patch_output), os.getcwd())
        os.rename(patch_output, out)
        os.rmdir(out_dir)

    if files is not None:
        files.append(out)


def publish_release(notes: str, prerelease: bool, files: list[str]):
    key = os.environ.get("GH_TOKEN")
    if key is None:
        raise Exception("GH_TOKEN is not set")

    release_version = os.environ["RELEASE_VERSION"]
    prerelease_version = os.environ["PRERELEASE_VERSION"]

    command = ["gh", "release", "create", "-n", notes, "-t"]

    if prerelease is True:
        command.append(prerelease_version)
        command.append(prerelease_version)
        command.append("--prerelease")
    else:
        command.append(release_version)
        command.append(release_version)
        command.append("--latest")

    if len(files) == 0:
        raise Exception("Files should have atleast one item")

    for file in files:
        command.append(file)

    subprocess.run(command, env=os.environ.copy()).check_returncode()
