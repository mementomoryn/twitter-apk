from apkmirror import Version, Variant
from build_variants import build_apks
from download_bins import download_apkeditor, download_revanced_bins
import github
from utils import panic, merge_apk, publish_release, report_to_telegram
import apkmirror
import os


def get_latest_release(versions: list[Version]) -> Version | None:
    for i in versions:
        if i.version.find("release") >= 0:
            return i


def main():
    # get latest version
    url: str = "https://www.apkmirror.com/apk/x-corp/twitter/"
    repo_url: str = os.environ["CURRENT_REPOSITORY"]
    patch_url: str = "crimera/piko"
    integration_url: str = "crimera/revanced-integrations"

    versions = apkmirror.get_versions(url)

    latest_version = get_latest_release(versions)
    if latest_version is None:
        raise Exception("Could not find the latest version")

    latest_version = latest_version

    # only continue if it's a release
    if latest_version.version.find("release") < 0:
        panic("Latest version is not a release version")

    last_build_version: github.GithubRelease | None = github.get_last_build_version(
        repo_url
    )
    count_releases: int | None = github.count_releases(
        repo_url
    )
    if last_build_version is None and count_releases is None:
        panic("Failed to fetch the latest build version")
        return

    last_patch_version: github.GithubRelease | None = github.get_last_build_version(
        patch_url
    )
    if last_patch_version is None:
        panic("Failed to fetch the latest patch version")
        return

    last_integration_version: github.GithubRelease | None = github.get_last_build_version(
        integration_url
    )
    if last_integration_version is None:
        panic("Failed to fetch the latest integration version")

    def previous_versions(index: int):
        return last_build_version.body.replace("\n\n", "\n").splitlines()[index].split(": ")[1]

    print(previous_version(0))
    print(previous_version(1))
    print(previous_version(2))
    print(previous_version(3))
    return

    # Begin stuff
    if count_releases == 0:
        print("First time building Piko Twitter!")
    elif previous_versions(2) != latest_version.version:
        print(f"New twitter version found: {latest_version.version}")
    elif previous_versions(0) != last_patch_version.tag_name:
        print(f"New patch version found: {last_patch_version.tag_name}")
    elif previous_versions(1) != last_integration_version.tag_name:
        print(f"New integration version found: {last_integration_version.tag_name}")
    else:
        print("No new version found")
        return

    # get bundle and universal variant
    variants: list[Variant] = apkmirror.get_variants(latest_version)

    download_link: Variant | None = None
    for variant in variants:
        if variant.is_bundle and variant.arcithecture == "universal":
            download_link = variant
            break

    if download_link is None:
        raise Exception("Bundle not Found")

    apkmirror.download_apk(download_link)
    if not os.path.exists("big_file.apkm"):
        panic("Failed to download apk")

    download_apkeditor()

    if not os.path.exists("big_file_merged.apk"):
        merge_apk("big_file.apkm")
    else:
        print("apkm is already merged")

    download_revanced_bins()

    build_apks(latest_version)

    def format_piko_changelogs(changelog: str) -> str:
        loglist: str = changelog.split("### ")[1:]
        append: str = ["### " + log for log in loglist]
        join: str = ''.join(append)
        
        return join

    release_notes: str = "**Patches**: " + last_patch_version.tag_name + "\n\n**Integrations**: " + last_integration_version.tag_name + "\n\n**Twitter**: " + latest_version.version + "\n\n## Patches\n" + format_piko_changelogs(last_patch_version.body) + "\n## Integrations\n" + format_piko_changelogs(last_integration_version.body)

    publish_release(
        release_notes,
        [
            f"twitter-piko-v{latest_version.version}.apk",
        ],
    )

    report_to_telegram()


if __name__ == "__main__":
    main()
