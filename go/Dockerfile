FROM golang:1.10 as build

WORKDIR $GOPATH/src/github.com/daneroo/im-ted1k/go
COPY . .

RUN go version && go get -u -v golang.org/x/vgo

# to avoid GitHUb API rate limiting
RUN cp dot.netrc $HOME/.netrc

# vgo is hard-coded to use clang: https://github.com/golang/go/issues/23965
RUN CC=gcc vgo install ./...

# Base images: scratch 2.2MB alpine:6.3MB distroless:18MB
FROM gcr.io/distroless/base
COPY --from=build /go/bin/capture /
CMD ["/capture"]