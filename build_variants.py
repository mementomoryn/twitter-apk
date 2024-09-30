from apkmirror import Version
from utils import move_merged_apk, patch_revanced_apk, patch_xposed_apk


def build_apks(latest_version: Version):
    # patch
    apk = "big_file_merged.apk"
    integrations = "bins/integrations.apk"
    patches = "bins/patches.jar"
    cli = "bins/cli.jar"
    xposed = "bins/xposed.apk"
    lspatch = "bins/lspatch.jar"
    files = []

    patch_revanced_apk(
        files,
        cli,
        integrations,
        patches,
        apk,
        includes=["Bring back twitter"],
        excludes=[],
        riparch=["armeabi-v7a", "x86", "x86_64"],
        out=f"twitter-piko-v{latest_version.version}.apk"
    )

    patch_xposed_apk(
        files,
        lspatch,
        xposed,
        apk,
        out_dir="twitter-hachidori",
        out=f"twitter-hachidori-v{latest_version.version}.apk"
    )

    move_merged_apk(
        files,
        apk,
        out=f"twitter-merged-v{latest_version.version}.apk"
    )
    
    return files
