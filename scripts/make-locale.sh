#! /bin/bash

__DIR__=$(dirname $(readlink -f $0))
po_dir=$__DIR__/../po
locale_dir=$__DIR__/../usr/share/locale
domain="uxdgmenu"

rm -rf $locale_dir/* 2> /dev/null

echo "=============================="
echo "Building localized messages..."

#find "$po_dir" -name *.po | while read po_file
for po_file in $po_dir/*.po
do
  language=$(basename $po_file '.po')
  language_dir="$locale_dir/$language/LC_MESSAGES"
  mkdir -p "$language_dir"
  msgfmt -o "$language_dir/$domain.mo" "$po_file"
done

exit 0
