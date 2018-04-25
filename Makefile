# project
PROJECT = $(shell pwd)

SOURCE  = $(PROJECT)/src
BINARY  = $(PROJECT)/sipd
LOGS    = $(PROJECT)/logs

all:
	cd $(SOURCE) &&\
	   zip -rv $(BINARY).zip * &&\
	   echo "#!/usr/bin/python" > $(BINARY) &&\
	   cat $(BINARY).zip >> $(BINARY)
	rm -fv $(BINARY).zip
	chmod u+x -v $(BINARY)

run:
	python $(SOURCE)

test:
	python $(SOURCE) --test

clean:
	rm -rfv $(LOGS)
	rm -fv $(BINARY)
	find $(SOURCE) \
	     -type f \
	     -iname "*.py[oc]" \
	     -exec rm -fv "{}" \;
	find $(SOURCE) \
	     -type d \
	     -name "__pycache__" \
	     -exec rm -rfdv "{}" \; ||\
	     true
