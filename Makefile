O ?= .

MAPPING := mappings/japanese/japanese.json
PYTHON ?= python

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
	$(PYTHON) -m builder $< $@ $(MAPPING)

install:
	mkdir -p $(HOME)/.local/share/fonts/font-transcription/
	cp $(FONT_DIR)/dist/*.ttf $(HOME)/.local/share/fonts/font-transcription/
	fc-cache -f
	@echo
	@echo "Added $(words $(wildcard $(FONT_DIR)/dist/*.ttf)) font(s)"