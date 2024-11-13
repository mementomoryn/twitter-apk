"""
any REPOSITORY string must contain "owner/repo"
any VERSION string can be empty to pick latest, lspatch doesn't support picking specific version for now
ENABLED_BINS list can contain any combination of these string: "revanced", "lspatch", "xposed", or "apkeditor"
"""

APKMIRROR_URL: str = "https://www.apkmirror.com/apk/x-corp/twitter/"

REVANCED_PATCH_REPOSITORY: str = "crimera/piko"

REVANCED_PATCH_VERSION: str = ""

REVANCED_INTEGRATION_REPOSITORY: str = "crimera/revanced-integrations"

REVANCED_INTEGRATION_VERSION: str = ""

REVANCED_CLI_REPOSITORY: str = "inotia00/revanced-cli"

REVANCED_CLI_VERSION: str = ""

XPOSED_MODULE_REPOSITORY: str = "Xposed-Modules-Repo/com.twifucker.hachidori"

XPOSED_MODULE_VERSION: str = ""

LSPATCH_REPOSITORY: str = "JingMatrix/LSPatch"

APKEDITOR_REPOSITORY: str = "REAndroid/APKEditor"

ENABLED_BINS: list = ["revanced", "xposed", "apkeditor"]