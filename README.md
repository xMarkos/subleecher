# SubLeecher
SubLeecher is a simple command line tool for downloading subtitles for TV shows and movies from OpenSubtitles.com.

## Why SubLeecher
There is plenty of software that is much more sophisticated and/or supports more sources than OpenSubtitles, so why did I bother to code this app?

1. I can download subtitles on demand with just my remote controller.
   - This is the most important point for me!
3. I can select alternative subtitles easily.
   - When the first match is not suitable, e.g. when out of sync.
4. I can fallback to another language.
   - When subtitles in my language are not available.
5. I can filter out machine and AI translated subtitles.
   - Because they simply suck!
7. It's so simple that it does not require any special configuration, or a windows service running all the time.
   - Other similar software is trying to be so smart, that I am no longer in control. And I want to be in control!

# Usage
The tool is built as a single exe app, so it does not need anthing else (the required dependencies are bundled in it).

## Installation (if that's what we can call it)
1. Put the exe file anywhere you like.
2. Create `%appdata%\SubLeecher\config.yaml` configuration file with your credentials.
3. Add a shortcut to the "Send To" context menu:
   - Press `Ctrl + R` and type `shell:SendTo`
   - Add a shortcut to SubLeecher.exe
   - Optionally add a command line switch `--pause` (that will cause the window to stay open)
  
## And to use it
1. Select video (or multiple videos) for which you want to download subtitles.
2. Right click and navigate to `Send to` menu.
3. Select `SubLeecher`.
4. A console will pop-up with suitable subtitle matches.
5. Write a letter of the subtitle you want to download and confirm with enter.
   - Multiple subtitles can be selected by writing multiple letters like `qwe`.
   - To skip current file (e.g. when you don't like any of the matches), write `-`.
  
The tool can be used from a command-line too. It allows globbing and brace expansion (similarly to how it would work on linux and bash), and you can process whole folders recursively.

## Configuration file
A configuration file with credentials is required in `%appdata%\SubLeecher\config.yaml` on Windows or `~/.config/SubLeecher/config.yaml` on linux.

```yaml
username: your username
password: your password
languages: array of languages
app_name: app registration name
api_key: app registration api key
```

As you can see, the app requires 2 forms of authentication:
1. Username and password of your account on OpenSubtitles.com.
2. An API key for the app.
   - I am not yet ready to share this key, however, it should be very easy to obtain one yourself.

Field `languages` determines which languages of subtitles are matched and in which order, e.g. `[cs,en,sk]` will match Czech, English, and Slovak subtitles, and the UI will present them in that order.
