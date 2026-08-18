O ?= .

MAPPING := mappings/japanese/japanese.json
PYTHON := /usr/bin/python

FONT_DIR := fonts/noto-sans-cjk

SOURCES := $(wildcard $(FONT_DIR)/*.ttf)
TARGETS := $(patsubst \
	$(FONT_DIR)/%.ttf, \
	$(O)/%-jpwithromaji.ttf, \
	$(SOURCES))

.PHONY: all

all: $(TARGETS)

$(O)/%-jpwithromaji.ttf: $(FONT_DIR)/%.ttf $(MAPPING)
	mkdir -p $(dir $@)
	$(PYTHON) build.py $< $@ $(MAPPING)