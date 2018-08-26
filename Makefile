# project
PROJECT = $(shell pwd)
BINARY  = $(PROJECT)/sipd
LOGS    = $(PROJECT)/logs
SOURCE  = $(PROJECT)/src

# python
PYTHON = $(shell which python3)

all:
	cd $(SOURCE) &&\
	   zip -rv $(BINARY).zip * &&\
	   echo "#!$(PYTHON)" > $(BINARY) &&\
	   cat $(BINARY).zip >> $(BINARY)
	rm -fv $(BINARY).zip
	chmod u+x -v $(BINARY)


test:
	tox


run:
	python $(SOURCE) || true


clean:
	find $(SOURCE) -type f -iname "*.py[oc]" -exec rm -fv "{}" \; || true
	find $(SOURCE) -type d -name "__pycache__" -exec rm -rfdv "{}" \; || true
	rm -rfv $(BINARY) $(LOGS)
