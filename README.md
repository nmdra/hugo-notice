# hugo-notice

Fork of [martignoni/hugo-notice](https://github.com/martignoni/hugo-notice) (GPLv3) — a [Hugo](https://gohugo.io) theme component providing a `notice` shortcode that renders **Obsidian-style callouts**, with native light/dark mode support and [Catppuccin](https://github.com/catppuccin/palette) colors (Latte/Mocha) that fit the PaperMod theme.

## Features

- 13 callout types from [Obsidian](https://obsidian.md/help/callouts): `note`, `abstract`, `info`, `todo`, `tip`, `success`, `question`, `warning`, `failure`, `danger`, `bug`, `example`, `quote`
- Obsidian aliases: `summary`/`tldr`, `hint`/`important`, `check`/`done`, `help`/`faq`, `caution`/`attention`, `fail`/`missing`, `error`, `cite`
- Foldable callouts: `{{< notice tip+ >}}` (expanded) / `{{< notice tip- >}}` (collapsed)
- Custom titles: `{{< notice tip "A New Title" >}}`
- Dark mode follows the theme toggle — works with PaperMod's `:root[data-theme="dark"]` (also `prefers-color-scheme` and `body.dark` setups)
- Inline Lucide-style stroke icons, no icon files needed
- Localization in 18 languages (English and 17 community translations; the 9 new type titles fall back to English in non-English locales)

## Installation

### As a Hugo module

1. Initialize your existing site as hugo module

    ```shell
    hugo mod init github.com/USERNAME/REPO
    ```

2. Add `hugo-notice` as a hugo module

    ```shell
    hugo mod get github.com/nmdra/hugo-notice
    ```

3. In your site's or theme's configuration file `hugo.yaml` or `hugo.toml`, add a new `module` section and define both `hugo-notice` and your currently used theme as modules to be imported.

    Example, with `hugo.yaml`:
    ```yaml
    module:
      imports:
        - path: github.com/nmdra/hugo-notice
        - path: my-theme
    ```
    or, with `hugo.toml`,
    ```toml
    [module]
      [[module.imports]]
        path = "github.com/nmdra/hugo-notice"
      [[module.imports]]
        path = "my-theme"
    ```

### As a Git submodule

1. Add `hugo-notice` as a submodule to be able to get upstream changes later `git submodule add https://github.com/nmdra/hugo-notice.git themes/hugo-notice`

2. Add `hugo-notice` as the left-most element of the `theme` list variable in your site's or theme's configuration file `hugo.yaml` or `hugo.toml`.

   Example, with `hugo.yaml`:
    ```yaml
    theme: ["hugo-notice", "my-theme"]
    ```
    or, with `hugo.toml`,
    ```toml
    theme = ["hugo-notice", "my-theme"]
    ```

## Usage

In your site, use the shortcode, this way:

```markdown
{{< notice warning >}}
This is a warning notice. Be warned!
{{< /notice >}}
```

```markdown
{{< notice tip >}}
This is a very good tip.
{{< /notice >}}
```

### Custom title

You may change the title of the notice by providing a string as a second argument:

```markdown
{{< notice tip "A New Title" >}}
This is a very good tip with a different title.
{{< /notice >}}
```

Note that unlike the built-in ones, these titles are not translatable by hugo-notice. If you need translation, you will need to translate them before passing them in.

### Aliases

All Obsidian aliases are supported. For example, `{{< notice summary >}}` and `{{< notice tldr >}}` render as `abstract`, and `{{< notice error >}}` renders as `danger`.

### Foldable callouts

Append `+` (expanded by default) or `-` (collapsed) to the type:

```markdown
{{< notice question- >}}
The answer is hidden until the reader expands the callout.
{{< /notice >}}
```

```markdown
{{< notice todo+ "Release checklist" >}}
- [ ] Update CHANGELOG
- [ ] Run regression tests
{{< /notice >}}
```

### Types and colors

| Type | Aliases | Icon | Light accent | Dark accent |
|---|---|---|---|---|
| `note` | — | pencil | blue `#1e66f5` | `#89b4fa` |
| `abstract` | `summary`, `tldr` | clipboard | teal `#179299` | `#94e2d5` |
| `info` | — | info | sky `#04a5e5` | `#89dceb` |
| `todo` | — | checkbox | lavender `#7287fd` | `#b4befe` |
| `tip` | `hint`, `important` | flame | green `#40a02b` | `#a6e3a1` |
| `success` | `check`, `done` | check | green `#40a02b` | `#a6e3a1` |
| `question` | `help`, `faq` | question mark | yellow `#df8e1d` | `#f9e2af` |
| `warning` | `caution`, `attention` | triangle | peach `#fe640b` | `#fab387` |
| `failure` | `fail`, `missing` | cross | red `#d20f39` | `#f38ba8` |
| `danger` | `error` | zap | red `#d20f39` | `#f38ba8` |
| `bug` | — | bug | maroon `#e64553` | `#eba0ac` |
| `example` | — | list | mauve `#8839ef` | `#cba6f7` |
| `quote` | `cite` | quote | gray `#6c6f85` | `#a6adc8` |

Unknown types fall back to `note` (Obsidian behavior).

The callout background and border are derived from the accent with `color-mix`, so they adapt automatically to light and dark themes. Requires a browser from 2023 onward (Chrome 111+, Firefox 113+, Safari 16.2+).

### Dark mode

The component targets `:root[data-theme="dark"]`, the standard used by PaperMod's theme toggle. It works out of the box with PaperMod, and also follows the standard `prefers-color-scheme` media feature when no `data-theme` attribute is present (e.g. with other themes).

## Development

### Localization

Thanks to the original hugo-notice contributors for the 17 non-English translations.

### Acknowledgement

This component is a fork of [hugo-notice](https://github.com/martignoni/hugo-notice) by Nicolas Martignoni, licensed under GPLv3. Lucide icons are MIT-licensed.
