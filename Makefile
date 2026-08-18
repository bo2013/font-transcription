O ?= .

MAPPING := mappings/japanese/japanese.json
PYTHON := /usr/bin/python

TARGETS := NotoSansCJK-JP-Regular-jpwithromaji.ttf NotoSansMonoCJK-JP-Regular-jpwithromaji.ttf

.PHONY: all

all: $(addprefix $(O)/,$(TARGETS))



$(O)/%-jpwithromaji.ttf: %.ttf $(MAPPING)
	mkdir -p $(O)
	$(PYTHON) build.py $< $@ $(MAPPING)