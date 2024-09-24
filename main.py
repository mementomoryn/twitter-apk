from apkmirror import Version, Variant
from build_variants import build_apks
from download_bins import download_apkeditor, download_revanced_bins
import github
from utils import panic, merge_apk, publish_release, report_to_telegram, previous_version, format_changelog
import apkmirror
import os
import argparse


def get_latest_release(versions: list[Version], prerelease: bool) -> Version | None:
    if prerelease is True:
        return versions[0]
    else:
        for i in versions:
            if i.version.lower().find("beta") == -1 and i.version.lower().find("alpha") == -1:
                return i


def main():
    # get latest version
    url: str = "https://www.apkmirror.com/apk/x-corp/twitter/"
    repo_url: str = os.environ["CURRENT_REPOSITORY"]
    patch_url: str = "crimera/piko"
    integration_url: str = "crimera/revanced-integrations"
    cli_url: str = "inotia00/revanced-cli"
    xposed_url: str = "Xposed-Modules-Repo/com.twifucker.hachidori"

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", nargs="?", action="store", dest="version", const=None, default=None)
    parser.add_argument("-p", "--prerelease", nargs="*", action="store", dest="prerelease", choices=["true", "false"], default=["false", "false", "false", "false", "false"])
    args = parser.parse_args()

    if len(args.prerelease) != 5:
        panic("Prerelease argument list is not correct")
    else:
        prerelease_build: bool = "true" in args.prerelease
        prerelease_cli: bool = args.prerelease[0] == "true"
        prerelease_patch: bool = args.prerelease[1] == "true"
        prerelease_int: bool = args.prerelease[2] == "true"
        prerelease_xp: bool = args.prerelease[3] == "true"
        prerelease_apk: bool = args.prerelease[4] == "true"

    if args.version is None:
        versions = apkmirror.get_versions(url)
        latest_version = get_latest_release(versions, prerelease_apk)
    else:
        latest_version = apkmirror.get_manual_version(url, args.version)
    
    if latest_version is None:
        raise Exception("Could not find the latest version")

    if latest_version.version.lower().find("beta") != -1 or latest_version.version.lower().find("alpha") != -1 and prerelease_apk is False:
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
        patch_url,
        prerelease_patch
    )

    if last_patch_version is None:
        panic("Failed to fetch the latest patch version")
        return

    last_integration_version: github.GithubRelease | None = github.get_last_build_version(
        integration_url,
        prerelease_int
    )

    if last_integration_version is None:
        panic("Failed to fetch the latest integration version")

    last_xposed_version: github.GithubRelease | None = github.get_last_build_version(
        xposed_url,
        prerelease_xp
    )

    if last_xposed_version is None:
        panic("Failed to fetch the latest xposed version")

    # checking for updates
    if count_releases == 0:
        print("First time building Piko Twitter!")
    elif args.version != None:
        print("Manual app version building!")
    elif prerelease_build is True:
        print("Pre-releases version building!") 
    elif previous_version(0, last_build_version) != last_patch_version.tag_name:
        print(f"New patch version found: {last_patch_version.tag_name}")
    elif previous_version(1, last_build_version) != last_integration_version.tag_name:
        print(f"New integration version found: {last_integration_version.tag_name}")
    elif previous_version(2, last_build_version) != last_xposed_version.tag_name:
        print(f"New xposed version found: {last_xposed_version}")
    elif previous_version(3, last_build_version) != latest_version.version:
        print(f"New twitter version found: {latest_version.version}")
    else:
        print("No new version found")
        return

    # get bundle and universal variant
    variants: list[Variant] = apkmirror.get_variants(latest_version)

    download_link: Variant | None = None
    for variant in variants:
        if variant.is_bundle and variant.arcithecture == "universal" or variant.arcithecture == "arm64-v8a":
            download_link = variant
            break

    if download_link is None:
        raise Exception("Bundle not Found")

    apkmirror.download_apk(download_link)
    if not os.path.exists("big_file.apkm"):
        panic("Failed to download apk")

    download_apkeditor()

    download_lspatch()

    if not os.path.exists("big_file_merged.apk"):
        merge_apk("big_file.apkm")
    else:
        print("apkm is already merged")

    download_revanced_bins(cli_url, "cli", prerelease_cli)

    download_revanced_bins(patch_url, "patch", prerelease_patch)

    download_revanced_bins(integration_url, "integration", prerelease_int)

    download_xposed_bins(xposed_url, "Hachidori", prerelease_xp)

    build_apks(latest_version)

    release_notes: str = "**Patches**: " + last_patch_version.tag_name + "\n\n**Integrations**: " + last_integration_version.tag_name + "\n\n**Xposed**: " + last_xposed_version.tag_name + "\n\n**Twitter**: " + latest_version.version + "\n\n## Patches\n" + format_changelog(last_patch_version.body) + "\n## Integrations\n" + format_changelog(last_integration_version.body) + "\n## Xposed\n" + format_changelog(last_xposed_version.body)

    publish_release(
        release_notes,
        prerelease_build,
        [
            f"twitter-piko-v{latest_version.version}.apk",
f"twitter-hachidori-v{latest_version.version}.apk",
        ]
    )

    report_to_telegram(patch_url, integration_url, xposed_url)


if __name__ == "__main__":
    main()
