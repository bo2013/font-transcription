# font-transcription

Fonts with built-in transcription.

> [!NOTE]
> This is a small project, so AI was used to speed up development.
<!-- # Using make
## Requirement
- **Linux / MacOS / WSL**
- **GNU Make**
- **Python 3**
- **Source**: any child folder in fonts/
- **Mapping file**: mappings/&lt;language&gt;/&lt;language&gt;.json
## Build
```sh
make [target] -O=<font directory>
``` -->

# Installation
> [!WARNING]
> These fonts use the same font family names as the original fonts. Installing them may cause applications to use these fonts instead of the original system fonts.
## Linux / MacOS 
```sh
mkdir -p "$HOME/.local/share/fonts/font-transcription"
cp "fonts/<font>/dist/"*.ttf "$HOME/.local/share/fonts/font-transcription/"
fc-cache -f
```
# Windows
```cmd
mkdir "%LOCALAPPDATA%\Microsoft\Windows\Fonts"
copy "fonts\<font>\dist\*.ttf" "%LOCALAPPDATA%\Microsoft\Windows\Fonts\"
```
# Using make (experimental)
```sh
make install FONT_DIR=fonts/<font>
```

# Fonts

> [!WARNING]
> Japanese Kanji are currently not supported.
> 
> Korean, Simplified Chinese, Traditional Chinese, and Hong Kong Chinese are currently not supported.

| Font | Japanese | Korean | Simplified Chinese | Traditional Chinese | Hong Kong Chinese |
|---|:---:|:---:|:---:|:---:|:---:|
| [Noto Sans CJK](fonts/noto-sans-cjk/) | ✅ | ❌ | ❌ | ❌ | ❓ |
| [Noto Sans Mono CJK](fonts/noto-sans-mono-cjk/) | ✅ | ❌ | ❌ | ❌ | ❓ |

<!-- Emoji source: ✅ ❌ ⚠️ ❓ -->

## License

| License | Type | Applies to |
|---|---|---|
| [Root license](LICENSE) | MIT | All repository contents except `fonts/*` |
| [Noto Sans CJK](fonts/noto-sans-cjk/LICENSE) | SIL Open Font License 1.1 | `fonts/noto-sans-cjk/*` |
| [Noto Sans Mono CJK](fonts/noto-sans-mono-cjk/LICENSE) | SIL Open Font License 1.1 | `fonts/noto-sans-mono-cjk/*` |
