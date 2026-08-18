O ?= .

MAPPING := mappings/japanese/japanese.json
PYTHON := /usr/bin/python

FONT_DIR := fonts/noto-sans-cjk

SOURCES := $(wildcard $(FONT_DIR)/*.ttf)
TARGETS := $(patsubst \
	$(FONT_DIR)/%.ttf, \
	$(FONT_DIR)/dist/%.ttf, \
	$(SOURCES))

.PHONY: all install

all: $(TARGETS)

$(FONT_DIR)/dist/%.ttf: $(FONT_DIR)/%.ttf $(MAPPING)
	mkdir -p $(dir $@)
	$(PYTHON) build.py $< $@ $(MAPPING)

install:
	mkdir -p $(HOME)/.local/share/fonts/jpwithromaji/
	cp $(FONT_DIR)/dist/*.ttf $(HOME)/.local/share/fonts/jpwithromaji/
	fc-cache -f
	@echo
	@echo "Added $(words $(wildcard $(FONT_DIR)/dist/*.ttf)) font(s)"