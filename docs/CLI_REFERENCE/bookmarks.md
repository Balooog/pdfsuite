# bookmarks

Manage PDF outline/bookmarks using `pdftk` dump/apply helpers.

## Commands

### `pdfsuite bookmarks dump`

Export bookmarks (table of contents) from a PDF into a UTF-8 text file that can be edited or versioned.

```
pdfsuite bookmarks dump input.pdf -o bookmarks.txt
```

- Requires `pdftk` on PATH.
- Output format matches `pdftk dump_data_utf8`, so it can be round-tripped via the `apply` command.

Exit codes: returns the upstream `pdftk` exit status (0 on success).

### `pdfsuite bookmarks apply`

Apply a bookmark dump file back onto a PDF.

```
pdfsuite bookmarks apply input.pdf bookmarks.txt -o bookmarked.pdf
```

- Uses `pdftk update_info_utf8`.
- Works with files exported by `dump` or edited manually (keep the `BookmarkPageNumber` and `BookmarkLevel` structure intact).

Exit codes: propagates the `pdftk` exit status.

## Tips

- Keep bookmark dumps in version control for complex manuals; you can edit titles with any UTF-8 aware editor.
- Combine with the GUI Bookmarks panel to preview edits before writing them back to the PDF.
