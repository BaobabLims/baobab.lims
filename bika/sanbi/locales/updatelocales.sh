#!/bin/bash
# zinstance/src/bika.sanbi/bika/sanbi/locales
ZINSTANCE=$PWD'/../../../../..'
I18NDUDE=$ZINSTANCE/bin/i18ndude
BIKA_POT=$ZINSTANCE/src/bika.lims/bika/lims/locales/bika.pot
BIKA_PLONE_POT=$ZINSTANCE/src/bika.lims/bika/lims/locales/plone.pot

# Flush the english po files
# If we don't do this, new *-manual translations won't be synced.
> en/LC_MESSAGES/plone.po
> en/LC_MESSAGES/bika.po
> en/LC_MESSAGES/bika.sanbi.po

# Remove generated files

find . -name "*.mo" -delete
rm plone.pot 2>/dev/null
rm bika.pot 2>/dev/null
rm bika.sanbi.pot 2>/dev/null

### plone domain (overrides)
DOMAIN=plone
$I18NDUDE trmerge $BIKA_PLONE_POT $DOMAIN-manual.pot > $DOMAIN-tmp.pot
mv $DOMAIN-tmp.pot $DOMAIN.pot
$I18NDUDE sync --pot $DOMAIN.pot */LC_MESSAGES/$DOMAIN.po

### bika domain (overrides)
DOMAIN=bika
$I18NDUDE trmerge $BIKA_POT $DOMAIN-manual.pot > $DOMAIN-tmp.pot
mv $DOMAIN-tmp.pot $DOMAIN.pot
$I18NDUDE sync --pot $DOMAIN.pot */LC_MESSAGES/$DOMAIN.po

### bika.sanbi domain
DOMAIN=bika.sanbi
$I18NDUDE rebuild-pot --pot $DOMAIN-tmp.pot --exclude "build" --create $DOMAIN ..
# smash bika-manual into bika.sanbi output,
# to prevent some kind of weird overlap, we overlap the whole lot.
$I18NDUDE trmerge $DOMAIN-tmp.pot bika-manual.pot > $DOMAIN-tmp2.pot
$I18NDUDE trmerge $DOMAIN-tmp2.pot $DOMAIN-manual.pot > $DOMAIN.pot
rm $DOMAIN-tmp.pot $DOMAIN-tmp2.pot
$I18NDUDE sync --pot bika.sanbi.pot */LC_MESSAGES/bika.sanbi.po

for po in `find . -name "*.po"`; do msgfmt -o ${po/%po/mo} $po; done
