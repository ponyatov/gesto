all: 
	-python gesto.py > gesto.log
	sleep 2

TODAY = $(shell date +%d%m%y)

MERGE  = Makefile .gitignore README.md
MERGE += gesto.py gesto.gst

merge:
	git checkout master
	git checkout ponyatov -- $(MERGE)

release:
	git tag $(TODAY)
	git push -v
	git checkout ponyatov
