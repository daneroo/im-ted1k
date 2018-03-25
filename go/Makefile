# The import path is where your repository can be found.
# To import subpackages, always prepend the full import path.
# If you change this, run `make clean`. Read more: https://git.io/vM7zV
IMPORT_PATH := github.com/daneroo/im-ted1k/go

.PHONY: all
all: capture

.PHONY: vscode
vscode: 
	echo set "go.gopath": "/Users/daniellauzon/Code/iMetrical/im-ted1k/go/.GOPATH"

.PHONY: capture
capture: .GOPATH/.ok
	@echo Using GOPATH=$(GOPATH)
	vgo install -v $(VERSION_FLAGS) $(IMPORT_PATH)/cmd/capture

##### ^^^^^^ EDIT ABOVE ^^^^^^ #####

##### =====> Utility targets <===== #####

.PHONY: clean test list cover format

clean:
	rm -rf bin .GOPATH

##### =====> Internals <===== #####

.PHONY: setup
setup: clean .GOPATH/.ok
	@echo Using GOPATH=$(GOPATH)
	@echo for vscode, set this in your workspace settings:
	@echo "go.gopath": "/Users/daniellauzon/Code/iMetrical/im-ted1k/go/.GOPATH"
	@echo and run "vgo vendor"
	
	@if ! grep "/.GOPATH" .gitignore > /dev/null 2>&1; then \
	    echo "/.GOPATH" >> .gitignore; \
	    echo "/bin" >> .gitignore; \
	fi

VERSION          := $(shell git describe --tags --always --dirty="-dev")
DATE             := $(shell date -u '+%Y-%m-%dT%H:%M:%SZ')
VERSION_FLAGS    := -ldflags='-X "main.Version=$(VERSION)" -X "main.BuildTime=$(DATE)"'


export GOPATH := $(CURDIR)/.GOPATH
unexport GOBIN


.GOPATH/.ok:
	@mkdir -p "$(dir .GOPATH/src/$(IMPORT_PATH))"
	@ln -s ../../../../.. ".GOPATH/src/$(IMPORT_PATH)"
	@mkdir -p bin
	@ln -s ../bin .GOPATH/bin
	@touch $@

# Based on https://github.com/cloudflare/hellogopher - v1.1 - MIT License
#
# Copyright (c) 2017 Cloudflare
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
