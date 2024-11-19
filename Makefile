.PHONY: install

PYVER=3.10
SYSPY=python$(PYVER)

VENV=$(shell pwd)/venv
VENVBIN=$(VENV)/bin
VENVPY=$(VENVBIN)/python
VENVPIP=$(VENVBIN)/pip

install: $(VENV) bin/z3
	$(VENVPY) setup.py develop

$(VENV):
	$(SYSPY) -m venv $(VENV)
	$(VENVPIP) install --upgrade setuptools

# build submodules
bin/z3: submodules/z3/README.md
	$(SYSPY) build_submodules.py

# clone submodules
submodules/z3/README.md:
	git submodule update --recursive -f
