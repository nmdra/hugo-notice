# hugo-notice

This [Hugo](https://gohugo.io) theme component is a fork of [martignoni/hugo-notice](https://github.com/martignoni/hugo-notice) (GPLv3). It provides a `notice` shortcode that displays **Obsidian-style callouts**. The component has native support for light and dark modes. It uses [Catppuccin](https://github.com/catppuccin/palette) colors (Latte/Mocha) that match the PaperMod theme.

## Features

- 13 callout types from [Obsidian](https://obsidian.md/help/callouts): `note`, `abstract`, `info`, `todo`, `tip`, `success`, `question`, `warning`, `failure`, `danger`, `bug`, `example`, `quote`
- Obsidian aliases: `summary`/`tldr`, `hint`/`important`, `check`/`done`, `help`/`faq`, `caution`/`attention`, `fail`/`missing`, `error`, `cite`
- Foldable callouts: `{{< notice "tip+" >}}` (expanded) / `{{< notice "tip-" >}}` (collapsed)
- Custom titles: `{{< notice tip "A New Title" >}}`
- Dark mode follows PaperMod's theme toggle through `:root[data-theme="dark"]`.
- Inline Lucide-style stroke icons require no icon files.
- Localization in 18 languages: English and 17 community translations. In non-English locales, the 9 new type titles use English as a fallback.

## Installation

### As a Hugo module

1. Initialize your existing site as a Hugo module.

    ```shell
    hugo mod init github.com/USERNAME/REPO
    ```

2. Add `hugo-notice` as a Hugo module.

    ```shell
    hugo mod get github.com/nmdra/hugo-notice
    ```

3. In your site's or theme's configuration file `hugo.yaml` or `hugo.toml`, add a new `module` section. In this section, define `hugo-notice` and your current theme as modules to import.

    Example with `hugo.yaml`:
    ```yaml
    module:
      imports:
        - path: github.com/nmdra/hugo-notice
        - path: my-theme
    ```
    Or with `hugo.toml`:
    ```toml
    [module]
      [[module.imports]]
        path = "github.com/nmdra/hugo-notice"
      [[module.imports]]
        path = "my-theme"
    ```

### As a Git submodule

1. Add `hugo-notice` as a submodule so that you can get upstream changes later: `git submodule add https://github.com/nmdra/hugo-notice.git themes/hugo-notice`

2. In your site's or theme's configuration file `hugo.yaml` or `hugo.toml`, add `hugo-notice` as the first element of the `theme` list variable.

   Example with `hugo.yaml`:
    ```yaml
    theme: ["hugo-notice", "my-theme"]
    ```
    Or with `hugo.toml`:
    ```toml
    theme = ["hugo-notice", "my-theme"]
    ```

## Usage

Use the shortcode in your site as shown in these examples:

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

To change the callout title, supply a string as the second argument:

```markdown
{{< notice tip "A New Title" >}}
This is a very good tip with a different title.
{{< /notice >}}
```

Unlike built-in titles, custom titles cannot be translated by hugo-notice. If you need a translated custom title, translate the title before you supply it to the shortcode.

### Aliases

The component supports all Obsidian aliases. For example, `{{< notice summary >}}` and `{{< notice tldr >}}` display as `abstract`. The shortcode `{{< notice error >}}` displays as `danger`.

### Foldable callouts

Append `+` (expanded by default) or `-` (collapsed) to the type. Note that the type argument must be quoted for Hugo to parse it:

```markdown
{{< notice "question-" >}}
The answer is hidden until the reader expands the callout.
{{< /notice >}}
```

```markdown
{{< notice "todo+" "Release checklist" >}}
- [ ] Update CHANGELOG
- [ ] Run regression tests
{{< /notice >}}
```

### Nested callouts

Put each nested shortcode on its own line. You do not need to enable raw HTML in Goldmark:

```markdown
{{< notice "note+" "Outer callout" >}}
Outer content.

{{< notice "tip-" "Inner callout" >}}
Inner content.
{{< /notice >}}
{{< /notice >}}
```

Foldable content opens and closes immediately through the browser's native `<details>` behavior. The fold indicator has a short transition, which is disabled when the reader requests reduced motion.

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

For unknown types, the component uses `note`, as Obsidian does.

The component uses `color-mix` to derive the callout background and border from the accent color. Title text uses a separate color for contrast. The background and border adapt automatically to light and dark themes. This requires a browser from 2023 onward (Chrome 111+, Firefox 113+, Safari 16.2+).

### Dark mode

The component targets `:root[data-theme="dark"]`, the standard that PaperMod's theme toggle uses. No additional configuration is necessary for PaperMod. Other themes must set `data-theme="dark"` on the root element or supply CSS overrides. The component does not detect `body.dark` or `prefers-color-scheme` automatically.

## Theming

### Add custom CSS

Add the following examples to a stylesheet that your site loads. Use your theme's method for loading custom CSS. You do not need to edit `layouts/shortcodes/notice.html`.

The shortcode inserts a stylesheet link before the first outermost callout on each page. Hugo publishes the CSS from `assets/css/hugo-notice.css` with a fingerprinted filename. The examples use selectors with higher specificity than the component's selectors, so they do not depend on stylesheet order.

### Change accent colors

Set `--notice-accent` on the callout type that you want to change. This property controls the icon, fold indicator, left border, background, and other borders. The background mixes 9% of the accent color with transparency. The other borders mix 20% of the accent color with transparency.

This example changes the `tip` accent in light and dark modes:

```css
html:root .notice.tip {
    --notice-accent: #006b54;
}

html:root[data-theme="dark"] .notice.tip {
    --notice-accent: #70e0c0;
}
```

Replace `.tip` with a type from [Types and colors](#types-and-colors). Use the type name, not an alias. For example, `hint` and `important` use the `.tip` class.

Define both rules to use a custom accent in both modes. A light-mode override alone does not replace the component's more specific dark-mode rule.

### Change spacing and borders

Use `.notice` to change all callout containers:

```css
html:root .notice {
    margin: 1rem 0;
    padding: 0.75rem 1rem;
    border-left-width: 3px;
    border-radius: 6px;
}
```

By default, the border radius uses `--radius`, with `8px` as the fallback. Set `border-radius` directly, as shown above, to change only callouts without changing the theme's shared `--radius` property.

To change the background or border color independently of the accent, override `background` or `border-color` on the same selector.

### Change titles and icons

Set `--notice-title-color` on a callout to change its title text color. The default is `#343a40` in light mode and `#cdd6f4` in dark mode. Check text contrast against the callout background after you change either color.

```css
html:root .notice.tip {
    --notice-title-color: #254b3f;
}

html:root[data-theme="dark"] .notice.tip {
    --notice-title-color: #d5f5e8;
}
```

Use the following selectors to change title spacing and icon size:

```css
html:root .notice-title {
    gap: 0.75rem;
    font-weight: 600;
}

html:root .notice-icon svg {
    width: 1.25em;
    height: 1.25em;
}
```

The icons use `currentColor` for their strokes. The icon and fold indicator use `--notice-accent`, independently of the title text color.

### Use another dark-mode selector

If your theme sets `body.dark`, set the dark title color for all callouts. Add an accent override for each type that you want to change:

```css
html:root body.dark .notice {
    --notice-title-color: #cdd6f4;
}

html:root body.dark .notice.tip {
    --notice-accent: #70e0c0;
}
```

If your theme uses only the system color preference, put the override in a media query:

```css
@media (prefers-color-scheme: dark) {
    html:root:not([data-theme]) .notice {
        --notice-title-color: #cdd6f4;
    }

    html:root:not([data-theme]) .notice.tip {
        --notice-accent: #70e0c0;
    }
}
```

The media-query example applies only when the root element has no `data-theme` attribute. It does not override an explicit light or dark selection through that attribute. Repeat the rule for other callout types as necessary.

## Development

### Tests

Install Hugo and Python 3. From the component directory, run:

```shell
python3 -m unittest discover -s tests -v
```

The tests build temporary Hugo sites. They do not change your site's content or configuration.

### Localization

Thanks to the original hugo-notice contributors for the 17 non-English translations.

### Acknowledgement

This component is a fork of [hugo-notice](https://github.com/martignoni/hugo-notice) by Nicolas Martignoni. The license is GPLv3. Lucide icons use the MIT license.
